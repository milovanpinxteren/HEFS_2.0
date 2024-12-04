import time

import requests
from django.conf import settings


class ProductMaker:

    def create_product(self, shopifyID, domain_name, headers):
        try:
            time.sleep(1)
            original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                           "X-Shopify-Access-Token": settings.HOB_ACCESS_TOKEN}
            get_product_info_url = f'https://7c70bf.myshopify.com/admin/api/2023-10/products/{shopifyID}.json'
            get_product_info_response = requests.get(url=get_product_info_url, headers=original_headers)
            if get_product_info_response.status_code == 200:
                product_info = get_product_info_response.json()
                get_product_metafields_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{shopifyID}/metafields.json"
                time.sleep(1)
                get_product_metafields_response = requests.get(url=get_product_metafields_url, headers=original_headers)
                if get_product_metafields_response.status_code == 200:
                    product_info = get_product_info_response.json()
                create_product_url = f"https://{domain_name}/admin/api/2023-10/products.json"
                try:
                    metafields = get_product_metafields_response.json()['metafields']
                    product_info['product']['metafields'] = metafields
                except Exception as e:
                    print(e)
                time.sleep(1)
                create_product_response = requests.post(url=create_product_url, headers=headers,
                                                            json=product_info)
                if create_product_response.status_code == 201:
                    print('created product')
                    return True, 201
                else:
                    return False, create_product_response.status_code
            elif get_product_info_response.status_code == 429:
                time.sleep(1)
                product_info = get_product_info_response.json()
                get_product_metafields_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{shopifyID}/metafields.json"
                get_product_metafields_response = requests.get(url=get_product_metafields_url, headers=original_headers)
                if get_product_metafields_response.status_code == 200:
                    product_info = get_product_info_response.json()
                create_product_url = f"https://{domain_name}/admin/api/2023-10/products.json"
                try:
                    metafields = get_product_metafields_response.json()['metafields']
                    product_info['product']['metafields'] = metafields
                except Exception as e:
                    print(e)
                create_product_response = requests.post(url=create_product_url, headers=headers,
                                                            json=product_info)
                if create_product_response.status_code == 201:
                    print('created product')
                    return True, 201
                else:
                    print('did not create')
                    if 'metafields' in product_info['product']:
                        product_info['product'].pop('metafields', None)
                        create_product_response = requests.post(url=create_product_url, headers=headers,
                                                                json=product_info)
                        if create_product_response.status_code == 201:
                            print('created product')
                            return True, 201
                        else:
                            return False, create_product_response.status_code
        except Exception as e:
            print(e)
            return False, e



