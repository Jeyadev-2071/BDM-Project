from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import docker


default_args = {
    'start_date': datetime(2024, 12, 5),
    'retries': 1,
}

def execute_command_in_existing_container(container_name, command):
    """
    Executes a command inside an already running Docker container.
    """
    client = docker.from_env()
    try:
        # Get the container
        container = client.containers.get(container_name)

        # Execute the command inside the container
        exec_id = container.client.api.exec_create(container.id, command)
        output = container.client.api.exec_start(exec_id).decode('utf-8')

        # Log output
        print(f"Command output: {output}")
    except Exception as e:
        print(f"Error: {e}")
        raise e

with DAG(
    'bdm_dbt_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    
    run_ingestion_pipeline = PythonOperator(
        task_id='run_ingestion_pipeline',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  
            'command': 'python3 Python_Scripts/main.py', 
        },
    )
    
    
    checking_dbt_version = PythonOperator(
        task_id='checking_dbt_version',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  # Name of the running container
            'command': 'dbt --version',  # Command to execute inside the container
        },
    )
    
    dbt_run = PythonOperator(
        task_id='dbt_run',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  # Name of the running container
            'command': 'dbt run',  # Command to execute inside the container
        },
    )
    
    dbt_test = PythonOperator(
        task_id='dbt_test',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  # Name of the running container
            'command': 'dbt test',  # Command to execute inside the container
        },
    )
    dbt_gen_docs = PythonOperator(
        task_id='dbt_gen_docs',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  # Name of the running container
            'command': 'dbt generate docs',  # Command to execute inside the container
        },
    )
    dbt_gen_docs_serve = PythonOperator(
        task_id='dbt_gen_docs_serve',
        python_callable=execute_command_in_existing_container,
        op_kwargs={
            'container_name': 'dbt_bigquery',  # Name of the running container
            'command': 'dbt docs serve',  # Command to execute inside the container
        },
    )
    run_ingestion_pipeline >> checking_dbt_version >> dbt_run >> dbt_test >> dbt_gen_docs >> dbt_gen_docs_serve
