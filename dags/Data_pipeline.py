from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.providers.google.cloud.hooks.kubernetes_engine import GKEHook
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    'gke_dbt_pipeline',
    default_args=default_args,
    description='Authenticate Airflow with GKE and run dbt pipeline',
    schedule_interval='@daily',  # Adjust schedule as needed
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Task: Authenticate Airflow to GKE
    def get_kube_config():
        """Authenticate to GKE and get kubeconfig."""
        gke_hook = GKEHook(
            gcp_conn_id='google_cloud_default',  # Replace with your GCP connection ID in Airflow
        )
        kube_config = gke_hook.get_cluster_config(
            project_id='iitj-capstone-project-group-18',  
            name='bdm-project',  # Replace with your GKE cluster name
            location='asia-south1	',  # Replace with the region/zone of your cluster
        )
        return kube_config

    # Task: Run dbt pipeline on GKE
    run_dbt_task = KubernetesPodOperator(
        namespace='default',  # Replace with your Kubernetes namespace
        image='gcr.io/iitj-capstone-project-group-18/dbt-image:latest', 
        cmds=['/bin/bash', '-c'],
        arguments=[
            'python3 /app/script.py && '
            'dbt run && dbt test && dbt docs generate'
        ],  # Example commands to execute
        labels={'app': 'dbt-pipeline'},
        name='run-dbt',
        task_id='run_dbt',
        get_logs=True,
        is_delete_operator_pod=True,  # Clean up the pod after execution
        config_file='/path/to/kubeconfig',  # Use the kubeconfig retrieved by get_kube_config()
    )

    # Dependency: Ensure authentication is done before running the task
    run_dbt_task
