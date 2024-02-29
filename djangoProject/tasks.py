from hefs.classes.microcash_sync.ftp_getter import FTPGetter


def update_product_inventory():
    ftp_getter = FTPGetter()
    ftp_getter.get_ftp_changed_file()