from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import subprocess

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

dag = DAG(
    "execute_on_deployment_pod",
    default_args=default_args,
    description="Run dbt commands on existing Deployment pods",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Kubernetes Deployment configuration
DEPLOYMENT_LABEL = "app=dbt-deployement"  # Label of your Deployment
NAMESPACE = "default"


# Step 1: Find the pod name dynamically
def get_deployment_pod():
    """
    Find the pod name from the deployment based on the label selector.
    """
    command = f"kubectl get pods -l {DEPLOYMENT_LABEL} -n {NAMESPACE} -o jsonpath='{{.items[0].metadata.name}}'"
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    pod_name = result.stdout.strip()
    print(f"Deployment pod name: {pod_name}")
    return pod_name


# Step 2: Execute a dbt command in the deployment pod
def run_command_in_pod(command):
    """
    Run a command (e.g., dbt run) in the deployment pod.
    """
    pod_name = get_deployment_pod()
    exec_command = f"kubectl exec -it {pod_name} -n {NAMESPACE} -- {command}"
    subprocess.run(exec_command, shell=True, check=True)
    print(f"Executed command in pod {pod_name}: {command}")


# Airflow tasks
dbt_run_task = PythonOperator(
    task_id="dbt_run",
    python_callable=run_command_in_pod,
    op_args=["dbt run"],  # Command to run in the pod
    dag=dag,
)

dbt_test_task = PythonOperator(
    task_id="dbt_test",
    python_callable=run_command_in_pod,
    op_args=["dbt test"],  # Command to run in the pod
    dag=dag,
)

# Task dependencies
dbt_run_task >> dbt_test_task
