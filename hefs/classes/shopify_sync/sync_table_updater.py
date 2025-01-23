import requests
from django.conf import settings
from django.db.models import Q

from hefs.classes.shopify_sync.graphql_queries.all_products_getter import AllProductsGetter
from hefs.classes.shopify_sync.product_creator import ProductCreator
from hefs.models import SyncInfo


class SyncTableUpdater:
    def __init__(self):
        self.hob_access_token = settings.HOB_ACCESS_TOKEN
        self.all_product_getter = AllProductsGetter()
        self.product_creator = ProductCreator()
        print('updating table')
        return

    def start_full_sync(self):
        print('starting full sync')
        #FLOW:
            # - Get all products from House of Beers
        # all_products = self.all_product_getter.get_all_products()
            # - Update the hob-related info in the SyncInfo Database model
        # self.update_hob_info(all_products)
            # - Check and Create GEB products
            # - Update GEB quantities
            # -
            # -

        # print('got products')
        self.update_geb_info()

        return True

    def update_hob_info(self, all_products):
        for product in all_products:
            id = product['id']
            title = product['title']
            handle = product['handle']
            total_inventory = product['totalInventory']
            variant_id = product['variants']['edges'][0]['node']['id']
            variant_price = product['variants']['edges'][0]['node']['price']
            sync_info, created = SyncInfo.objects.get_or_create(
                hob_id=id,
                defaults={
                    'hob_product_title': title,
                    'hob_product_handle': handle,
                    'quantity': total_inventory,
                    'hob_variant_id': variant_id,
                    'hob_price': variant_price,
                }
            )

            if not created:  # If the object already exists, check for changes
                update_fields = []
                # Check and update total inventory
                if sync_info.quantity != total_inventory:
                    print('updating product quantity:', title)
                    sync_info.quantity = total_inventory
                    update_fields.append('quantity')
                # Check and update price
                if sync_info.hob_price != variant_price:
                    sync_info.hob_price = variant_price
                    update_fields.append('hob_price')
                # Save updates if there are changes
                if update_fields:
                    sync_info.save(update_fields=update_fields)
        return

    def update_geb_info(self):
        products_to_create = SyncInfo.objects.filter(Q(geb_id__isnull=True) | Q(geb_id=""))
        self.product_creator.check_and_update(products_to_create)
        products_to_check = SyncInfo.objects.filter(geb_id__isnull=False)

        return
