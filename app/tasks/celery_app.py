from __future__ import annotations

import os

from celery import Celery

celery_app = Celery(
    "product_pipeline",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
)

celery_app.conf.task_routes = {
    "app.tasks.pipeline_tasks.*": {"queue": "pipeline"},
}
