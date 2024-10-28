import time
from datetime import datetime, timedelta
import requests
from django.conf import settings
from hefs.models import Orders, NewOrders, VerzendOpties, Orderline, AlgemeneInformatie
from django.utils import timezone


class Kerstdiner2024API:
    def __init__(self):
        self.get_shopify_orders()

    def get_shopify_orders(self):
        shopify_access_token = settings.KERSTDINER_ACCESS_TOKEN
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": shopify_access_token
        }

        query = """
        query($cursor: String) {
            orders(first: 50, after: $cursor, query: "created_at:>=2024-09-01T00:00:00Z") {
                edges {
                    cursor
                    node {
                        id
                        name
                        createdAt
                        email
                        updatedAt
                        discountCodes
                        totalDiscountsSet {
                            shopMoney {
                                amount
                            }
                        }
                        subtotalPriceSet {
                            shopMoney {
                                amount
                            }
                        }
                        totalPriceSet {
                            shopMoney {
                                amount
                            }
                        }
                        shippingLine {
                            code
                            title
                        }
                        customer {
                            note
                        }
                        lineItems(first: 50) {
                            edges {
                                node {
                                    sku
                                    quantity
                                    fulfillableQuantity
                                    name
                                }
                            }
                        }
                        shippingAddress {
                            firstName
                            lastName
                            address1
                            address2
                            phone
                            city
                            zip
                            country
                        }
                        billingAddress {
                            address1
                            address2
                            zip
                            city
                            country
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """

        variables = {"cursor": None}
        orders = []

        while True:
            response = requests.post(
                url="https://d36867-2.myshopify.com/admin/api/2023-07/graphql.json",
                headers=headers,
                json={"query": query, "variables": variables}
            )

            if response.status_code == 200:
                data = response.json()
                orders_data = data['data']['orders']['edges']
                orders.extend([edge['node'] for edge in orders_data])

                self.handle_shopify_orders(orders)

                # Pagination handling
                page_info = data['data']['orders']['pageInfo']
                if page_info['hasNextPage']:
                    variables['cursor'] = page_info['endCursor']
                else:
                    break
            else:
                print("Failed to retrieve orders. Status code:", response.status_code)
                return []

    def handle_shopify_orders(self, orders):
        last_api_call = AlgemeneInformatie.objects.get(naam='lastApiCall')
        last_api_call_date = datetime.fromtimestamp(last_api_call.waarde)
        for order in orders:
            conversieID = order['name']
            created_at = order['createdAt']
            updated_at = order['updatedAt']

            if created_at != updated_at:  # Order was updated
                existing_order = Orders.objects.filter(conversieID=conversieID)
                existing_new_order = NewOrders.objects.filter(conversieID=conversieID)
                if not existing_order and not existing_new_order:
                    print('order does not exist, adding')
                    self.add_to_new_orders(order)
                    # self.handle_coupons(order)
                else:
                    updated_at_date = datetime.strptime(updated_at[:10], '%Y-%m-%d')
                    if updated_at_date > (last_api_call_date - timedelta(days=1)):
                        print('order changed', conversieID)
                        Orders.objects.filter(conversieID=conversieID).delete()
                        NewOrders.objects.filter(conversieID=conversieID).delete()
                        self.add_to_new_orders(order)
                        # self.handle_coupons(order)
                    else:
                        print('order change already handled', conversieID)
            elif created_at == updated_at:
                existing_order = Orders.objects.filter(conversieID=conversieID)
                existing_new_order = NewOrders.objects.filter(conversieID=conversieID)
                if not existing_order and not existing_new_order:
                    print('order does not exist, adding')
                    self.add_to_new_orders(order)
                    # self.handle_coupons(order)
                else:
                    print("order exists and not alternated", conversieID)
        last_api_call.waarde = time.time()
        last_api_call.save()

    # Add the rest of your methods (add_to_new_orders, handle_coupons, etc.) here
    def add_to_new_orders(self, order):
        try:
            try:
                verzendoptie = VerzendOpties.objects.filter(verzendoptie=order['shippingLine']['code'])[0]
            except IndexError:
                verzendoptie = VerzendOpties.objects.filter(verzendoptie=order['shippingLine']['title'])[0]

            besteldatum = datetime.strptime(order['createdAt'][:10], '%Y-%m-%d')
            tz = timezone.get_current_timezone()
            timzone_besteldatum = timezone.make_aware(besteldatum, tz, True)

            for newOrderLine in order['lineItems']['edges']:
                newOrderLine = newOrderLine['node']
                if int(newOrderLine['fulfillableQuantity']) > 0:
                    print(order['name'])
                    NewOrders.objects.create(conversieID=order['name'],
                                             besteldatum=timzone_besteldatum,
                                             verzendoptie=verzendoptie,
                                             afleverdatum=verzendoptie.verzenddatum,
                                             aflevertijd='00:00:00',
                                             verzendkosten=float(verzendoptie.verzendkosten),
                                             korting=float(order['totalDiscountsSet']['shopMoney']['amount']),
                                             orderprijs=order['subtotalPriceSet']['shopMoney']['amount'],
                                             totaal=float(order['totalPriceSet']['shopMoney']['amount']),
                                             aantal=int(newOrderLine['quantity']),
                                             product=newOrderLine['name'],
                                             productSKU=newOrderLine['sku'],
                                             voornaam=order['shippingAddress']['firstName'],
                                             achternaam=order['shippingAddress']['lastName'],
                                             emailadres=order['email'],
                                             telefoonnummer=order['shippingAddress']['phone'],
                                             straatnaam=order['shippingAddress']['address1'],
                                             huisnummer=order['shippingAddress']['address2'],
                                             postcode=order['shippingAddress']['zip'],
                                             plaats=order['shippingAddress']['city'],
                                             land=order['shippingAddress']['country'],
                                             postadres_straatnaam=order['billingAddress']['address1'],
                                             postadres_huisnummer=order['billingAddress']['address2'],
                                             postadres_postcode=order['billingAddress']['zip'],
                                             postadres_plaats=order['billingAddress']['city'],
                                             postadres_land=order['billingAddress']['country'],
                                             opmerkingen=order['customer']['note'])
        except Exception as e:
            print('Adding to neworders error', e)
