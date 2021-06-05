from celery import shared_task

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

# Create your tasks here

# TODO write task to check daily tax rate for every corp

# TODO write task to periodically recalculate tax owed

# Example Task
@shared_task
def my_task():
    pass
