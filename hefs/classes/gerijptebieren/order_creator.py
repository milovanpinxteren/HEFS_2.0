import requests
from django.conf import settings


class OrderCreator():
    def create_order(self, json_body, domain_name):
        handle_and_quantity_dict = self.get_handles_from_ids(json_body, domain_name)
        original_id_and_quantity_dict = self.get_ids_from_handles(handle_and_quantity_dict)
        self.make_order_on_original(json_body, original_id_and_quantity_dict)

    def get_handles_from_ids(self, json_body, domain_name):
        partner_websites = {
            'gereiftebiere.de': {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}}  # add domains here

        product_ids = ''
        handle_and_quantity_dict = {}  # create id as key, quantity as value. Later overwrite the id to be the handle
        for line_item in json_body['line_items']:
            product_id = line_item['id']
            handle_and_quantity_dict[line_item['id']] = line_item['fulfillable_quantity']
            product_ids += str(product_id) + ','  # has to be a string
        product_ids = product_ids[:-1]  # remove the last ', '

        request_domain_dict = partner_websites[domain_name]
        request_domain_name = list(request_domain_dict.keys())[0]
        token = request_domain_dict[request_domain_name]
        get_products_url = f"https://{request_domain_name}/admin/api/2023-10/products.json?ids={product_ids}"
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": token}

        get_product_response = requests.get(url=get_products_url, headers=headers).json()
        product_handles = []
        for product in get_product_response['products']:
            handle = product['handle']
            handle_and_quantity_dict[product['handle']] = handle_and_quantity_dict[product['id']]
            del handle_and_quantity_dict[product['id']]
            product_handles.append(handle)

        return handle_and_quantity_dict

    def get_ids_from_handles(self, handle_and_quantity_dict):  # On original website
        # flag order if handle does not exist
        self.original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                                 "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        for handle, quantity in handle_and_quantity_dict.items():
            get_product_on_original_site_url = f"https://gerijptebieren.nl/products/{handle}.json"
            get_product_original_site_response = requests.get(url=get_product_on_original_site_url,
                                                              headers=self.original_headers)
            # TODO what if id not found?
            original_variant_id = get_product_original_site_response.json()['product']['variants'][0]['id']
            handle_and_quantity_dict[original_variant_id] = handle_and_quantity_dict[handle]
            del handle_and_quantity_dict[handle]
        original_id_and_quantity_dict = handle_and_quantity_dict

        return original_id_and_quantity_dict

    def make_order_on_original(self, json_body, original_id_and_quantity_dict):
        # use self.original_headers and https://gerijptebieren.nl after development
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        create_order_on_original_site_url = f"https://387f61-2.myshopify.com/admin/api/2023-10/orders.json"
        #This works
        #TODO: it's 1 order, vairant should be appended to payload, and one call.
        #TODO: correct call, orderID, fulfillment
        #TODO: check if this updates stock
        for variant_id, quantity in original_id_and_quantity_dict.items():
            payload = {"order": {"email": "foo@example.com", "fulfillment_status": "fulfilled", "send_receipt": False,
                                 "send_fulfillment_receipt": False,
                                 "line_items": [{"variant_id": variant_id, "quantity": quantity}]}}
            get_product_original_site_response = requests.post(url=create_order_on_original_site_url,
                                                              headers=headers, json=payload)
            print(get_product_original_site_response)


