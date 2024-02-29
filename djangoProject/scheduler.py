
import time
from datetime import timedelta
from os import getenv

from django.dispatch import receiver
from django_rq import get_queue
from rq import Queue
from rq.registry import ScheduledJobRegistry
from django.conf import settings
from redis import Redis
from djangoProject.tasks import update_product_inventory, sync_all_products
from datetime import datetime, timedelta


def start_schedule_tasks():
    #init for 5 minute task
    update_product_inventory()

    #init for daily task at 22:30
    queue = get_queue()
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, 22, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    queue.enqueue_at(next_run, sync_all_products)



