from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import container_v1
from google.oauth2 import service_account
import logging
import os
import json

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
