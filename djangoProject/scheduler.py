from datetime import datetime, timedelta
from django_rq import get_queue
from djangoProject.tasks import update_product_inventory, sync_all_products
from hefs.classes.error_handler import ErrorHandler


def start_schedule_tasks():
    error_handler = ErrorHandler()
    queue = get_queue()
    queue.empty()
    # init for 5 minute task
    update_product_inventory()
    now = datetime.now()
    # init for daily task at 23:30
    next_run = datetime(now.year, now.month, now.day, 23, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    queue.enqueue_at(next_run, sync_all_products)
    error_handler.log_error('in Scheduler enqueing full sync for' + str(next_run))
    print('queued full sync in scheduler')
