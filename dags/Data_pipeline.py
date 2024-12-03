from airflow import DAG
from airflow.providers.google.cloud.operators.kubernetes_engine import GKEStartPodOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'your_name',
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'dbt_pipeline',
    default_args=default_args,
    description='Run Python script, dbt commands, and generate docs',
    schedule_interval='0 2 * * *',  # Adjust as needed
    catchup=False,
) as dag:

    run_dbt_tasks = GKEStartPodOperator(
        task_id='run_dbt_tasks',
        project_id='iitj-capstone-project-group-18',
        location='asia-south1',  # e.g., 'us-central1'
        cluster_name='bdm-project',
        namespace='default',
        name='dbt-task-pod',
        image='gcr.io/iitj-capstone-project-group-18/dbt_image:latest',
        cmds=['/bin/bash', '-c'],
        arguments=[
            'python3 Python_Script/main.py && '
            'dbt run && '
            'dbt test && '
            'dbt docs generate && '
            'dbt docs serve --port 8080 --no-browser'
        ],
        get_logs=True,
    )
