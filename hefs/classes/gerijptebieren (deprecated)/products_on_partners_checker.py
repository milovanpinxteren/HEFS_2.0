import requests
from django.conf import settings

from hefs.classes.gerijptebieren.error_handler import ErrorHandler


class ProductsOnPartnersChecker():

    def get_all_partner_products(self, domain_name, headers):
        last_product_id = 0
        get_all_product_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products.json?since_id={last_product_id}"
        get_all_products_partner_site_response = requests.get(url=get_all_product_partner_site_url,
                                                              headers=headers)
        status_code = get_all_products_partner_site_response.status_code
        all_products_list = []
        while status_code == 200:
            get_all_product_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products.json?limit=250&since_id={last_product_id}"
            get_all_product_partner_site_response = requests.get(url=get_all_product_partner_site_url,
                                                                         headers=headers)
            all_products_list.append(get_all_product_partner_site_response.json()['products'])
            status_code = get_all_product_partner_site_response.status_code
            try:
                last_product_id = get_all_product_partner_site_response.json()['products'][249]['id']
            except IndexError:
                status_code = 404

        return all_products_list
    def check_existment_on_original(self):
        self.original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                                 "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        self.partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}
        error_handler = ErrorHandler()
        for domain_name, token in self.partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            succesfull_check_counter = 0
            failed_check_counter = 0
            all_products_list = self.get_all_partner_products(domain_name, headers)
            for product_set in all_products_list:  # each set contains 250 products
                for product in product_set:
                    get_product_on_original_site_url = f"https://gerijptebieren.nl/products/{product['handle']}.json"
                    product_on_partner_response = requests.get(url=get_product_on_original_site_url, headers=headers)
                    if product_on_partner_response.status_code == 200:
                        succesfull_check_counter += 1
                        print('product found on original, moving on')
                    elif product_on_partner_response.status_code == 404:
                        print('product not found on original, deleting ', product['handle'])
                        del_product_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product['id']}.json"
                        del_product_partner_site_response = requests.delete(url=del_product_partner_site_url,
                                                                             headers=headers)
                        if del_product_partner_site_response.status_code == 200:
                            error_message = 'ProductSyncer: Product handle not found on original, deleted it: ' + str(
                                domain_name) + 'Product Handle: ' + str(product['handle'])
                            error_handler.log_error(error_message)
                        elif del_product_partner_site_response.status_code != 200:
                            error_message = 'ProductSyncer: Product handle not found on original and unable to delete: ' + str(
                                domain_name) + 'Product Handle: ' + str(product['handle'])
                            error_handler.log_error(error_message)
                        failed_check_counter += 1
                    else:
                        print('Error when trying to find product on original', product['handle'])
                        error_message = 'ProductSyncer: Error when trying to find product on original: ' + str(
                            domain_name) + 'Product Handle: ' + str(product['handle'])
                        error_handler.log_error(error_message)
                        failed_check_counter += 1
            print('successes: ', succesfull_check_counter)
            print('fails: ', failed_check_counter)
            error_message = 'Sync result Products on Partner: succesfully checked: ' + str(
                succesfull_check_counter) + ', Failed checks: ' + str(failed_check_counter)
            error_handler.log_error(error_message)
