from datetime import datetime
import requests



from hefs.models import Orders, NewOrders, VerzendOpties


class Kerstdiner2023API:
    def __init__(self):
        self.get_shopify_orders()

    def get_shopify_orders(self):
        shopify_access_token = "dameugdeniewete"
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
            print(order)
            orderID = order['id'] #get OrderID, and check if OrderID already exists.
            existing_order = Orders.objects.filter(pk=orderID)
            if existing_order:
                print('BESTAAT')
                # If it exists, check if contents/dishes are still the same
                # If this is FALSE, delete the order, add new order to Neworders
                # If it's still the same, do nothing (don't add to neworders)
            else:
                print('ADD TO NEWORDERS')
                #financial_status
                if '#' in order['name']:
                    order['name'] = order['name'].replace('#', '9')
                verzendoptie = VerzendOpties.objects.filter(verzendoptie=order['shipping_lines'][0]['code'])[0]
                besteldatum = datetime.strptime(order['created_at'][:9], '%Y-%m-%d')
                for newOrderLine in order['line_items']:
                    NewOrders.objects.create(conversieID=order['name'],
                                             besteldatum=besteldatum,
                                             verzendoptie=verzendoptie,
                                             afleverdatum='2023-07-17 17:37:05',
                                             aflevertijd='17:00:00',
                                             verzendkosten=float(verzendoptie.verzendkosten),
                                             korting=float(order['total_discounts']),
                                             orderprijs=order['current_subtotal_price'],
                                             totaal=float(order['current_total_price']),
                                             aantal=int(newOrderLine['quantity']),
                                             product=newOrderLine['name'],
                                             productSKU=newOrderLine['sku'],
                                             # organisatieID=order['created_at'],
                                             # organisatienaam=order['created_at'],
                                             voornaam=order['shipping_address']['first_name'],
                                             achternaam=order['shipping_address']['last_name'],
                                             # tussenvoegsel=order['created_at'],
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
                                             opmerkingen=order['customer']['note']
                                             )





