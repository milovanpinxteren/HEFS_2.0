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
                    totalRefundedSet {
                      shopMoney {
                        amount
                      }
                    }
                    paymentGatewayNames
                    channelInformation {
                        channelDefinition {
                            channelName
                            subChannelName
                        }
                    }
                    currentSubtotalPriceSet { shopMoney { amount } }
                    totalShippingPriceSet {
                      shopMoney {
                        amount
                      }
                    }
                    totalRefundedSet {
                      shopMoney {
                        amount
                      }
                    }
                    lineItems(first: 100) {
                        edges {
                            node {
                                id
                                quantity
                                discountedUnitPriceSet {
                                  shopMoney {
                                    amount
                                  }
                                }
                                product {
                                    id
                                    title
                                    tags
                                    variants(first: 2) {
                                        edges { node { price } }
                                    }
                                }
                            }
                        }
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
        response = requests.post(
            url="https://7c70bf.myshopify.com/admin/api/2024-01/graphql.json",
            headers=headers,
            json={"query": query, "variables": variables},
            timeout=30  # seconds

        )

        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                error_messages = [error['message'] for error in data['errors']]
                if any('Throttled' in msg for msg in error_messages):
                    print("Throttled: waiting before retry...")
                    time.sleep(1.3)  # Simple backoff, or dynamically calculate if needed
                    continue  # Retry same request after waiting
                else:
                    print("API error:", data['errors'])
                    break  # Stop on other errors
            throttle_status = data.get('extensions', {}).get('cost', {}).get('throttleStatus', {})
            available = throttle_status.get('currentlyAvailable', 1000)
            restore_rate = throttle_status.get('restoreRate', 100)

            if available < 500:
                wait_time = (552 - available) / restore_rate
                wait_time *= 0.4
                print(f"Low capacity ({available} units). Waiting {round(wait_time, 2)} seconds...")
                time.sleep(max(wait_time, 0.3))

            try:
                orders_data = data['data']['orders']['edges']
                for edge in orders_data:
                    order = edge['node']
                    # Exclude cancelled
                    if order.get('cancelledAt') is not None:
                        print('cancelled order')
                        continue
                    orders.append(order)
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
