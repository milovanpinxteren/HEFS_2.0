import json

from django.conf import settings

from hefs.classes.error_handler import ErrorHandler
from hefs.classes.shopify.info_getter import InfoGetter


class WebhookHandler():
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.info_getter = InfoGetter()

    def handle_request(self, headers, body):
        json_body = json.loads(body.decode('utf-8'))
        self.authenticate(headers, json_body)

    def authenticate(self, headers, json_body):
        partner_websites = ['387f61-2.myshopify.com', 'gereiftebiere.de', '7c70bf.myshopify.com',
                            'gerijptebieren.myshopify.com', 'houseofbeers.nl',
                            'gerijptebieren.nl']  # both are the german, just to be sure
        request_domain = headers['x-shopify-shop-domain']
        customer_name = json_body['customer']['first_name'] + ' ' + json_body['customer']['last_name']

        if request_domain in partner_websites:
            if headers["x-shopify-topic"] == "orders/create":
                self.error_handler.log_error('Order ontvangen ' + customer_name + request_domain)
                if 'GEB' in json_body['name']:
                    for product in json_body['line_items']:
                        handle = self.info_getter.get_product_handle_from_partner(product['product_id'], request_domain)
                        headers = {"Accept": "application/json", "Content-Type": "application/json",
                                   "X-Shopify-Access-Token": settings.HOB_ACCESS_TOKEN}
                        productid, inventory_item_id = self.info_getter.get_ids_from_handle(handle,
                                                                                            '7c70bf.myshopify.com',
                                                                                            headers)
                        product['product_id'] = productid
                try:
                    print(json_body['line_items'])
                    #TODO: update inventory in HOB


                except Exception as e:
                    self.error_handler.log_error('Order verzenden mislukt:, ' + str(e))
