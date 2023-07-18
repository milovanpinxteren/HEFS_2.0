from datetime import datetime

import requests
from django.conf import settings

from hefs.models import Orders, NewOrders, VerzendOpties, Orderline


class Kerstdiner2023API:
    def __init__(self):
        self.get_shopify_orders()

    def get_shopify_orders(self):
        shopify_access_token = settings.SHOPIFY_ACCESS_TOKEN
        headers = {"Accept": "application/json", "Content-Type": "application/json",
                   "X-Shopify-Access-Token": shopify_access_token}
        response = requests.get(url="https://d36867-2.myshopify.com/admin/api/2023-04/orders.json", headers=headers)
        if response.status_code == 200:
            orders = response.json()["orders"]
            self.handle_shopify_orders(orders)
        else:
            print("Failed to retrieve orders. Status code:", response.status_code)
            return []

    def handle_shopify_orders(self, orders):
        for order in orders:
            if '#' in order['name']:
                order['name'] = order['name'].replace('#', '9')
            conversieID = order['name']  # get OrderID, and check if OrderID already exists.
            existing_order = Orders.objects.filter(conversieID=conversieID)
            existing_new_order = NewOrders.objects.filter(conversieID=conversieID)
            if existing_order or existing_new_order:
                self.detect_changes(order, existing_order, existing_new_order)
            else:
                print('ADD TO NEWORDERS')
                self.add_to_new_orders(order)

    #TODO: test this!
    def detect_changes(self, order, existing_order, existing_new_order):
        shopify_order_lines = []
        shopify_order_quantities = []

        for existingOrderLine in order['line_items']:
            shopify_order_lines = shopify_order_lines.append(existingOrderLine['sku'])
            shopify_order_quantities = shopify_order_quantities.append(existingOrderLine['fulfillable_quantity'])

        if existing_order:
            orderID = existing_order.values_list("id", flat=True)[0]
            hefs_order_quantity = sum(Orderline.objects.filter(order=orderID).values_list("aantal", flat=True))
            if hefs_order_quantity != sum(shopify_order_quantities):
                Orders.objects.filter(order=existing_order.values_list("id", flat=True)[0]).delete()
                #TODO does this also delete orderlines?
                self.add_to_new_orders(order)
            else:  # if quantities are the same, check if all the productSKU's are the same
                hefs_order_lines = list(Orderline.objects.filter(order=orderID).values_list("productSKU", flat=True))
                res_order = [x for x in hefs_order_lines + shopify_order_lines if
                             x not in hefs_order_lines or x not in shopify_order_lines]
                if res_order:  # difference in productSKU's in order
                    Orders.objects.filter(order=orderID).delete()
                    self.add_to_new_orders(order)

        if existing_new_order:
            hefs_neworder_quantity = sum(existing_new_order.values_list("aantal", flat=True))
            if hefs_neworder_quantity != sum(shopify_order_quantities):
                NewOrders.objects.filter(conversieID=order['name']).delete()
                self.add_to_new_orders(order)
            else:
                hefs_neworder_lines = list(existing_new_order.values_list("productSKU", flat=True))
                res_new_order = [x for x in hefs_neworder_lines + shopify_order_lines if
                                 x not in hefs_neworder_lines or x not in shopify_order_lines]
                if res_new_order: # difference in productSKU's in order
                    NewOrders.objects.filter(conversieID=order['name']).delete()
                    self.add_to_new_orders(order)

    def add_to_new_orders(self, order):
        verzendoptie = VerzendOpties.objects.filter(verzendoptie=order['shipping_lines'][0]['code'])[0]
        besteldatum = datetime.strptime(order['created_at'][:9], '%Y-%m-%d')
        for newOrderLine in order['line_items']:
            if newOrderLine['fulfillable_quantity'] > 0:
                NewOrders.objects.create(conversieID=order['name'],
                                         besteldatum=besteldatum,
                                         verzendoptie=verzendoptie,
                                         afleverdatum=verzendoptie.verzenddatum,
                                         aflevertijd='00:00:00',
                                         verzendkosten=float(verzendoptie.verzendkosten),
                                         korting=float(order['total_discounts']),
                                         orderprijs=order['current_subtotal_price'],
                                         totaal=float(order['current_total_price']),
                                         aantal=int(newOrderLine['quantity']),
                                         product=newOrderLine['name'],
                                         productSKU=newOrderLine['sku'],
                                         voornaam=order['shipping_address']['first_name'],
                                         achternaam=order['shipping_address']['last_name'],
                                         emailadres=order['contact_email'],
                                         telefoonnummer=order['shipping_address']['phone'],
                                         straatnaam=order['shipping_address']['address1'],
                                         huisnummer=order['shipping_address']['address2'],
                                         postcode=order['shipping_address']['zip'],
                                         plaats=order['shipping_address']['city'],
                                         land=order['shipping_address']['country'],
                                         postadres_straatnaam=order['billing_address']['address1'],
                                         postadres_huisnummer=order['billing_address']['address2'],
                                         postadres_postcode=order['billing_address']['zip'],
                                         postadres_plaats=order['billing_address']['city'],
                                         postadres_land=order['billing_address']['country'],
                                         opmerkingen=order['customer']['note'])
