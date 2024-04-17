from hefs.classes.error_handler import ErrorHandler
from hefs.classes.microcash_sync.ftp_getter import FTPGetter
from django_rq import get_queue
from django.conf import settings
from datetime import datetime, timedelta


def update_product_inventory():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_changed_file()
    queue = get_queue()
    print('enqueing small sync')
    queue.enqueue_in(timedelta(seconds=int(settings.SCHEDULE_INTERVAL)), update_product_inventory)

def sync_all_products():
    ftp_getter = FTPGetter()
    error_handler = ErrorHandler()
    ftp_getter.get_ftp_full_file()
    queue = get_queue()
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, 23, 30)
    if now > next_run:
        next_run += timedelta(days=1)
    print('enqueing full sync for', next_run)
    error_handler.log_error('enqueing full sync for' + str(next_run))

    queue.enqueue_at(next_run, sync_all_products)