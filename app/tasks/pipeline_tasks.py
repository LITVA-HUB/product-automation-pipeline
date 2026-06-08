from __future__ import annotations

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.pipeline_tasks.healthcheck")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
