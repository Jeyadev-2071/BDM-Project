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

    
    # Task 1: Write the JSON content from the environment variable to a temporary file
    write_service_account_key = BashOperator(
        task_id='write_service_account_key',
        bash_command="""
        mkdir -p temp &&
        echo "$SERVICE_ACCOUNT_KEY" > temp/google_key.json
        """,
        env={'SERVICE_ACCOUNT_KEY': '{{ var.value.service_account_key }}'}
    )
    # debug_env = BashOperator(
    # task_id='debug_env',
    # bash_command='echo $PATH && which dbt'
    # )

    fetch_profiles = BashOperator(
    task_id='fetch_profiles',
    bash_command="""
    set -e  # Exit on error
    echo "Creating directory for profiles.yml..."
    mkdir -p /home/airflow/gcs/data/.dbt
    echo "Copying profiles.yml from GCS to /home/airflow/gcs/data/.dbt/..."
    gcloud storage cp gs://bdm-project-bucket/dbt/.dbt/profiles.yml /home/airflow/gcs/data/.dbt/profiles.yml
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
            'PATH': '/opt/python3.11/bin:$PATH',
            'GOOGLE_APPLICATION_CREDENTIALS': 'temp/google_key.json'
        }
    )

    # Task 3: Run dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /home/airflow/gcs/data/.dbt/',
        env={
            'PATH': '/opt/python3.11/bin:$PATH',
            'GOOGLE_APPLICATION_CREDENTIALS': 'temp/google_key.json'
        }
    )

    # Task dependencies
    write_service_account_key >> fetch_profiles >> dbt_run >> dbt_test
