import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Q
import re

from hefs.apis.hobApi import HobAPI
from hefs.classes.shopify.graphql_inventory_updater import GraphQLInventoryUpdater
from hefs.classes.shopify_sync.graphql_queries.all_products_getter import AllProductsGetter
from hefs.classes.shopify_sync.product_creator import ProductCreator
from hefs.models import SyncInfo


class SyncTableUpdater:
    def __init__(self):
        self.hob_access_token = settings.HOB_ACCESS_TOKEN
        self.untappd_token = settings.UNTAPPD_TOKEN
        self.all_product_getter = AllProductsGetter()
        self.product_creator = ProductCreator()
        self.inventory_updater = GraphQLInventoryUpdater()
        self.hob_api = HobAPI()
        self.locations = {'7c70bf.myshopify.com': "gid://shopify/Location/89627787602", }
        print('updating table')
        return

    def start_full_sync(self):
        print('starting full sync')
        # self.hob_api.get_shopify_orders()

        # FLOW:
        # - Get all products from House of Beers
        all_products = self.all_product_getter.get_all_products()
        # - Update the hob-related info in the SyncInfo Database model
        self.update_hob_info(all_products)
        self.update_untappd()

        return True

    def update_hob_info(self, all_products):
        for product in all_products:
            id = product['id']
            title = product['title']
            handle = product['handle']
            total_inventory = product['totalInventory']
            variant_id = product['variants']['edges'][0]['node']['id']
            inventory_id = product['variants']['edges'][0]['node']['inventoryItem']['id']
            variant_price = product['variants']['edges'][0]['node']['price']
            statiegeld_value = 0
            for tag in product['tags']:
                if 'Statiegeld' in tag:
                    # Use regular expression to find a number after 'Statiegeld'
                    match = re.search(r'Statiegeld:\s*(\d+\.\d+)', tag)
                    if match:
                        statiegeld_value = float(match.group(1))

            sync_info, created = SyncInfo.objects.get_or_create(
                hob_id=id,
                defaults={
                    'hob_product_title': title,
                    'hob_product_handle': handle,
                    'quantity': total_inventory,
                    'hob_variant_id': variant_id,
                    'hob_inventory_id': inventory_id,
                    'hob_price': variant_price,
                    'deposit_money': statiegeld_value,
                }
            )

            if created:
                sync_info.untappd_id = self.get_untappd(title)
                sync_info.save()
            else:
                sync_info.hob_product_title = title
                sync_info.hob_product_handle = handle
                sync_info.quantity = total_inventory
                sync_info.hob_variant_id = variant_id
                sync_info.hob_inventory_id = inventory_id
                sync_info.hob_price = variant_price
                sync_info.deposit_money = statiegeld_value

                # Only set untappd_id if it is currently None.
                if sync_info.untappd_id is None:
                    sync_info.untappd_id = self.get_untappd(title)

                sync_info.save()

        return

    def get_untappd(self, title):
        untappd_id = None
        words = ['atiegeld', 'Cadeau', 'adeau', 'akket']
        if not any(word in title for word in words):
            trimmed_title = self.trim_title(title)
            found_untappd_beer = self.get_beer_from_untappd(trimmed_title)
            if found_untappd_beer:
                print(found_untappd_beer)
                untappd_id = found_untappd_beer
                # add_item_to_section(found_untappd_beer)
            else:
                tried_counter = 0
                found_beer = False
                while tried_counter < 2 and not found_beer:
                    tried_counter += 1
                    trimmed_title = self.simplify_beer_name(trimmed_title)
                    if len(trimmed_title) > 2:
                        found_untappd_beer = self.get_beer_from_untappd(trimmed_title)
                        if found_untappd_beer:
                            found_beer = True
                            print(f'Found after {tried_counter} tries {trimmed_title}')
                            untappd_id = found_untappd_beer
                            # add_item_to_section(found_untappd_beer)
        return untappd_id

    def simplify_beer_name(self, beer):
        if len(beer) > 1:
            if beer.endswith(' '):
                new_beer = beer[:-1]
            elif bool(re.search(r'\d{4}$', beer)):  # if beer ends in year
                new_beer = beer[:-5]
            else:  # remove the last word
                new_beer = ' '.join(beer.split()[:-1])
            return new_beer
        else:
            return False

    def get_beer_from_untappd(self, beer):
        beer_query = beer.replace(' ', '+')
        untappd_url = f'https://untappd.com/search?q={beer_query}'
        untappd_headers = {
            "Accept": "application/json", "Content-Type": "application/json",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url=untappd_url, headers=untappd_headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            beer_items = soup.find_all('div', class_='beer-item')

            if len(beer_items) > 0:
                beer = beer_items[0]
                first_anchor = beer.find('a')
                # Extract the href attribute from the anchor tag
                if first_anchor:
                    href = first_anchor.get('href')
                    # print(f"First href within beer-item: {beer_query}")
                    beer_id = int(href.replace('/beer/', ''))
                    return beer_id
                else:
                    print("No href found within beer-item", beer)
                    return False
            elif len(beer_items) == 0:
                print('no beer on untappd found for ', beer_query)
                return False
        else:
            print("Error fetching beer information from Untappd:", response.status_code)
            return False

    def trim_title(self, title):
        if title.endswith('37.5 CL'):
            title = title[:-10]
        if title.endswith('CL') or title.endswith('1.5 L') and not title.endswith('37.5 CL'):
            title = title[:-8]
        elif title.endswith('(1 pint)'):
            title = title[:-19]
        elif title.endswith('1 L') or title.endswith('3 L') or title.endswith('5 L'):
            title = title[:-4]
        elif title.endswith('fust'):
            title = title[:-11]
        title = title.replace('zonder doos', '').replace('met doos', '').replace('met koker', '').replace(
            'Met Koker', '').replace(' - ', '').replace('met doos', '').replace('met kistje', '').replace('Met kistje',
                                                                                                          '').replace(
            'zonder kistje', '').replace('Zonder kistje', '')
        return title

    def update_untappd(self):
        products = SyncInfo.objects.filter(untappd_id__isnull=False, quantity__gt=0)
        for product in products:
            self.add_item_to_section(product.untappd_id)

        products = SyncInfo.objects.filter(untappd_id__isnull=False, quantity__lte=0)
        for product in products:
            self.remove_item_from_section(product.untappd_id)

    def add_item_to_section(self, untappd_id):
        token = self.untappd_token
        url = "https://business.untappd.com/api/v1/sections/1598904/items"
        payload = {"untappd_id": untappd_id, "unique": True, "full": True, "default_containers": True}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + token
        }
        response = requests.post(url, headers=headers, json=payload)
        # Optionally, check for errors
        if response.ok:
            print("Item added successfully:")
            return True
        else:
            print("Failed to add item:", response.status_code, response.text)
            return False

    def remove_item_from_section(self, untappd_id):
        token = self.untappd_token
        url = "https://business.untappd.com/api/v1/sections/1598904/items"
        payload = {"untappd_id": untappd_id, "unique": True, "full": True, "default_containers": True}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + token
        }
        response = requests.delete(url, headers=headers, json=payload)
        if response.ok:
            print("Item deleted successfully:")
            return True
        else:
            print("Failed to delete item:", response.status_code, response.text)
            return False
