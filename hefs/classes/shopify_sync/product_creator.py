from django.conf import settings

from hefs.classes.shopify.graphql_inventory_updater import GraphQLInventoryUpdater
from hefs.classes.shopify.inventory_updater import InventoryUpdater
from hefs.classes.shopify_sync.graphql_queries.get_product_from_handle import GetProductFromHandle
from hefs.classes.shopify_sync.graphql_queries.product_info_getter import ProductInfoGetter
from hefs.classes.shopify_sync.graphql_queries.product_creator import GraphQLProductCreator

class ProductCreator:
    def __init__(self):
        self.product_getter = GetProductFromHandle()
        self.url_to_check = 'https://gerijptebieren.myshopify.com/admin/api/2023-04/graphql.json'
        self.access_token = settings.GERIJPTEBIEREN_ACCESS_TOKEN
        self.product_info_getter = ProductInfoGetter()
        self.product_creator = GraphQLProductCreator()
        self.inventory_updater = GraphQLInventoryUpdater()
        return


    def check_and_update(self, products_to_create):
        for product in products_to_create:
            data = self.product_getter.get_product(product.hob_product_handle, self.url_to_check, self.access_token)
            if data:
                if float(data['variants']['edges'][0]['node']['price']) == float(product.hob_price):
                    product.geb_id = data['id']
                    product.geb_variant_id = data['variants']['edges'][0]['node']['id']
                    product.geb_product_title = data['title']
                    product.geb_product_handle = data['handle']
                    product.geb_price = data['variants']['edges'][0]['node']['price']
                    product.save()
                else:
                    print('price discrepancy')
            else: #product cannot be found on GEB
                created = self.create_product(product)
                if created:
                    print('product created')
                else:
                    raise Exception('product not created')
                
        return

    def create_product(self, product):
        info = self.product_info_getter.get_product_info(product.hob_id)
        created = self.product_creator.create_product_with_graphql(info, self.url_to_check, self.access_token)
        return created
