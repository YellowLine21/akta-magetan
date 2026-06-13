# Load Celery app when Django starts so @shared_task decorators are registered.
from celery import current_app as celery_app  # noqa: F401

__all__ = ('celery_app',)
