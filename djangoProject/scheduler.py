from datetime import datetime, timedelta

from django_rq import get_queue

from djangoProject import settings
from djangoProject.tasks import update_product_inventory, sync_all_products
from hefs.classes.error_handler import ErrorHandler


# from django.conf import settings


def start_schedule_tasks():
    error_handler = ErrorHandler()
    full_sync_queue = get_queue(name=settings.full_sync)
    full_sync_queue.empty()
    # init for 5 minute task
    update_product_inventory()
    now = datetime.now()
    # init for daily task at 23:30
    next_run = datetime(now.year, now.month, now.day, 23, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    full_sync_queue.enqueue_at(next_run, sync_all_products)
    error_handler.log_error('in Scheduler enqueing full sync for' + str(next_run))
    print('queued full sync in scheduler')
