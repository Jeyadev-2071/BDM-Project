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
DBT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest" 
PYTHON_SCRIPT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image:latest"  

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

dbt_docs_generate = KubernetesPodOperator(
    task_id="dbt_docs_generate",
    name="dbt-docs-generate-task",
    namespace=GKE_NAMESPACE,
    image=DBT_IMAGE,
    cmds=["dbt"],
    arguments=["docs", "generate"],
    labels={"app": "dbt-docs-task"},
    get_logs=True,
    dag=dag,
)

# Task 2: Run dbt docs serve
dbt_docs_serve = KubernetesPodOperator(
    task_id="dbt_docs_serve",
    name="dbt-docs-serve-task",
    namespace=GKE_NAMESPACE,
    image=DBT_IMAGE,
    cmds=["dbt"],
    arguments=["docs", "serve", "--host", "0.0.0.0", "--port", "8080"],
    labels={"app": "dbt-docs-task"},
    ports=[{"containerPort": 8080, "hostPort": 8080}],
    get_logs=True,
    is_delete_operator_pod=False,  # Keep the pod running to serve the docs
    dag=dag,
)

# Set task dependencies
run_python_script >> dbt_run >> dbt_test >> dbt_docs_generate >> dbt_docs_serve
