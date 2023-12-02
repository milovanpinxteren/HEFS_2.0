import json
import requests
from django.conf import settings

#######################################Assumptions######################################################################
        #Handle Product Change
            #Each shop only has 1 location
            #Each product does not have any (additional) variants (or in shopify -> only has 1 variant)
            #Each shop uses API version 2023-10
class WebhookHandler():
    def handle_request(self, headers, body):
        json_body = json.loads(body.decode('utf-8'))
        self.authenticate(headers, json_body)

    def authenticate(self, headers, json_body):
        request_domain = headers['x-shopify-shop-domain']

        if request_domain == 'gerijptebieren.myshopify.com':
            self.handle_product_change(json_body)
        # TODO: elif it is an order creation in partner shop (make order in original) or product update in original



    def handle_product_change(self, json_body):
        partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        for domain_name, token in partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            get_product_on_partner_site_url = f"https://{domain_name}/products/{json_body['handle']}.json"
            product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
            if product_on_partner_response.status_code == 404:  # product not found, make new one
                print('make new product')
                # TODO: make a new product
            elif product_on_partner_response.status_code == 200: #product found, do update
                self.update_product(product_on_partner_response, domain_name, headers, json_body)
                    # TODO: update metafields, title, description, status, collections, tags, media, price, price comparison, costs, SKU, barcode, weight
                    # TODO: translate body_html

    def update_product(self, product_on_partner_response, domain_name, headers, json_body):
        product_id_on_partner_site = product_on_partner_response.json()['product']['id']
        get_product_variant_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id_on_partner_site}/variants.json"
        product_variant_on_partner_response = requests.get(url=get_product_variant_on_partner_site_url, headers=headers)

        if len(json_body['variants']) == len(
                product_variant_on_partner_response.json()['variants']) == 1:  # If no variants are known
            partner_inventory_item_id = product_variant_on_partner_response.json()['variants'][0]['inventory_item_id']
            inventory_item_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels/set.json"
            locations_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/locations.json"
            locations_on_partner_site_url_response = requests.get(
                url=locations_on_partner_site_url, headers=headers)
            updated_inventory_data = {
                "location_id": locations_on_partner_site_url_response.json()['locations'][0]['id'],
                # Replace with the actual location ID
                "inventory_item_id": partner_inventory_item_id,  # Replace with the actual inventory item ID
                "available": json_body['variants'][0]['inventory_quantity'],  # Replace with the new available quantity
            }
            update_inventory_item_on_partner_response = requests.post(
                url=inventory_item_on_partner_site_url, headers=headers, json=updated_inventory_data)
            print(update_inventory_item_on_partner_response)