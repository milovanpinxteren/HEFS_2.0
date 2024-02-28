import requests
from django.conf import settings

from hefs.classes.gerijptebieren.error_handler import ErrorHandler
from hefs.classes.gerijptebieren.product_updater import ProductUpdater
from hefs.classes.gerijptebieren.translator import Translator


class ProductCreator():
    def create_product(self, json_body):
        partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        for domain_name, token in partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            metafields = self.check_existment_and_metafields(domain_name, headers, json_body)
            if metafields != False:
                create_product_url = f"https://{domain_name}/admin/api/2023-10/products.json"
                translator = Translator()
                translated_body = translator.translate_from_google(domain_name, json_body['body_html'])
                create_product_data = {"product": {
                    "title": json_body['title'],
                    "handle": json_body['handle'],
                    "body_html": translated_body,
                    "vendor": json_body['vendor'],
                    "status": json_body['status'],
                    "tags": json_body['tags'],
                    "published_at": json_body['published_at'],
                    "published_scope": json_body['published_scope'],
                    "variants": [{
                        "barcode": json_body['variants'][0]['barcode'],
                        "compare_at_price": json_body['variants'][0]['compare_at_price'],
                        "price": json_body['variants'][0]['price'],
                        "tags": json_body['variants'][0]['price'],
                        "sku": json_body['variants'][0]['sku'],
                        "grams": json_body['variants'][0]['grams'],
                        "inventory_management": json_body['variants'][0]['inventory_management'],
                        "weight": json_body['variants'][0]['weight'],
                        "weight_unit": json_body['variants'][0]['weight_unit'],
                    }],
                    "metafields": metafields,
                }}
                images_array = []
                for i in range(0, len(json_body['images'])):
                    image_dict = json_body['images'][i]
                    images_array.insert(i, image_dict)
                create_product_data['product']["images"] = images_array
                create_product_response = requests.post(url=create_product_url, headers=headers,
                                                        json=create_product_data)
                if create_product_response.status_code == 201:
                    print('Product created', json_body['title'], create_product_response)
                    self.update_product_quantity(create_product_response, domain_name, headers,
                                                 json_body)  # !important -> as last, other updates set inventory on 0

                else:
                    error_message = 'ProductCreator: Failed to create product: ' + json_body[
                        'title'] + 'on ' + create_product_url + 'status code: ' + str(create_product_response)
                    error_handler = ErrorHandler()
                    error_handler.log_error(error_message)
                    raise Exception
            else:
                error_message = 'ProductCreator: Failed to create product because product already exists: ' + json_body[
                    'title'] + ' update initialized'
                error_handler = ErrorHandler()
                error_handler.log_error(error_message)
                raise Exception

    def update_product_quantity(self, create_product_response, domain_name, headers, json_body):
        product_id_on_partner_site = create_product_response.json()['product']['id']
        get_product_variant_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id_on_partner_site}/variants.json"
        product_variant_on_partner_response = requests.get(url=get_product_variant_on_partner_site_url, headers=headers)

        if len(json_body['variants']) == len(product_variant_on_partner_response.json()['variants']) == 1:
            partner_inventory_item_id = product_variant_on_partner_response.json()['variants'][0]['inventory_item_id']
            inventory_item_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels/set.json"
            locations_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/locations.json"
            locations_on_partner_site_url_response = requests.get(
                url=locations_on_partner_site_url, headers=headers)
            updated_inventory_data = {
                "location_id": locations_on_partner_site_url_response.json()['locations'][0]['id'],
                "inventory_item_id": partner_inventory_item_id,
                "available": json_body['variants'][0]['inventory_quantity'],
            }
            update_inventory_item_on_partner_response = requests.post(
                url=inventory_item_on_partner_site_url, headers=headers, json=updated_inventory_data)
            print('Inventory of created object updated', update_inventory_item_on_partner_response)

    def check_existment_and_metafields(self, domain_name, headers, json_body):
        get_product_on_partner_site_url = f"https://{domain_name}/products/{json_body['handle']}.json"
        product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
        if product_on_partner_response.status_code == 404:  # product handle not found, get metafields of original
            print('product handle not found, get metafields of original')
            original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                                "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
            product_id_original_site = json_body['id']
            get_product_metafields_original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products/{product_id_original_site}/metafields.json"
            get_product_metafields_original_site_response = requests.get(url=get_product_metafields_original_site_url,
                                                                         headers=original_headers)
            try:
                original_metafields = get_product_metafields_original_site_response.json()['metafields']
                translator = Translator()
                for metafield in original_metafields:
                    if metafield['key'] in ['rijpingsmethode', 'soort_bier', 'land_van_herkomst']:
                        translated_value = translator.translate_value_from_dict(domain_name, metafield['key'],
                                                                                metafield['value'])
                        metafield['value'] = translated_value
            except KeyError:  # no metafields found
                original_metafields = []
            return original_metafields

        elif product_on_partner_response.status_code == 200:  # product found, do update
            product_updater = ProductUpdater()
            product_updater.update_product(json_body)
            return False
