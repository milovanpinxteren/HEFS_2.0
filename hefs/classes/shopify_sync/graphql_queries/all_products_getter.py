import requests
from django.conf import settings


class AllProductsGetter:
    def __init__(self):
        self.hob_access_token = settings.HOB_ACCESS_TOKEN


    def fetch_products(self,after_cursor=None):
        query = """
        query($after: String) {
          products(first: 100, after: $after) {
            edges {
              cursor
              node {
                id
                title
                handle
                description
                totalInventory
                tags
                  seo {
                    title
                    description
                  }
                variants(first: 10) {
                  edges {
                    node {
                      id
                      title
                      price
                      compareAtPrice
                      taxable
                      inventoryItem {
                        id
                        }
                    }
                  }
                }
                metafields(first: 10) {
                    edges {
                        node {
                        key
                        namespace
                        value
                            }
                        }
                }
              }
            }
            pageInfo {
              hasNextPage
            }
          }
        }
        """

        variables = {"after": after_cursor} if after_cursor else {}

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.hob_access_token
        }

        response = requests.post(
            "https://7c70bf.myshopify.com/admin/api/2023-04/graphql.json",
            json={"query": query, "variables": variables},
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status code {response.status_code}. {response.text}")

    def get_all_products(self):
        after_cursor = None
        has_next_page = True
        all_products = []

        while has_next_page:
            result = self.fetch_products(after_cursor)
            try:
                products = result['data']['products']['edges']
                page_info = result['data']['products']['pageInfo']

                for product_edge in products:
                    product = product_edge['node']
                    all_products.append(product)

                has_next_page = page_info['hasNextPage']

                if has_next_page:
                    after_cursor = products[-1]['cursor']
            except Exception as e:
                print(f'Get all products exception: {e}')
                print(f'result: {result}')

        return all_products