from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'JD',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'update_dbt_docs',
    default_args=default_args,
    description='Run Python script and dbt commands in existing Kubernetes pod',
    schedule_interval='0 2 * * *',  # Adjust as needed
    catchup=False,
) as dag:

    run_python_script = BashOperator(
        task_id='run_python_script',
        bash_command=(
            'kubectl exec -i -t deployment/dbt-deployement --'
            'python3 Python_Scripts/main.py'
        ),
    )

    run_dbt_commands = BashOperator(
        task_id='run_dbt_commands',
        bash_command=(
            'kubectl exec -i -t deployment/dbt-deployement --'
            'bash -c "dbt run && dbt test && dbt docs generate"'
        ),
    )

    run_python_script >> run_dbt_commands
