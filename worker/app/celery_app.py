"""
Celery app configuration for worker
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "efi_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "evm-sync": {
            "task": "evm_sync_task",
            "schedule": 30.0,  # Every 30 seconds
        },
        "btc-sync": {
            "task": "btc_sync_task",
            "schedule": 60.0,  # Every 60 seconds
        },
        "metrics-aggregate": {
            "task": "metrics_aggregate_task",
            "schedule": 300.0,  # Every 5 minutes
        },
        "alerts": {
            "task": "alerts_task",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)

# Register tasks
from app.ingestion.tasks import evm_sync_task, btc_sync_task, metrics_aggregate_task, alerts_task

celery_app.task(name="evm_sync_task")(evm_sync_task)
celery_app.task(name="btc_sync_task")(btc_sync_task)
celery_app.task(name="metrics_aggregate_task")(metrics_aggregate_task)
celery_app.task(name="alerts_task")(alerts_task)
