
import time
from datetime import timedelta

from django.dispatch import receiver
from rq import Queue
from rq.registry import ScheduledJobRegistry
from django.conf import settings
from redis import Redis
from djangoProject.tasks import update_product_inventory


def schedule_task():
    redis_conn = Redis()
    # Create a queue
    queue = Queue(connection=redis_conn)
    while True:
        job = queue.enqueue(update_product_inventory)
        print(job in queue)  # Outputs False as job is not enqueued
        print('job in queue, scheduler')
        registry = ScheduledJobRegistry(queue=queue)
        print(job in registry)
        time.sleep(settings.SCHEDULE_INTERVAL)

