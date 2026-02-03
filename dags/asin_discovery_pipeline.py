from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pathlib import Path
import glob
import logging

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}


def merge_discovered_asins(**context):
    """Merge discovered ASINs into watchlist"""
    discovery_output_dir = Path(
        "/home/smlflg/Dokumente/WS2025/DataEnge/arbitrage-tracker/data/discovery"
    )
    watchlist_path = Path(
        "/home/smlflg/Dokumente/WS2025/DataEnge/arbitrage-tracker/config/watchlist.txt"
    )

    existing_asins = set()
    if watchlist_path.exists():
        with open(watchlist_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    existing_asins.add(line)

    discovered_files = list(discovery_output_dir.glob("asins_*.txt"))
    all_discovered = set()
    for filepath in discovered_files:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_discovered.add(line)

    new_asins = all_discovered - existing_asins
    duplicates = len(all_discovered) - len(new_asins)

    if new_asins:
        with open(watchlist_path, "a") as f:
            for asin in sorted(new_asins):
                f.write(f"{asin}\n")
        logging.info(f"Appended {len(new_asins)} new ASINs to watchlist")

    logging.info(
        f"Discovery summary: {len(new_asins)} new, {duplicates} duplicates, {len(all_discovered)} total discovered"
    )

    return {
        "new_asins": len(new_asins),
        "duplicates": duplicates,
        "total": len(all_discovered),
    }


def notify_completion(**context):
    """Send notification on completion"""
    ti = context["task_instance"]
    metrics = ti.xcom_pull(task_ids="merge_results")
    logging.info(f"ASIN Discovery completed: {metrics}")


with DAG(
    dag_id="asin_discovery_pipeline",
    default_args=default_args,
    description="Weekly ASIN discovery pipeline for multiple marketplaces",
    schedule_interval="0 2 * * 0",
    start_date=datetime(2025, 1, 5),
    catchup=False,
    tags=["discovery", "keepa", "asin"],
) as dag:
    start = DummyOperator(task_id="start_discovery")

    discover_fr = BashOperator(
        task_id="discover_marketplace_FR",
        bash_command="python scripts/discover_german_keyboards.py --marketplace FR",
        execution_timeout=timedelta(minutes=30),
        retries=2,
    )

    discover_it = BashOperator(
        task_id="discover_marketplace_IT",
        bash_command="python scripts/discover_german_keyboards.py --marketplace IT",
        execution_timeout=timedelta(minutes=30),
        retries=2,
    )

    discover_es = BashOperator(
        task_id="discover_marketplace_ES",
        bash_command="python scripts/discover_german_keyboards.py --marketplace ES",
        execution_timeout=timedelta(minutes=30),
        retries=2,
    )

    discover_uk = BashOperator(
        task_id="discover_marketplace_UK",
        bash_command="python scripts/discover_german_keyboards.py --marketplace UK",
        execution_timeout=timedelta(minutes=30),
        retries=2,
    )

    merge = PythonOperator(
        task_id="merge_results",
        python_callable=merge_discovered_asins,
    )

    cleanup = BashOperator(
        task_id="cleanup_old_discovery_files",
        bash_command='find /home/smlflg/Dokumente/WS2025/DataEnge/arbitrage-tracker/data/discovery -name "asins_*.txt" -mtime +30 -delete',
        description="Remove discovery files older than 30 days",
    )

    notify = PythonOperator(
        task_id="notify_completion",
        python_callable=notify_completion,
    )

    end = DummyOperator(task_id="end_discovery")

    (
        start
        >> [discover_fr, discover_it, discover_es, discover_uk]
        >> merge
        >> cleanup
        >> notify
        >> end
    )
