import json
import requests
from django.conf import settings

from hefs.classes.error_handler import ErrorHandler
from hefs.classes.microcash_sync.invoice_sender import InvoiceSender
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
                            'gerijptebieren.myshopify.com', 'houseofbeers.nl', 'gerijptebieren.nl']  # both are the german, just to be sure
        request_domain = headers['x-shopify-shop-domain']
        customer_name = json_body['customer']['first_name'] + ' ' + json_body['customer']['last_name']

        if request_domain in partner_websites:
            if headers["x-shopify-topic"] == "orders/create":
                self.error_handler.log_error('Order ontvangen ' + customer_name + request_domain)
                if request_domain != 'houseofbeers.nl':
                    for product in json_body['line_items']:
                        handle = self.info_getter.get_product_handle(product['id'])
                        headers = {"Accept": "application/json", "Content-Type": "application/json",
                                       "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
                        productid, inventory_item_id = self.info_getter.get_ids_from_handle(handle, request_domain, headers)
                        product['id'] = productid
                try:
                    xml_string = f"""
                        <Order>
                          <Reference>{json_body['name']}</Reference>
                          <WebShop>House Of Beers</WebShop>
                          <Naw>
                            <Naam>{customer_name}</Naam>
                            <Adres>{json_body['shipping_address']['address1']}</Adres>
                            <Postcode>{json_body['shipping_address']['zip']}</Postcode>
                            <Plaats>{json_body['shipping_address']['city']}</Plaats>
                            <Email>{json_body['email']}</Email>
                          </Naw>
                          <Products>
                    """
                    for product in json_body['line_items']:
                        xml_string += f"""
                            <Product>
                              <Barcode>{product['product_id']}</Barcode>
                              <Amount>{product['fulfillable_quantity']}</Amount>
                              <Price>{product['price']}</Price> 
                            </Product>
                                        """
                    xml_string += """
                          </Products>
                          <Note></Note>
                        </Order>
                            """
                    invoice_sender = InvoiceSender()
                    invoice_sender.send_invoice(xml_string)
                except Exception as e:
                    self.error_handler.log_error('Order verzenden mislukt:, ' + str(e))
