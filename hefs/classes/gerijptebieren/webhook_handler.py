import json
import requests
from django.conf import settings

from hefs.classes.gerijptebieren.order_creator import OrderCreator
from hefs.classes.gerijptebieren.product_creator import ProductCreator
from hefs.classes.gerijptebieren.product_updater import ProductUpdater


#######################################Assumptions######################################################################
        #Handle Product Change
            #Each shop only has 1 location
            #Each product does not have any (additional) variants (or in shopify -> only has 1 variant)
            #Each shop uses API version 2023-10


#ROADMAP: full sync
#ROADMAP: order update/fulfillment also triggers update/fulfilment in partner
#ROADMAP: send mails from partner, not gerijptebieren
#ROADMAP: If publish date is in the future
#ROADMAP: if collection or shipping changed, blog made
#ROADMAP: update costs of product (not used now)

class WebhookHandler():
    def handle_request(self, headers, body):
        json_body = json.loads(body.decode('utf-8'))
        self.authenticate(headers, json_body)

    def authenticate(self, headers, json_body):
        partner_websites = ['387f61-2.myshopify.com', 'gereiftebiere.de'] #both are the german, just to be sure
        request_domain = headers['x-shopify-shop-domain']
        #TODO: check request

        if request_domain == 'gerijptebieren.myshopify.com':
            if headers["x-shopify-topic"] == "products/delete":
                self.delete_product(json_body)
            elif headers["x-shopify-topic"] == "products/create":
                product_creator = ProductCreator()
                product_creator.create_product(json_body)
            elif headers["x-shopify-topic"] == "products/update":
                product_updater = ProductUpdater()
                product_updater.update_product(json_body)




        if request_domain in partner_websites:
            if headers["x-shopify-topic"] == "orders/create":
                order_creator = OrderCreator()
                order_creator.create_order(json_body, request_domain)




#TODO: does not work, ID does not exist after deletion -> no way to get the handle
    def delete_product(self, json_body):
        get_product_original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products/{json_body['id']}.json"
        original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                            "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        get_product_original_site_response = requests.get(url=get_product_original_site_url, headers=original_headers)
        product_handle = get_product_original_site_response.json()['product']['handle']

        partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        for domain_name, token in partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            get_product_on_partner_site_url = f"https://{domain_name}/products/{product_handle}.json"
            product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
            if product_on_partner_response.status_code == 200:  # product handle found
                product_id = product_on_partner_response.json()['product']['id']
                del_product_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id}.json"
                del_product_on_partner_response = requests.delete(url=del_product_on_partner_site_url, headers=headers)
                print('deleted product on partner site', del_product_on_partner_response)






