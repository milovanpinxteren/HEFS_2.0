from hefs.classes.microcash_sync.ftp_getter import FTPGetter
from django_rq import get_queue
from django.conf import settings
from datetime import datetime, timedelta


def update_product_inventory():
    ftp_getter = FTPGetter()
    get_changed_file = ftp_getter.get_ftp_changed_file()
    get_changed_file()
    queue = get_queue()
    print('enqueing')
    queue.enqueue_in(timedelta(seconds=int(settings.SCHEDULE_INTERVAL)), get_changed_file)

def sync_all_products():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_full_file()
    queue = get_queue()
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, 22, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    print('enqueing full sync')
    queue.enqueue_at(next_run, sync_all_products)