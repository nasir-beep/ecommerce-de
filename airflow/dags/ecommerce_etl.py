from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "ntokozo",
    "depends_on_past": False,
}

with DAG(
    dag_id="ecommerce_etl",
    default_args=default_args,
    description="E-commerce ETL Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    extract = BashOperator(
        task_id="extract_data",
        bash_command="python /opt/airflow/scripts/extract.py",
    )

    transform = BashOperator(
        task_id="transform_data",
        bash_command="python /opt/airflow/scripts/transform.py",
    )

    load = BashOperator(
        task_id="load_data",
        bash_command="python /opt/airflow/scripts/load.py",
    )

    extract >> transform >> load