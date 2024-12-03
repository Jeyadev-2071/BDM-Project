from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

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
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Configurations
GKE_NAMESPACE = "default"  # Change if your pods are in a different namespace
GKE_CLUSTER_NAME = "bdm-project"
GKE_REGION = "asia-south1"  # e.g., asia-south1
PROJECT_ID = "iitj-capstone-project-group-18"

DBT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest"  # Docker image with dbt installed
PYTHON_SCRIPT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest"  # Docker image with the Python script


# Task 1: Run the Python script
run_python_script = KubernetesPodOperator(
    task_id="run_python_script",
    name="python-script-task",
    namespace=GKE_NAMESPACE,
    image=PYTHON_SCRIPT_IMAGE,
    cmds=["python"],
    arguments=["/app/Python_Script/main.py"],  # Path to the script in the container
    labels={"app": "python-script-task"},
    get_logs=True,
    dag=dag,
)

# Task 2: Run dbt commands (dbt run, dbt test, etc.)
dbt_run = KubernetesPodOperator(
    task_id="dbt_run",
    name="dbt-run-task",
    namespace=GKE_NAMESPACE,
    image=DBT_IMAGE,
    cmds=["dbt"],
    arguments=["run"],
    labels={"app": "dbt-task"},
    get_logs=True,
    dag=dag,
)

dbt_test = KubernetesPodOperator(
    task_id="dbt_test",
    name="dbt-test-task",
    namespace=GKE_NAMESPACE,
    image=DBT_IMAGE,
    cmds=["dbt"],
    arguments=["test"],
    labels={"app": "dbt-task"},
    get_logs=True,
    dag=dag,
)

# Set task dependencies
run_python_script >> dbt_run >> dbt_test
