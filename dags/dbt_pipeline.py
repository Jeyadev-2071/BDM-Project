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

    # Task 1: Run dbt run
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --profiles-dir /path/to/profiles --project-dir /path/to/dbt_project',
    )

    # Task 2: Run dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /path/to/profiles --project-dir /path/to/dbt_project',
    )

    # Set task dependencies
    dbt_run >> dbt_test
