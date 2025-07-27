from app.tasks import celery_app

@celery_app.task
def example_task(name: str) -> str:
    return f"Hello {name}"