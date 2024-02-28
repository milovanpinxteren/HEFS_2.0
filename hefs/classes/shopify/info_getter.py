import requests
from django.conf import settings


class InfoGetter:
    def get_product_handle(self, hoBproductID):
        get_product_handle_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{hoBproductID}.json"
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": settings.HOB_ACCESS_TOKEN}
        get_product_handle_url_response = requests.get(url=get_product_handle_url, headers=headers)
        if get_product_handle_url_response.status_code == 200:
            return get_product_handle_url_response.json()['product']['handle']

    def get_ids_from_handle(self, product_handle, domain_name, headers):
        get_product_from_handle_url = f"https://{domain_name}/products/{product_handle}.json"
        get_product_from_handle_url_response = requests.get(url=get_product_from_handle_url, headers=headers)
        if get_product_from_handle_url_response.status_code == 200:
            print('got')
            product_id = get_product_from_handle_url_response.json()['product']["id"]
            inventory_item_id = self.get_inventory_item_id(product_id, domain_name, headers)

            return product_id, inventory_item_id
        else:
            print('no product found, will create product when syncing')
            return False, False

    def get_inventory_item_id(self, product_id, domain_name, headers):
        get_product_inventory_item_id_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id}/variants.json"
        product_inventory_item_response = requests.get(url=get_product_inventory_item_id_url, headers=headers)
        inventory_item_id = product_inventory_item_response.json()['variants'][0]['inventory_item_id']
        return inventory_item_id