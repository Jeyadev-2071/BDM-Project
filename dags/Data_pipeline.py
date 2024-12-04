from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2024, 12, 4),
    'retries': 1,
}

# Specify your GKE namespace and image containing dbt
GKE_NAMESPACE = "default"
DBT_IMAGE = "gcr.io/iitj-capstone-project-group-18/dbt_image" 

with DAG(
    'dbt_workflow_in_gke',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Task to check dbt version
    check_dbt_version = KubernetesPodOperator(
        task_id='check_dbt_version',
        name='check-dbt-version',
        namespace=GKE_NAMESPACE,
        image=DBT_IMAGE,
        cmds=["sh", "-c"],
        arguments=["dbt --version"],
        is_delete_operator_pod=True,
    )

    # Task to run dbt models
    dbt_run = KubernetesPodOperator(
        task_id='dbt_run',
        name='dbt-run',
        namespace=GKE_NAMESPACE,
        image=DBT_IMAGE,
        cmds=["sh", "-c"],
        arguments=["dbt run --profiles-dir /path/to/your/profiles"],
        is_delete_operator_pod=True,
    )

    # Task to run dbt tests
    dbt_test = KubernetesPodOperator(
        task_id='dbt_test',
        name='dbt-test',
        namespace=GKE_NAMESPACE,
        image=DBT_IMAGE,
        cmds=["sh", "-c"],
        arguments=["dbt test --profiles-dir /path/to/your/profiles"],
        is_delete_operator_pod=True,
    )

    # Task dependencies
    check_dbt_version >> dbt_run >> dbt_test
