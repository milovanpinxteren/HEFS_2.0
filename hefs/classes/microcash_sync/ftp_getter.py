import os
import tempfile
from ftplib import FTP

from hefs.classes.error_handler import ErrorHandler
from hefs.classes.shopify.inventory_updater import InventoryUpdater
from hefs.classes.shopify.info_getter import InfoGetter
from hefs.classes.shopify.product_checker import ProductChecker
from hefs.classes.shopify.product_maker import ProductMaker
from hefs.classes.shopify.product_updater import ProductUpdater

from django.conf import settings


class FTPGetter:
    def __init__(self):
        # 7c70bf.myshopify.com is HouseOfBeers
        self.websites = {'7c70bf.myshopify.com': settings.HOB_ACCESS_TOKEN,
                         'gerijptebieren.myshopify.com': settings.GERIJPTEBIEREN_ACCESS_TOKEN}  # add domains here
        self.locations = {'7c70bf.myshopify.com': 89627787602, 'gerijptebieren.myshopify.com': 73763651849}

        self.column_names = []
        self.info_getter = InfoGetter()
        self.inventory_updater = InventoryUpdater()
        self.product_checker = ProductChecker()
        self.product_updater = ProductUpdater()
        self.product_maker = ProductMaker()
        self.error_handler = ErrorHandler()
        self.host = '86.88.43.117'
        self.port = 21
        self.username = 'Webshop'
        self.password = settings.MICROCASH_FTP_PASSWORD
        self.corrected_price_of_items = 0
        self.corrected_inventory_of_items = 0
        self.created_items = 0

        # self.open_test_file()

    def callback(self, line, sync_function):
        if not hasattr(self, 'first_line_skipped'):
            self.first_line_skipped = False
        if self.first_line_skipped:
            sync_function(line)
        else:
            self.first_line_skipped = True
            self.column_names = line.strip().split('\t')
            try:
                self.shopifyID_index = self.column_names.index("Shopify ID")
                self.sales_price_index = self.column_names.index("Verkoopprijs")
                self.inventory_index = self.column_names.index("Voorraad")
            except ValueError:
                self.shopifyID_index = self.column_names.index("Barcode")
                self.inventory_index = self.column_names.index("Voorraad")

    def get_ftp_changed_file(self):
        try:
            with FTP(self.host) as ftp:
                print('connecting with ftp for inventory changed file')
                ftp.connect(self.host, self.port)
                ftp.login(self.username, self.password)
                print('logged in')
                files = ftp.nlst()

                for file in files:
                    if file == 'WEB_mcVrdExp.txt':
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            ftp.retrbinary('RETR ' + file, temp_file.write)
                            temp_file_path = temp_file.name
                ftp.quit()
                print('found inventory changes file')
                self.process_file(temp_file_path, self.get_changed_inventory)
                print('removing file path')
                self.error_handler.log_error('CHANGE SYNC DONE, PRICE CORRECTED, INVENTORY CORRECTED, ITEMS CREATED ' + str(
                    self.corrected_price_of_items) + str(self.corrected_inventory_of_items) + str(
                    self.created_items))
                os.remove(temp_file_path)
                # ftp.retrlines('RETR ' + file, callback=lambda line: self.callback(line.strip(), self.get_changed_inventory))
        except Exception as e:
            print(e)
            self.error_handler.log_error('ERROR IN get_ftp_changed_file ', e)

    def get_ftp_full_file(self):
        try:
            with FTP(self.host) as ftp:
                ftp.connect(self.host, self.port)
                ftp.login(self.username, self.password)
                files = ftp.nlst()
                print('connected for full file')

                for file in files:
                    if file == 'WEB_mcArtExp.txt':
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            ftp.retrbinary('RETR ' + file, temp_file.write)
                            temp_file_path = temp_file.name
                ftp.quit()
                print('found full sync file')
                self.process_file(temp_file_path, self.sync_product)
                print('removing file path')
                self.error_handler.log_error('FULL SYNC DONE, PRICE CORRECTED, INVENTORY CORRECTED, ITEMS CREATED ' + str(
                    self.corrected_price_of_items) + str(self.corrected_inventory_of_items) + str(
                    self.created_items))
                os.remove(temp_file_path)
        except Exception as e:
            print(e)
            self.error_handler.log_error('ERROR IN GET_FTP_FULL_FILE ', e)

    # def open_test_file(self):
    #     file = 'WEB_mcVrdExp.txt'
    #     local_file_path = "C:/Downloads/" + file
    #     with open(local_file_path, 'r') as local_file:
    #         for line in local_file:
    #             print(line)
    #             self.callback(line, self.get_changed_inventory)

    def process_file(self, file_path, sync_function):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    self.callback(line.strip(), sync_function)
        except Exception as e:
            print(e)

    def sync_product(self, row):
        try:
            data = row.strip().split('\t')
            # self.error_handler.log_error('Updating product ' + data[0])
            shopifyID = data[self.shopifyID_index]
            price = data[self.sales_price_index]
            inventory_quantity = data[self.inventory_index]
            product_handle = self.info_getter.get_product_handle(shopifyID)
            for domain_name, token in self.websites.items():
                headers = {"Accept": "application/json", "Content-Type": "application/json",
                           "X-Shopify-Access-Token": token}
                existment_response = self.product_checker.check_existment_from_handle(domain_name, product_handle,
                                                                                      headers)
                if existment_response:
                    product_id = existment_response['product']['id']
                    variant_id = existment_response['product']['variants'][0]['id']
                    inventory_item_id = self.info_getter.get_inventory_item_id(product_id, domain_name, headers)
                    price_correct = self.product_checker.check_price(existment_response, price)
                    if not price_correct:
                        # self.error_handler.log_error('Price incorrect, updating ' + product_handle + domain_name)
                        self.product_updater.update_price(domain_name, headers, product_id, variant_id, price)
                        self.corrected_price_of_items += 1
                    inventory_correct = self.product_checker.check_inventory(domain_name, headers, product_id,
                                                                             inventory_quantity)
                    if not inventory_correct:
                        # self.error_handler.log_error('Inventory incorrect, updating ' + product_handle + domain_name)
                        location_id = self.locations[domain_name]
                        inventory_updated = self.product_updater.update_inventory(domain_name, headers,
                                                                                  inventory_item_id, inventory_quantity,
                                                                                  location_id)
                        self.corrected_inventory_of_items += 1
                        if not inventory_updated:
                            self.error_handler.log_error('Inventory not updated ' + product_handle + domain_name)
                else:
                    # self.error_handler.log_error('Product not found, creating ' + product_handle + domain_name)
                    try:
                        product_created = self.product_maker.create_product(shopifyID, domain_name, headers)
                        self.created_items += 1
                        if not product_created[0]:
                            self.error_handler.log_error(
                                'Could not create product ' + product_handle + domain_name + str(product_created[1]))
                    except Exception as e:
                        print(e)
                        self.error_handler.log_error('Could not create product ' + product_handle + domain_name)
        except Exception as e:
            print(e)
            self.error_handler.log_error('Could not check product ' + row)
        return

    def get_changed_inventory(self, row):
        # row = "8763716796754\t69"  # was 24
        print('inventory changed row: ', row)
        hoBproductID, inventory_quantity = row.split("\t")
        product_handle = self.info_getter.get_product_handle(hoBproductID)
        print('handle:', product_handle)
        self.inventory_updater.update_product_quantity(self.websites, self.locations, hoBproductID, product_handle,
                                                       inventory_quantity)


get_ftp = FTPGetter()
