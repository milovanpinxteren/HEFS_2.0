
import time
from datetime import timedelta

from rq import Queue
from rq.registry import ScheduledJobRegistry

from redis import Redis
from djangoProject.tasks import update_product_inventory

def schedule_task():
    redis_conn = Redis()
    # Create a queue
    queue = Queue(connection=redis_conn)
    job = queue.enqueue_in(timedelta(seconds=10), update_product_inventory())
    print(job in queue)  # Outputs False as job is not enqueued
    print('job in queue, scheduler')
    registry = ScheduledJobRegistry(queue=queue)
    print(job in registry)

