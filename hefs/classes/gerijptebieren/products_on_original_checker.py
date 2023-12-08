import time

import requests
from django.conf import settings

from hefs.classes.gerijptebieren.error_handler import ErrorHandler
from hefs.classes.gerijptebieren.product_creator import ProductCreator
from hefs.classes.gerijptebieren.product_updater import ProductUpdater


class ProductsOnOriginalChecker():
    def get_all_original_products(self):
        self.original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                                 "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        self.partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        last_product_id = 0
        get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?since_id={last_product_id}"
        get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
                                                              headers=self.original_headers)
        status_code = get_all_product_original_site_response.status_code
        all_products_list = []
        while status_code == 200:
            get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?limit=250&since_id={last_product_id}"
            get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
                                                                  headers=self.original_headers)
            all_products_list.append(get_all_product_original_site_response.json()['products'])
            status_code = get_all_product_original_site_response.status_code
            try:
                last_product_id = get_all_product_original_site_response.json()['products'][249]['id']
            except IndexError:
                status_code = 404

        return all_products_list

    ###For development: only gets 5 products
    # def get_all_original_products(self):
    #     last_product_id = 0
    #     get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?since_id={last_product_id}"
    #     get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
    #                                                           headers=self.original_headers)
    #     status_code = get_all_product_original_site_response.status_code
    #     all_products_list = []
    #
    #     get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?limit=5&since_id={last_product_id}"
    #     get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
    #                                                           headers=self.original_headers)
    #     all_products_list.append(get_all_product_original_site_response.json()['products'])
    #     status_code = get_all_product_original_site_response.status_code
    #
    #     return all_products_list

    def check_products_on_partner_sites(self, all_products_list):
        error_handler = ErrorHandler()
        product_updater = ProductUpdater()
        product_creator = ProductCreator()
        for domain_name, token in self.partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            succesfull_check_counter = 0
            failed_check_counter = 0
            for product_set in all_products_list:  # each set contains 250 products
                for product in product_set:
                    get_product_on_partner_site_url = f"https://{domain_name}/products/{product['handle']}.json"
                    product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
                    if product_on_partner_response.status_code == 200:
                        product_on_partner = product_on_partner_response.json()['product']
                        if product['variants'][0]['price'] == product_on_partner['variants'][0]['price']:
                            print('price is the same, checking inventory')
                            same_inventory = self.check_inventory(product, product_on_partner['id'], domain_name,
                                                                  headers)
                            if not same_inventory:
                                print('inventory not up to date')
                                failed_check_counter += 1
                                error_message = 'ProductSyncer: Inventory not consistent ' + str(
                                    domain_name) + 'Product Handle: ' + str(product['handle'])
                                error_handler.log_error(error_message)
                                product_updater.update_product(product)
                            elif same_inventory:
                                print('correct inventory, go to next product')
                                succesfull_check_counter += 1
                        elif product['variants'][0]['price'] != product_on_partner['variants'][0]['price']:
                            print('price is not the same')
                            failed_check_counter += 1
                            error_message = 'ProductSyncer: Product Price not consistent ' + str(
                                domain_name) + 'Product Handle: ' + str(product['handle'])
                            error_handler.log_error(error_message)
                            product_updater.update_product(product)
                    else:
                        print('product not found on partner', product['handle'])
                        error_message = 'ProductSyncer: Product handle not found on partner: ' + str(
                            domain_name) + 'Product Handle: ' + str(product['handle'])
                        error_handler.log_error(error_message)
                        product_creator.create_product(product)
                        failed_check_counter += 1
            print('successes: ', succesfull_check_counter)
            print('fails: ', failed_check_counter)
            error_message = 'Sync result Product on original: succesfully checked: ' + str(
                succesfull_check_counter) + ', Failed checks: ' + str(failed_check_counter)
            error_handler.log_error(error_message)

    def check_inventory(self, original_product, partner_product_id, domain_name, headers):
        error_handler = ErrorHandler()
        original_quantity = original_product['variants'][0]['inventory_quantity']

        get_product_variant_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{partner_product_id}/variants.json"
        product_variant_on_partner_response = requests.get(url=get_product_variant_on_partner_site_url, headers=headers)
        time.sleep(1)
        if product_variant_on_partner_response.status_code == 200:
            partner_inventory_item_id = product_variant_on_partner_response.json()['variants'][0]['inventory_item_id']
            inventory_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/inventory_items.json?ids={partner_inventory_item_id}"
            inventory_item_on_partner_response = requests.get(url=inventory_on_partner_site_url, headers=headers)
            time.sleep(1)
            if inventory_item_on_partner_response.status_code == 200:
                inventory_item_id_partner = inventory_item_on_partner_response.json()['inventory_items'][0]['id']
                locations_on_partner_url = f"https://{domain_name}/admin/api/2023-10/locations.json"
                locations_on_partner_response = requests.get(url=locations_on_partner_url, headers=headers)
                if locations_on_partner_response.status_code == 200:
                    location_id = locations_on_partner_response.json()['locations'][0]['id']
                    inventory_level_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels.json?location_ids={location_id}&inventory_item_ids={inventory_item_id_partner}"
                    inventory_level_partner = requests.get(url=inventory_level_on_partner_site_url, headers=headers)
                    time.sleep(1)
                    if inventory_level_partner.status_code == 200:
                        availability_on_partner = inventory_level_partner.json()['inventory_levels'][0]['available']
                        # This is the available amount on the partner site. Might not be correct. If a item is ordered but not yet shipped
                        if availability_on_partner == original_quantity:
                            return True
                        elif availability_on_partner != original_quantity:
                            return False
                    elif inventory_level_partner.status_code != 200:
                        error_message = 'ProductSyncer: Failed to get inventory of Product ID: ' + str(
                            partner_product_id) + 'status code: ' + str(
                            inventory_level_partner.status_code)
                        error_handler.log_error(error_message)
                elif locations_on_partner_response.status_code != 200:
                    error_message = 'ProductSyncer: Failed to get locations of Partner site: ' + str(
                        domain_name) + 'status code: ' + str(
                        locations_on_partner_response.status_code)
                    error_handler.log_error(error_message)
            elif inventory_item_on_partner_response.status_code != 200:
                error_message = 'ProductSyncer: Failed to get InventoryID of Partner site, ProductID: ' + str(
                    partner_product_id) + 'status code: ' + str(
                    inventory_item_on_partner_response.status_code)
                error_handler.log_error(error_message)
        elif product_variant_on_partner_response.status_code != 200:
            error_message = 'ProductSyncer: Failed to get Variant ID of Partner site, ProductID: ' + str(
                partner_product_id) + 'status code: ' + str(
                product_variant_on_partner_response.status_code)
            error_handler.log_error(error_message)
