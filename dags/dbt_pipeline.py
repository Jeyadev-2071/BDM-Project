from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id='dbt_pipeline',
    default_args=default_args,
    description='Run dbt pipeline with Airflow',
    schedule_interval='@daily',  # Adjust as per your schedule
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Set the JSON content in an environment variable
    service_account_key = """
    {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR-PRIVATE-KEY\\n-----END PRIVATE KEY-----\\n",
        "client_email": "your-service-account-email",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email"
    }
    """

    # Task 1: Write the JSON content to a temporary file
    write_service_account_key = BashOperator(
        task_id='write_service_account_key',
        bash_command="""
        mkdir -p temp &&
        echo '{{ service_account_key }}' > temp/google_key.json
        """,
        env={'service_account_key': service_account_key}
    )
    fetch_profiles = BashOperator(
    task_id='fetch_profiles',
    bash_command="""
    set -e  # Exit on error
    echo "Creating directory for profiles.yml..."
    mkdir -p /home/airflow/gcs/data/.dbt
    echo "Copying profiles.yml from GCS to /home/airflow/gcs/data/.dbt/..."
    gsutil cp gs://bdm-project-bucket/.dbt/profiles.yml /home/airflow/gcs/data/.dbt/profiles.yml
    if [ $? -ne 0 ]; then
        echo "Error: Failed to copy profiles.yml from GCS"
        exit 1
    fi
    echo "profiles.yml successfully copied"
    """,
    env={
        'GOOGLE_APPLICATION_CREDENTIALS': 'temp/google_key.json'
        }
    )   

    # Task 2: Run dbt commands (e.g., dbt run)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --profiles-dir /home/airflow/gcs/data/.dbt/',
        env={
            'GOOGLE_APPLICATION_CREDENTIALS': 'temp/google_key.json'
        }
    )

    # Task 3: Run dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /home/airflow/gcs/data/.dbt/',
        env={
            'GOOGLE_APPLICATION_CREDENTIALS': 'temp/google_key.json'
        }
    )

    # Task dependencies
    write_service_account_key >> fetch_profiles >> dbt_run >> dbt_test
