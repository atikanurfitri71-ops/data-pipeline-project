from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "atika",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="crypto_etl_pipeline",
    default_args=default_args,
    description="ETL pipeline untuk data crypto dari CoinGecko",
    schedule_interval="*/10 * * * *",  # jalan tiap 1 jam
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["etl", "crypto"],
) as dag:

    extract_task = BashOperator(
        task_id="extract_data",
        bash_command="cd /opt/airflow && python extract/extract.py",
    )

    transform_task = BashOperator(
        task_id="transform_data",
        bash_command="cd /opt/airflow && python transform/transform.py",
    )

    load_task = BashOperator(
        task_id="load_data",
        bash_command="cd /opt/airflow && python load/load.py",
    )

    # Urutan eksekusi: extract → transform → load
    extract_task >> transform_task >> load_task