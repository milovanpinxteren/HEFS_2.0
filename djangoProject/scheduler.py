
import time
from datetime import timedelta
from os import getenv

from django.dispatch import receiver
from django_rq import get_queue
from rq import Queue
from rq.registry import ScheduledJobRegistry
from django.conf import settings
from redis import Redis
from djangoProject.tasks import update_product_inventory


def schedule_task():
    # redis_conn = Redis(host=getenv('REDIS_URL', 'localhost:6379'))
    # Create a queue
    # queue = Queue(connection=redis_conn)
    queue = get_queue()
    while True:
        job = queue.enqueue(update_product_inventory)
        # print(job in queue)  # Outputs False as job is not enqueued
        print('job in queue, scheduler')
        registry = ScheduledJobRegistry(queue=queue)
        # print(job in registry)
        time.sleep(int(settings.SCHEDULE_INTERVAL))

