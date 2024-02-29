from datetime import datetime, timedelta
from django_rq import get_queue
from djangoProject.tasks import update_product_inventory, sync_all_products


def start_schedule_tasks():
    # init for 5 minute task
    update_product_inventory()

    # init for daily task at 22:30
    queue = get_queue()
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, 22, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    queue.enqueue_at(next_run, sync_all_products)
