import requests
import json

from django.conf import settings


class Paasontbijt2024Transacties:

    def __init__(self):
        self.access_token = settings.PAASONTBIJT_ACCESS_TOKEN
        self.graphql_endpoint = f'https://b88885-3.myshopify.com/admin/api/2021-10/graphql.json'

    def fetch_orders(self):
        query = """
        query FetchOrders($first: Int!, $after: String) {
          orders(first: $first, after: $after) {
            edges {
              node {
                id
                name
                cancelledAt
                confirmed
                totalPriceSet {
                  shopMoney {
                    amount
                  }
                }
                shippingLine {
                  price
                }
                transactions(first: 10) {
                    amountSet {
                      shopMoney {
                        amount
                      }
                    }
                    fees {
                    amount {
                        amount
                    }
                    }
                    receiptJson
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


        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }

        orders = []
        has_next_page = True
        end_cursor = None
        while has_next_page:
            variables = {"first": 250}
            if end_cursor:
                variables["after"] = end_cursor
            response = requests.post(self.graphql_endpoint, json={'query': query, 'variables': variables},
                                     headers=headers)
            data = json.loads(response.text)
            orders += data['data']['orders']['edges']
            has_next_page = data['data']['orders']['pageInfo']['hasNextPage']
            if has_next_page:
                end_cursor = data['data']['orders']['pageInfo']['endCursor']

        return orders

    def extract_order_details(self, order):
        node = order['node']
        order_conversie_id = node['name']
        total_payment = node['totalPriceSet']['shopMoney']['amount']
        try:
            shipping_cost = node['shippingLine']['price']
        except Exception as e:
            shipping_cost = 0
        # Calculate transaction cost
        transaction_cost = 0
        try:
            transactions = node['transactions']
            for transaction in transactions:
                transaction_cost += float(transaction['fees'][0]['amount']['amount'])
        except Exception as e:
            transaction_cost = 0
        return {
            'order_conversie_id': order_conversie_id,
            'total_payment': total_payment,
            'shipping_cost': shipping_cost,
            'transaction_cost': transaction_cost
        }

    def fetch_and_print_orders(self):
        orders = self.fetch_orders()
        orders_matrix = []
        for order in orders:
            if order['node']['cancelledAt'] == None and order['node']['confirmed'] == True:
                order_details = self.extract_order_details(order)
                orders_matrix.append([order_details['order_conversie_id'], order_details['total_payment'],
                                      order_details['shipping_cost'], order_details['transaction_cost']
                                      ])
        return orders_matrix
