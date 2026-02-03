"""
Simple test DAG to verify Airflow DAG parsing
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="test_dag",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["test"],
) as dag:
    EmptyOperator(task_id="test_task")
