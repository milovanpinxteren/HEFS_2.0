import json
import requests
from django.conf import settings

from hefs.classes.gerijptebieren.product_updater import ProductUpdater


#######################################Assumptions######################################################################
        #Handle Product Change
            #Each shop only has 1 location
            #Each product does not have any (additional) variants (or in shopify -> only has 1 variant)
            #Each shop uses API version 2023-10


#ROADMAP: if collection or shipping changed, blog made
#ROADMAP: update costs of product (not used now)

class WebhookHandler():
    def handle_request(self, headers, body):
        json_body = json.loads(body.decode('utf-8'))
        self.authenticate(headers, json_body)

    def authenticate(self, headers, json_body):
        request_domain = headers['x-shopify-shop-domain']
        #TODO: check request

        if request_domain == 'gerijptebieren.myshopify.com':
            if headers["x-shopify-topic"] == "products/delete":
                self.delete_product(json_body)
            elif headers["x-shopify-topic"] == "products/create":
                self.create_product(json_body)
            elif headers["x-shopify-topic"] == "products/update":
                product_updater = ProductUpdater()
                product_updater.update_product(json_body)


        if request_domain != 'gerijptebieren.myshopify.com':
            print('check if order and make order in main')
            # TODO: elif it is an order creation in partner shop (make order in original)






    def delete_product(self, json_body):
        #TODO: delete product
        #jsonbody = {"id":788032119674292922}
        #TODO: for each (get handle, get id on partner, delete)
        pass

    def create_product(self, json_body):
        partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        for domain_name, token in partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            create_product_on_partner_site_url = f"https://{domain_name}/products/{json_body['handle']}.json"

            # if product_on_partner_response.status_code == 200:  # product found, do update
            #     self.update_product_fields(product_on_partner_response, domain_name, headers, json_body)
            #     self.update_product_quantity(product_on_partner_response, domain_name, headers,
            #                                  json_body)  # !important -> as last, other updates set inventory on 0

        pass

