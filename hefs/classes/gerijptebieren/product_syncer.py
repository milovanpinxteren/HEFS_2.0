import requests
from django.conf import settings


class ProductSyncer():
    def do_sync(self):
        self.original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                            "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        self.partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here

        print('sync')
        all_products_list = self.get_all_original_products()
        self.check_products_on_partner_sites(all_products_list)
        # Check if it exists (also check drafts)
        # If it does not exist -> make the product

        # For each product on partner
        # check if it exists on gerijptebieren
        # if it does not exist (flag it and allow for manual deletion)

    def get_all_original_products(self):
        last_product_id = 0
        get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?since_id={last_product_id}"
        get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
                                                              headers=self.original_headers)
        status_code = get_all_product_original_site_response.status_code
        all_products_list = []
        while status_code == 200:
            get_all_product__original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products.json?limit=250&since_id={last_product_id}"
            get_all_product_original_site_response = requests.get(url=get_all_product__original_site_url,
                                                                         headers=self.original_headers)
            all_products_list.append(get_all_product_original_site_response.json()['products'])
            status_code = get_all_product_original_site_response.status_code
            try:
                last_product_id = get_all_product_original_site_response.json()['products'][249]['id']
            except IndexError:
                status_code = 404

        return all_products_list

    def check_products_on_partner_sites(self, all_products_list):
        for domain_name, token in self.partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            succesfull_check_counter = 0
            failed_check_counter = 0
            for product_set in all_products_list: #each set contains 250 products
                for product in product_set:
                    product_handle = product['handle']
                    get_product_on_partner_site_url = f"https://{domain_name}/products/{product_handle}.json"
                    product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
                    if product_on_partner_response.status_code == 200:
                        print('product found, moving on')
                        #TODO: check quantity, price and status
                        succesfull_check_counter += 1
                    else:
                        print('product not found on partner', product_handle)
                        #TODO: log this
                        failed_check_counter += 1
            print('successes: ', succesfull_check_counter)
            print('fails: ', failed_check_counter)
