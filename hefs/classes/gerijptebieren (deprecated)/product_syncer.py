import time

import requests
from django.conf import settings

from hefs.classes.gerijptebieren import error_handler
from hefs.classes.gerijptebieren.error_handler import ErrorHandler
from hefs.classes.gerijptebieren.product_creator import ProductCreator
from hefs.classes.gerijptebieren.product_updater import ProductUpdater
from hefs.classes.gerijptebieren.products_on_original_checker import ProductsOnOriginalChecker
from hefs.classes.gerijptebieren.products_on_partners_checker import ProductsOnPartnersChecker


class ProductSyncer():
    def do_sync(self, type):

        if type == 'all_original_products':
            products_on_original_checker = ProductsOnOriginalChecker()
            all_products_list = products_on_original_checker.get_all_original_products()
            products_on_original_checker.check_products_on_partner_sites(all_products_list) #for all products on original, checks if it exists on partner
        elif type == 'all_partner_products':
            products_on_partners_checker = ProductsOnPartnersChecker()
            products_on_partners_checker.check_existment_on_original() #for all products on all partners, checks if it exists on original


