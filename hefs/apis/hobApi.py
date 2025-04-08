import time
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.utils import timezone

from hefs.models import Orders, NewOrders, VerzendOpties, AlgemeneInformatie, HobOrders, HobOrderProducts


class HobAPI:
    def __init__(self):
        HobOrders.objects.all().delete()
        self.get_shopify_orders()

    def get_shopify_orders(self):
        shopify_access_token = settings.HOB_ACCESS_TOKEN
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": shopify_access_token
        }

        query = """
        query($cursor: String) {
            orders(first: 150, after: $cursor, query: "created_at:>=2022-09-01T00:00:00Z") {
                edges {
                    cursor
                    node {
                        id
                        name
                        createdAt
                        email
                        updatedAt
                        discountCodes
                        note
                        channelInformation {
                            channelDefinition {
                                channelName
                                subChannelName
                            }
                        }
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
                            originalPriceSet {
                                shopMoney {
                                    amount
                                }
                            }
                        }
                        customer {
                            note
                        }
                        lineItems(first: 150) {
                          edges {
                            node {
                              id
                              quantity
                              fulfillableQuantity
                              name
                              product {
                                id
                                tags
                                variants(first: 1) {
                                    edges {
                                        node {
                                            price
                                        }
                                    }
                                }
                              }
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
            time.sleep(0.2)
            response = requests.post(
                url="https://7c70bf.myshopify.com/admin/api/2024-01/graphql.json",
                headers=headers,
                json={"query": query, "variables": variables}
            )

            if response.status_code == 200:
                data = response.json()
                try:
                    orders_data = data['data']['orders']['edges']
                except KeyError:
                    print('api error')
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

        for order in orders:
            name = order['name']
            existing_order = HobOrders.objects.filter(name=name)
            if not existing_order:
                print('order does not exist, adding')
                self.add_to_new_orders(order)

    # Add the rest of your methods (add_to_new_orders, handle_coupons, etc.) here
    def add_to_new_orders(self, order):
        # try:
        if order['shippingLine']:
            try:
                verzendkosten = order['shippingLine']['originalPriceSet']['shopMoney']['amount']
                voornaam = order['shippingAddress']['firstName']
                achternaam = order['shippingAddress']['lastName']
                telefoonnummer = order['shippingAddress']['phone']
                straatnaam = order['shippingAddress']['address1']
                huisnummer = order['shippingAddress']['address2']
                postcode = order['shippingAddress']['zip']
                plaats = order['shippingAddress']['city']
                land = order['shippingAddress']['country']
            except (KeyError, TypeError):
                verzendkosten = 0
                try:
                    voornaam = 'Onbekend'
                    achternaam = 'Onbekend'
                    telefoonnummer = ''
                    straatnaam = order['billingAddress']['address1']
                    huisnummer = order['billingAddress']['address2']
                    postcode = order['billingAddress']['zip']
                    plaats = order['billingAddress']['city']
                    land = order['billingAddress']['country']
                except KeyError:
                    print('error')

            emailadres = order['email']
        else:
            verzendkosten = 0
            voornaam = 'House'
            achternaam = 'Of Beers'
            emailadres = 'info@houseofbeers.nl'
            telefoonnummer = ''
            straatnaam = 'Prior van Millstraat'
            huisnummer = '2'
            postcode = '5402GH'
            plaats = 'Uden'
            land = 'Nederland'
        try:
            sales_channel = order['channelInformation']['channelDefinition']['channelName']
        except TypeError:
            sales_channel = 'manual'
        besteldatum = datetime.strptime(order['createdAt'][:10], '%Y-%m-%d')
        hob_order = HobOrders.objects.create(name=order['name'],
                                             shopifyID=order['id'],
                                             sales_channel=sales_channel,
                                             besteldatum=besteldatum,
                                             verzendkosten=verzendkosten,
                                             korting=float(order['totalDiscountsSet']['shopMoney']['amount']),
                                             orderprijs=order['subtotalPriceSet']['shopMoney']['amount'],
                                             voornaam=voornaam,
                                             achternaam=achternaam,
                                             emailadres=emailadres,
                                             telefoonnummer=telefoonnummer,
                                             straatnaam=straatnaam,
                                             huisnummer=huisnummer,
                                             postcode=postcode,
                                             plaats=plaats,
                                             land=land,
                                             opmerkingen=order['note'])
        for orderline in order['lineItems']['edges']:
            product_name = orderline['node']['name']
            try:
                orderline['node']['product']['tags']
                product_tags = orderline['node']['product']['tags']
                product_tags_str = ",".join(product_tags)
                price = float(orderline['node']['product']['variants']['edges'][0]['node']['price'])
            except TypeError:
                product_tags_str = ''
                price = 0
            try:
                product_id = orderline['node']['product']['id']
            except TypeError:
                product_id = None
            quantity = orderline['node']['quantity']

            # if 'atiegeld' not in product_name:
            HobOrderProducts.objects.create(productname=product_name, hoborder=hob_order, aantal=quantity,
                                            productid=product_id, product_tags=product_tags_str, price=price)
    # except Exception as e:
    #     print('Adding to neworders error', e)
