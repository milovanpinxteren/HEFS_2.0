from hefs.classes.microcash_sync.ftp_getter import FTPGetter


def update_product_inventory():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_changed_file()

def sync_all_products():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_full_file()