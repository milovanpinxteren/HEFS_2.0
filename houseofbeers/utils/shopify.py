import time
from django.conf import settings
import requests

def get_shopify_orders(start_date, end_date):
    access_token = settings.HOB_ACCESS_TOKEN
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }

    query = """
    query($cursor: String, $query: String!) {
        orders(first: 150, after: $cursor, query: $query) {
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
                    paymentGatewayNames
                    channelInformation {
                        channelDefinition {
                            channelName
                            subChannelName
                        }
                    }
                    totalDiscountsSet { shopMoney { amount } }
                    subtotalPriceSet { shopMoney { amount } }
                    totalPriceSet { shopMoney { amount } }
                    shippingLine {
                        code
                        title
                        originalPriceSet { shopMoney { amount } }
                    }
                    customer { note }
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
                                        edges { node { price } }
                                    }
                                }
                            }
                        }
                    }
                    shippingAddress {
                        firstName lastName address1 address2 phone city zip country
                    }
                    billingAddress {
                        address1 address2 zip city country
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

    # Format: ISO 8601 with time and Zulu (UTC)
    start_str = f"{start_date}T00:00:00Z"
    end_str = f"{end_date}T23:59:59Z"
    query_filter = f"created_at:>={start_str} AND created_at:<={end_str}"

    variables = {"cursor": None, "query": query_filter}
    orders = []

    while True:
        time.sleep(0.3)
        response = requests.post(
            url="https://7c70bf.myshopify.com/admin/api/2024-01/graphql.json",
            headers=headers,
            json={"query": query, "variables": variables}
        )

        if response.status_code == 200:
            data = response.json()
            try:
                orders_data = data['data']['orders']['edges']
                orders.extend([edge['node'] for edge in orders_data])
                page_info = data['data']['orders']['pageInfo']
                if page_info['hasNextPage']:
                    variables['cursor'] = page_info['endCursor']
                else:
                    break
            except KeyError:
                print('API error or unexpected structure:', data)
                break
        else:
            print("Failed to retrieve orders. Status code:", response.status_code)
            break

    return orders
