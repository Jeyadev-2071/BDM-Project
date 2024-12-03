from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.kubernetes_engine import GKEStartJobOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import V1ContainerPort
# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}
dag = DAG(
    "kubernetes_dbt_workflow",
    default_args=default_args,
    description="Run Python and dbt commands on Kubernetes using KubernetesPodOperator",
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)
# Configurations
GKE_NAMESPACE = "default"  # Change if your pods are in a different namespace
GKE_CLUSTER_NAME = "bdm-project"
GKE_REGION = "asia-south1"  # e.g., asia-south1
PROJECT_ID = "iitj-capstone-project-group-18"
DBT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest" 
PYTHON_SCRIPT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest"  

# Task 1: Run the Python script
run_python_script = GKEStartJobOperator(
    task_id="run_python_script",
    name="python-script-task",
    location=GKE_REGION,
    namespace=GKE_NAMESPACE,
    image=PYTHON_SCRIPT_IMAGE,
    cluster_name=GKE_CLUSTER_NAME,
    cmds=["python"],
    arguments=["/app/Python_Script/main.py"],  # Path to the script in the container
    labels={"app": "python-script-task"},
    get_logs=True,
    dag=dag,
)
# Task 2: Run dbt commands dbt run
dbt_run = GKEStartJobOperator(
    task_id="dbt_run",
    name="dbt-run-task",
    namespace=GKE_NAMESPACE,
    location=GKE_REGION,
    image=DBT_IMAGE,
    cluster_name=GKE_CLUSTER_NAME,
    cmds=["dbt"],
    arguments=["run"],
    labels={"app": "dbt-task"},
    get_logs=True,
    dag=dag,
)
# Task 3 : Run dbt command test
dbt_test = GKEStartJobOperator(
    task_id="dbt_test",
    name="dbt-test-task",
    namespace=GKE_NAMESPACE,
    location=GKE_REGION,
    image=DBT_IMAGE,
    cluster_name=GKE_CLUSTER_NAME,
    cmds=["dbt"],
    arguments=["test"],
    labels={"app": "dbt-task"},
    get_logs=True,
    dag=dag,
)
# Task 4 : Run dbt command docs generate
dbt_docs_generate = GKEStartJobOperator(
    task_id="dbt_docs_generate",
    name="dbt-docs-generate-task",
    namespace=GKE_NAMESPACE,
    location=GKE_REGION,
    image=DBT_IMAGE,
    cluster_name=GKE_CLUSTER_NAME,
    cmds=["dbt"],
    arguments=["docs", "generate"],
    labels={"app": "dbt-docs-task"},
    get_logs=True,
    dag=dag,
)

# Task 5 : Run dbt command docs serve
dbt_docs_serve = GKEStartJobOperator(
    task_id="dbt_docs_serve",
    name="dbt-docs-serve-task",
    namespace=GKE_NAMESPACE,
    location=GKE_REGION,
    image=DBT_IMAGE,
    cmds=["dbt"],
    cluster_name=GKE_CLUSTER_NAME,
    arguments=["docs", "serve", "--host", "0.0.0.0", "--port", "8080"],
    labels={"app": "dbt-docs-task"},
    ports=[V1ContainerPort(container_port=8080, host_port=8080)],  # Use V1ContainerPort
    get_logs=True,
    is_delete_operator_pod=False,  # Keep the pod running to serve the docs
    dag=dag,
)
# Set task dependencies
run_python_script >> dbt_run >> dbt_test >> dbt_docs_generate >> dbt_docs_serve
