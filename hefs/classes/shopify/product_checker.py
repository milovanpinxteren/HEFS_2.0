import requests


class ProductChecker:
    def check_existment_from_handle(self, domain_name, handle, headers):
        check_existment_url = f"https://{domain_name}/products/{handle}.json"
        check_existment_response = requests.get(url=check_existment_url, headers=headers)
        if check_existment_response.status_code == 200:
            return check_existment_response.json()
        else:
            return False

    def check_price(self, existment_response, price):
        if existment_response['product']['variants'][0]['price'] == price.replace(',', '.'):
            return True
        else:
            return False

    def check_inventory(self, domain_name, headers, product_id, inventory_quantity):
        get_inventory_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id}.json"
        get_inventory_response = requests.get(url=get_inventory_url, headers=headers)
        if get_inventory_response.status_code == 200:
            if get_inventory_response.json()['product']['variants'][0]['inventory_quantity'] == int(inventory_quantity):
                return True
            else:
                return False
        else:
            #TODO: log error
            return False



