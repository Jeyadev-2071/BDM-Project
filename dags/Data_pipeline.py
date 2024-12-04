from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import container_v1
from google.oauth2 import service_account
import logging
import os
import json
import subprocess
def check_dbt_version():
    """Function to check dbt version."""
    try:
        result = subprocess.run(["dbt", "--version"], capture_output=True, text=True, check=True)
        logging.info(f"DBT Version Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking dbt version: {e.stderr}")
        raise


def dbt_run():
    """Function to run dbt models."""
    try:
        result = subprocess.run(
            ["dbt", "run"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"DBT Run Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running dbt: {e.stderr}")
        raise


def dbt_test():
    """Function to run dbt tests."""
    try:
        result = subprocess.run(
            ["dbt", "test"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"DBT Test Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running dbt tests: {e.stderr}")
        raise
    
def list_gke_nodes(**kwargs):
    try:
        # Load the service account JSON content from an environment variable
        json_key_content = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if not json_key_content:
            raise ValueError("GCP_SERVICE_ACCOUNT_JSON environment variable is not set")

        # Parse the JSON content
        credentials_info = json.loads(json_key_content)

        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_info(credentials_info)

        # Initialize the GKE client with the credentials
        client = container_v1.ClusterManagerClient(credentials=credentials)

        # Specify your GCP project, location (region/zone), and cluster name
        project_id = 'iitj-capstone-project-group-18'
        location = 'asia-south1'  # e.g., 'us-central1-a'
        cluster_name = 'bdm-project'

        # Construct the cluster path
        cluster_path = client.cluster_path(project_id, location, cluster_name)

        # Get the cluster details
        cluster = client.get_cluster(name=cluster_path)

        # Log the cluster details
        logging.info(f"Cluster Name: {cluster.name}")
        logging.info(f"Cluster Status: {cluster.status}")
        logging.info(f"Node Pools: {cluster.node_pools}")

        # List nodes in the cluster
        for node_pool in cluster.node_pools:
            logging.info(f"Node Pool: {node_pool.name}")
            for node in node_pool.instance_group_urls:
                logging.info(f"Node: {node}")

    except Exception as e:
        logging.error(f"Error accessing GKE cluster: {e}")
        raise

default_args = {
    'start_date': datetime(2024, 12, 4),
}

with DAG(
    'gke_access_check',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    check_gke_access = PythonOperator(
        task_id='list_gke_nodes',
        python_callable=list_gke_nodes,
        provide_context=True,
    )
    
    check_dbt_version_task = PythonOperator(
        task_id='check_dbt_version',
        python_callable=check_dbt_version,
    )
    
    dbt_run_task = PythonOperator(
        task_id='dbt_run',
        python_callable=dbt_run,
    )

    # Task to run dbt tests
    dbt_test_task = PythonOperator(
        task_id='dbt_test',
        python_callable=dbt_test,
    )

    # Task dependencies
    check_gke_access >> check_dbt_version_task >> dbt_run_task >> dbt_test_task