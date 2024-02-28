import requests
from django.conf import settings

from hefs.classes.gerijptebieren.error_handler import ErrorHandler


class OrderCreator():
    def create_order(self, json_body, domain_name):
        # TODO: check payment status etc
        handle_and_quantity_dict = self.get_handles_from_ids(json_body, domain_name)
        original_id_and_quantity_dict = self.get_ids_from_handles(handle_and_quantity_dict)
        self.make_order_on_original(json_body, original_id_and_quantity_dict)

    def get_handles_from_ids(self, json_body, domain_name):
        partner_websites = {
            'gereiftebiere.de': {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN},
            '387f61-2.myshopify.com': {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}
            # add domains here
        }

        product_ids = ''
        handle_and_quantity_dict = {}  # create id as key, quantity as value. Later overwrite the id to be the handle
        for line_item in json_body['line_items']:
            product_id = line_item['product_id']
            handle_and_quantity_dict[line_item['product_id']] = line_item['fulfillable_quantity']
            product_ids += str(product_id) + ','  # has to be a string
        product_ids = product_ids[:-1]  # remove the last ', '

        request_domain_dict = partner_websites[domain_name]
        request_domain_name = list(request_domain_dict.keys())[0]
        token = request_domain_dict[request_domain_name]
        get_products_url = f"https://{request_domain_name}/admin/api/2023-10/products.json?ids={product_ids}"
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": token}

        get_product_response = requests.get(url=get_products_url, headers=headers)
        if get_product_response.status_code == 200 and len(get_product_response.json()['products']) > 0:
            get_product_response = get_product_response.json()
            product_handles = []
            for product in get_product_response['products']:
                handle = product['handle']
                handle_and_quantity_dict[product['handle']] = handle_and_quantity_dict[product['id']]
                del handle_and_quantity_dict[product['id']]
                product_handles.append(handle)

            return handle_and_quantity_dict
        else:
            error_message = 'OrderCreator: Get products from ID on site:' + domain_name + ' of order' + \
                            json_body["name"] + ' failed, productIDs: ' + str(
                product_ids) + ' url:' + get_products_url + ' status code: ' + str(get_product_response.status_code)
            error_handler = ErrorHandler()
            error_handler.log_error(error_message)
            raise Exception

    def get_ids_from_handles(self, handle_and_quantity_dict):  # On original website
        # flag order if handle does not exist
        self.original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                                 "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        original_id_and_quantity_dict = handle_and_quantity_dict.copy()
        for handle, quantity in handle_and_quantity_dict.items():
            get_product_on_original_site_url = f"https://gerijptebieren.nl/products/{handle}.json"
            get_product_original_site_response = requests.get(url=get_product_on_original_site_url,
                                                              headers=self.original_headers)
            if get_product_original_site_response.status_code == 200:
                original_variant_id = get_product_original_site_response.json()['product']['variants'][0]['id']
                original_id_and_quantity_dict[original_variant_id] = handle_and_quantity_dict[handle]
                del original_id_and_quantity_dict[handle]
            else:
                error_message = 'OrderCreator: no productID on found on site: gerijptebieren.nl for handle: ' + str(
                    handle) + ' status code: ' + str(get_product_original_site_response.status_code)
                error_handler = ErrorHandler()
                error_handler.log_error(error_message)
                raise Exception

        return original_id_and_quantity_dict

    def make_order_on_original(self, json_body, original_id_and_quantity_dict):

        line_item_array = []
        for variant_id, quantity in original_id_and_quantity_dict.items():
            line_item_array.append({"variant_id": variant_id, "quantity": quantity}) #after testing
            # line_item_array.append({"variant_id": 47818297901384, "quantity": quantity, "requires_shipping": True})

        #TODO: shipping and discounts
        payload = {
            "order": {
                "email": json_body['contact_email'],
                "fulfillment_status": None,
                "send_receipt": False,
                "send_fulfillment_receipt": False,
                "line_items": line_item_array,
                "name": json_body["name"],
                "customer_locale": json_body["customer_locale"],
                "inventory_behaviour": "decrement_obeying_policy",
                "total_discounts": json_body['total_discounts'],
                "total_price": json_body['total_price'],
                "billing_address": {
                    "first_name": json_body['billing_address']['first_name'],
                    "last_name": json_body['billing_address']['last_name'],
                    "phone": json_body['billing_address']['phone'],
                    "address1": json_body['billing_address']['address1'],
                    "city": json_body['billing_address']['city'],
                    "province": json_body['billing_address']['province'],
                    "country": json_body['billing_address']['country'],
                    "zip": json_body['billing_address']['zip'],
                },
                "shipping_address": {
                    "first_name": json_body['shipping_address']['first_name'],
                    "last_name": json_body['shipping_address']['last_name'],
                    "phone": json_body['shipping_address']['phone'],
                    "address1": json_body['shipping_address']['address1'],
                    "city": json_body['shipping_address']['city'],
                    "province": json_body['shipping_address']['province'],
                    "country": json_body['shipping_address']['country'],
                    "zip": json_body['shipping_address']['zip'],
                },
                "shipping_lines": [{
                    "discounted_price": json_body['shipping_lines'][0]['discounted_price'],
                    "price": json_body['shipping_lines'][0]['price']
                }],
            },
            "customer": {
                "first_name": json_body['customer']['first_name'],
                "last_name": json_body['customer']['last_name'],
                "email": json_body['customer']['email'],
            },
        }


        # use self.original_headers and https://gerijptebieren.nl after development
        # headers = {"Accept": "application/json", "Content-Type": "application/json",
        #            "X-Shopify-Access-Token": settings.GEREIFTEBIERE_ACCESS_TOKEN}
        # create_order_on_original_site_url = f"https://387f61-2.myshopify.com/admin/api/2023-10/orders.json"
        create_order_on_original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/orders.json"
        create_order_original_site_response = requests.post(url=create_order_on_original_site_url,
                                                            headers=self.original_headers, json=payload)

        if create_order_original_site_response.status_code == 201:
            print('order created', json_body["name"])
        else:
            error_message = 'Failed to create order in gerijptebieren. OrderName: ' + json_body[
                "name"] + ' status code: ' + str(create_order_original_site_response.status_code)
            error_handler = ErrorHandler()
            error_handler.log_error(error_message)
            raise Exception
