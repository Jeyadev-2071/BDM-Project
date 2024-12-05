from airflow import DAG
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta

import random

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bigquery_hello_world_looping',
    default_args=default_args,
)

hello_world_query = '''
    SELECT 'Hello, World!' AS message;
'''

num_tasks = 3
hello_world_tasks = []

def simulate_failure():
    if random.randint(0, 1) == 1:
        raise AirflowException("Task failed due to simulated failure")

for i in range(num_tasks):
    task_id = f'hello_world_{i+1}'
    hello_world_task = BigQueryOperator(
        task_id=task_id,
        sql=hello_world_query,
        use_legacy_sql=False,
        gcp_conn_id='google_cloud_default',
        dag=dag,
    )
    hello_world_task.execute_callable = simulate_failure
    hello_world_tasks.append(hello_world_task)

# Set task dependencies
for i in range(num_tasks - 1):
    hello_world_tasks[i] >> hello_world_tasks[i+1]