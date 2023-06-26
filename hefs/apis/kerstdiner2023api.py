import requests


class Kerstdiner2023API:
    def __init__(self):
        self.get_shopify_orders()



    def get_shopify_orders(self):
        shopify_access_token = "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"
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": shopify_access_token}
        response = requests.get(url="https://gerijptebieren.myshopify.com/admin/api/2023-04/orders.json", headers=headers)
        if response.status_code == 200:
            orders = response.json()["orders"]
            # print(orders)
            self.handle_shopify_orders(orders)
        else:
            print("Failed to retrieve orders. Status code:", response.status_code)
            return []




    def handle_shopify_orders(self, orders):
        print(orders)
