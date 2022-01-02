import logging

from celery import shared_task

from mcs.celery import app

logger = logging.getLogger('django')


@app.task
def check_server_running():
    logger.info("Boy")
