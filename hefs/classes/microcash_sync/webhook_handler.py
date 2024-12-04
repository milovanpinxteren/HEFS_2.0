import json

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
                        if 'atiegeld' not in product['name']:
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
                    if len(json_body['line_items']) < 8:
                        invoice_sender = InvoiceSender()
                        invoice_sender.send_invoice(xml_string)
                    else:
                        self.error_handler.log_error(
                            'Order te lang, voor ieder product 1 invoice aanmaken ' + json_body['name'])
                        product_counter = 0
                        for product in json_body['line_items']:
                            if 'atiegeld' not in product['name']:
                                product_counter += 1
                                xml_string = f"""
                                                            <Order>
                                                              <Reference>{json_body['name'] + str(product_counter)}</Reference>
                                                              <WebShop>House Of Beers</WebShop>
                                                              <Naw>
                                                                <Naam>{customer_name}</Naam>
                                                                <Adres>{json_body['shipping_address']['address1']}</Adres>
                                                                <Postcode>{json_body['shipping_address']['zip']}</Postcode>
                                                                <Plaats>{json_body['shipping_address']['city']}</Plaats>
                                                                <Email>{json_body['email']}</Email>
                                                              </Naw>
                                                              <Products>
                                                                <Product>
                                                                  <Barcode>{product['product_id']}</Barcode>
                                                                  <Amount>{product['fulfillable_quantity']}</Amount>
                                                                  <Price>{product['price']}</Price> 
                                                                </Product>
                                                              </Products>
                                                              <Note></Note>
                                                            </Order>
                                                                """
                                invoice_sender = InvoiceSender()
                                invoice_sender.send_invoice(xml_string)
                except Exception as e:
                    self.error_handler.log_error('Order verzenden mislukt:, ' + str(e))
