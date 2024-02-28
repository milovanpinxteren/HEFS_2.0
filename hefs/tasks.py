from celery import shared_task

from hefs.classes.microcash_sync.ftp_getter import FTPGetter


@shared_task
def sync_changed_inventory():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_changed_file()