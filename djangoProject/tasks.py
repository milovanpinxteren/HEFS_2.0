from hefs.classes.microcash_sync.ftp_getter import FTPGetter

import time
from django_rq import get_queue
from rq.registry import ScheduledJobRegistry
from django.conf import settings
from djangoProject.tasks import update_product_inventory, sync_all_products
from datetime import datetime, timedelta


def update_product_inventory():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_changed_file()
    queue = get_queue()
    queue.enqueue_in(timedelta(seconds=settings.SCHEDULE_INTERVAL), update_product_inventory)

def sync_all_products():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_full_file()