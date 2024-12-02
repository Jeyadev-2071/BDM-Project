from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

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

    # Task 1: Fetch profiles.yml from GCS (if using Cloud Composer or GCS storage)
    fetch_profiles = BashOperator(
        task_id='fetch_profiles',
        bash_command='mkdir -p /home/airflow/gcs/data/.dbt && '
                     'gcloud storage cp gs://bdm-project-bucket/.dbt/profiles.yml /home/airflow/gcs/data/.dbt/profiles.yml'
    )

    # Task 2: Run dbt commands (e.g., dbt run)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --profiles-dir /home/airflow/gcs/data/.dbt/',
        
    )

    # Task 3: Run dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /home/airflow/gcs/data/.dbt/',
    )

    # Task Dependencies
    fetch_profiles >> dbt_run >> dbt_test
