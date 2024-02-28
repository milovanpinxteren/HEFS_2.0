import requests
from django.conf import settings

class ProductMaker:

    def create_product(self, shopifyID, domain_name, headers):
        original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": settings.HOB_ACCESS_TOKEN}
        get_product_info_url = f'https://7c70bf.myshopify.com/admin/api/2023-10/products/{shopifyID}.json'
        get_product_info_response = requests.get(url=get_product_info_url, headers=original_headers)
        if get_product_info_response.status_code == 200:
            get_product_metafields_url = f"https://7c70bf.myshopify.com/admin/api/2023-10/products/{shopifyID}/metafields.json"
            get_product_metafields_response = requests.get(url=get_product_metafields_url, headers=original_headers)
            if get_product_metafields_response.status_code == 200:
                product_info = get_product_info_response.json()
                metafields = get_product_metafields_response.json()['metafields']
                create_product_url = f"https://{domain_name}/admin/api/2023-10/products.json"
                product_info['product']['metafields'] = metafields
                create_product_response = requests.post(url=create_product_url, headers=headers,
                                                        json=product_info)
                if create_product_response.status_code == 201:
                    return True, 201
                else:
                    return False, create_product_response.status_code




