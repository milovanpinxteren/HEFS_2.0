import requests


class ProductUpdater:
    def update_price(self, domain_name, headers, product_id, variant_id, new_price):
        updated_field_data = {
            "product": {
                "id": product_id,
                "variants": [{
                    "id": variant_id,
                    "price": new_price,
                }]
            }
        }
        update_price_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id}.json"
        update_price_response = requests.put(url=update_price_url, headers=headers, json=updated_field_data)
        if update_price_response.status_code == 200:
            return True
        else:
            #TODO: log eroor
            return False

    def update_inventory(self, domain_name, headers, inventory_item_id, inventory_quantity, location_id):
        update_inventory_data = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": inventory_quantity}
        update_inventory_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels/set.json"
        update_inventory_response = requests.post(
            url=update_inventory_url, headers=headers, json=update_inventory_data)
        if update_inventory_response.status_code == 200:
            return True
        elif update_inventory_response.status_code != 200:
            print(update_inventory_response.status_code)
            return False

