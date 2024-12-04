import requests
from django.conf import settings
from hefs.classes.gerijptebieren import product_creator
from hefs.classes.gerijptebieren.error_handler import ErrorHandler
from hefs.classes.gerijptebieren.translator import Translator


class ProductUpdater:
    def update_product(self, json_body):
        partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}  # add domains here
        for domain_name, token in partner_websites.items():
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "X-Shopify-Access-Token": token}
            get_product_on_partner_site_url = f"https://{domain_name}/products/{json_body['handle']}.json"
            product_on_partner_response = requests.get(url=get_product_on_partner_site_url, headers=headers)
            print('product_on_partner_response', product_on_partner_response)
            product_id_on_partner = False  # set to false, overwritten if id is found
            if product_on_partner_response.status_code == 404:  # product handle not found, but has been made
                print('product handle ' + json_body['handle'] + ' not found, check if it is a draft')
                get_draft_products_url = f"https://{domain_name}/admin/api/2023-10/products.json?status=draft"
                get_draft_products_response = requests.get(url=get_draft_products_url, headers=headers)
                if get_draft_products_response.status_code == 200:
                    for product in get_draft_products_response.json()['products']:
                        if product['handle'] == json_body['handle']:
                            product_id_on_partner = product['id']
                            print('draft found, passing id of draft product')

            elif product_on_partner_response.status_code == 200:  # product found, do update
                product_id_on_partner = product_on_partner_response.json()['product']['id']

            if product_id_on_partner != False:
                self.update_product_fields(product_id_on_partner, domain_name, headers, json_body)
                self.update_product_metafields(product_id_on_partner, domain_name, headers, json_body)
                self.update_product_quantity(product_id_on_partner, domain_name, headers,
                                             json_body)  # !important -> as last, other updates set inventory on 0
            elif product_id_on_partner == False:
                error_message = 'ProductUpdater: Failed to update product, handle not found and no drafts found, making new product: ' + \
                                json_body['handle'] + 'on domain: ' + domain_name
                error_handler = ErrorHandler()
                error_handler.log_error(error_message)
                creator = product_creator.ProductCreator()
                creator.create_product(json_body)

    def update_product_fields(self, product_id_on_partner, domain_name, headers, json_body):
        error_handler = ErrorHandler()
        product_id_on_partner_site = product_id_on_partner
        translator = Translator()
        translated_body = translator.translate_from_google(domain_name, json_body['body_html'])
        updated_field_data = {
            "product": {
                "id": product_id_on_partner_site,
                "title": json_body['title'],
                "body_html": translated_body,
                "status": json_body['status'],
                "tags": json_body['tags'],
                "variants": [{
                    "barcode": json_body['variants'][0]['barcode'],
                    "compare_at_price": json_body['variants'][0]['compare_at_price'],
                    "price": json_body['variants'][0]['price'],
                    "tags": json_body['variants'][0]['price'],
                    "sku": json_body['variants'][0]['sku'],
                    "grams": json_body['variants'][0]['grams'],
                    "weight": json_body['variants'][0]['weight'],
                    "weight_unit": json_body['variants'][0]['weight_unit'],
                }],
                "image": json_body['image'],
            }
        }
        images_array = []
        for i in range(0, len(json_body['images'])):
            image_dict = json_body['images'][i]
            images_array.insert(i, image_dict)
        updated_field_data['product']["images"] = images_array

        update_product_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id_on_partner_site}.json"
        update_product_on_partner_site_response = requests.put(url=update_product_on_partner_site_url, headers=headers,
                                                               json=updated_field_data)
        if update_product_on_partner_site_response.status_code != 200:
            error_message = 'ProductUpdater: Failed to update product fields, ProductID on partner site: ' + str(product_id_on_partner_site) \
                            + 'on domain: ' + domain_name + 'status code: ' + str(update_product_on_partner_site_response.status_code)
            error_handler.log_error(error_message)

    def update_product_quantity(self, product_id_on_partner, domain_name, headers, json_body):
        error_handler = ErrorHandler()
        product_id_on_partner_site = product_id_on_partner
        get_product_variant_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id_on_partner_site}/variants.json"
        product_variant_on_partner_response = requests.get(url=get_product_variant_on_partner_site_url, headers=headers)
        if product_variant_on_partner_response.status_code == 200:
            if len(json_body['variants']) == len(
                    product_variant_on_partner_response.json()['variants']) == 1:  # If no variants are known
                partner_inventory_item_id = product_variant_on_partner_response.json()['variants'][0]['inventory_item_id']
                inventory_item_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/inventory_levels/set.json"
                locations_on_partner_site_url = f"https://{domain_name}/admin/api/2023-10/locations.json"
                locations_on_partner_site_url_response = requests.get(
                    url=locations_on_partner_site_url, headers=headers)
                if locations_on_partner_site_url_response.status_code == 200:
                    updated_inventory_data = {
                        "location_id": locations_on_partner_site_url_response.json()['locations'][0]['id'],
                        "inventory_item_id": partner_inventory_item_id,
                        "available": json_body['variants'][0]['inventory_quantity'],
                    }
                    update_inventory_item_on_partner_response = requests.post(
                        url=inventory_item_on_partner_site_url, headers=headers, json=updated_inventory_data)
                    if update_inventory_item_on_partner_response.status_code != 200:
                        error_message = 'ProductUpdater: Failed to update inventory: ' + inventory_item_on_partner_site_url + 'status code: ' + str(
                            update_inventory_item_on_partner_response.status_code) + 'ProductID on partner: ' + str(product_id_on_partner_site)
                        error_handler.log_error(error_message)
                elif locations_on_partner_site_url_response.status_code != 200:
                    error_message = 'ProductUpdater: Failed to get locations of store: ' + locations_on_partner_site_url + 'status code: ' + str(
                        locations_on_partner_site_url_response.status_code)
                    error_handler.log_error(error_message)
        elif product_variant_on_partner_response.status_code != 200:
            error_message = 'ProductUpdater: Failed to get variants of productID: ' + str(product_id_on_partner) + 'status code: ' + str(
                product_variant_on_partner_response.status_code)
            error_handler.log_error(error_message)
    def update_product_metafields(self, product_id_on_partner, domain_name, headers, json_body):
        error_handler = ErrorHandler()
        translator = Translator()
        product_id_on_partner_site = product_id_on_partner
        product_id_original_site = json_body['id']
        original_headers = {"Accept": "application/json", "Content-Type": "application/json",
                            "X-Shopify-Access-Token": settings.GERIJPTEBIEREN_ACCESS_TOKEN}
        get_product_metafields_original_site_url = f"https://gerijptebieren.myshopify.com/admin/api/2023-10/products/{product_id_original_site}/metafields.json"
        get_product_metafields_original_site_response = requests.get(url=get_product_metafields_original_site_url,
                                                                     headers=original_headers)
        try:
            original_metafields = get_product_metafields_original_site_response.json()['metafields']
            for metafield in original_metafields:
                if metafield['key'] in ['rijpingsmethode', 'soort_bier', 'land_van_herkomst']:
                    translated_value = translator.translate_value_from_dict(domain_name, metafield['key'],
                                                                            metafield['value'])
                    metafield['value'] = translated_value
                payload = {"metafield": metafield}
                make_metafield_url = f"https://{domain_name}/admin/api/2023-10/products/{product_id_on_partner_site}/metafields.json"
                post_metafields_partner_site_response = requests.post(url=make_metafield_url, headers=headers,
                                                                      json=payload)
                print('Metafields of object updated', post_metafields_partner_site_response)
        except Exception:
            print('no metafields found')
            error_message = 'ProductUpdater: no metafields found, ProductID on original: ' + str(product_id_original_site) + 'status code: ' + str(
                get_product_metafields_original_site_response.status_code)
            error_handler.log_error(error_message)
