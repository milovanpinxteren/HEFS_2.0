import requests

from hefs.classes.shopify.info_getter import InfoGetter


class InventoryUpdater:
    def __init__(self):
        self.info_getter = InfoGetter()
    def update_product_quantity(self, websites, locations, hoBproductID, product_handle, inventory_quantity):
        for domain_name, token in websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            if domain_name == '7c70bf.myshopify.com':
                product_id = hoBproductID
                inventory_item_id = self.info_getter.get_inventory_item_id(product_id, domain_name, headers)
            else:
                product_id, inventory_item_id = self.info_getter.get_ids_from_handle(product_handle, domain_name, headers)
            if product_id: #if product exists
                update_inventory_data = {
                    "location_id": locations[domain_name],
                    "inventory_item_id": inventory_item_id,
                    "available": inventory_quantity}
                update_inventory_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels/set.json"
                update_inventory_response = requests.post(
                    url=update_inventory_url, headers=headers, json=update_inventory_data)
                if update_inventory_response.status_code == 200:
                    print('success')
                elif update_inventory_response.status_code != 200:
                    print(update_inventory_response.status_code)