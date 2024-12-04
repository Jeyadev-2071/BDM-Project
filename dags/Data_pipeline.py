from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import logging


def run_dbt_in_gke(command, namespace="default", pod_name="dbt-deployement-5dc96f4bb-gd7bh", cluster_name="bdm-project"):
    """
    Function to execute a dbt command inside an existing GKE cluster.
    This uses kubectl to interact with the GKE cluster and run commands in a Pod.

    Args:
        command (str): The dbt command to execute (e.g., 'dbt run', 'dbt test').
        namespace (str): Kubernetes namespace where the Pod is located.
        pod_name (str): The name of the Pod to use for running the command.
        cluster_name (str): The name of the GKE cluster.
    """
    try:
        # Ensure kubectl is set up to communicate with the cluster
        logging.info(f"Ensuring kubectl context is set for cluster: {cluster_name}")
        subprocess.run(
            ["gcloud", "container", "clusters", "get-credentials", cluster_name, "--zone", "your-cluster-zone"],
            check=True,
            capture_output=True,
            text=True
        )

        # Run the dbt command inside the Pod
        logging.info(f"Executing command '{command}' in Pod '{pod_name}' within namespace '{namespace}'")
        result = subprocess.run(
            ["kubectl", "exec", pod_name, "-n", namespace, "--", "sh", "-c", command],
            check=True,
            capture_output=True,
            text=True
        )

        logging.info(f"Command Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        raise


# Define specific tasks for dbt
def check_dbt_version_in_gke():
    run_dbt_in_gke("dbt --version")


def dbt_run_in_gke():
    run_dbt_in_gke("dbt run --profiles-dir /path/to/your/profiles")


def dbt_test_in_gke():
    run_dbt_in_gke("dbt test --profiles-dir /path/to/your/profiles")


# Default arguments for the DAG
default_args = {
    'start_date': datetime(2024, 12, 4),
    'retries': 1,
}

# Define the DAG
with DAG(
    'dbt_workflow_in_gke',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Task to check dbt version
    check_dbt_version_task = PythonOperator(
        task_id='check_dbt_version',
        python_callable=check_dbt_version_in_gke,
    )

    # Task to run dbt models
    dbt_run_task = PythonOperator(
        task_id='dbt_run',
        python_callable=dbt_run_in_gke,
    )

    # Task to run dbt tests
    dbt_test_task = PythonOperator(
        task_id='dbt_test',
        python_callable=dbt_test_in_gke,
    )

    # Task dependencies
    check_dbt_version_task >> dbt_run_task >> dbt_test_task
