import requests
from django.conf import settings


class ProductInfoGetter():
    def __init__(self):
        self.hob_access_token = settings.HOB_ACCESS_TOKEN

    def get_product_info(self, product_id):
        graphql_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.hob_access_token,
        }

        # Step 1: Fetch Product Information and Metafields
        query = """
        query($id: ID!) {
            product(id: $id) {
                id
                title
                handle
                descriptionHtml
                status
                tags
                totalInventory
                variants(first: 1) {
                  edges {
                    node {
                      barcode
                      compareAtPrice
                      price
                      sku
                      weight
                      weightUnit
                      inventoryManagement
                    }
                  }
                }
                metafields(first: 10) {
                    edges {
                        node {
                            namespace
                            key
                            value
                            type
                        }
                    }
                }
                images(first: 10) {
                  edges {
                    node {
                      id
                      altText
                      originalSrc
                    }
                  }
                }
                seo {
                    description
                    title
                }
            }
        }
        """
        variables = {"id": product_id}
        response = requests.post(
            f"https://7c70bf.myshopify.com/admin/api/2023-04/graphql.json",
            headers=graphql_headers,
            json={"query": query, "variables": variables},
        )
        if response.status_code != 200:
            return False, response.status_code

        product_info = response.json()["data"]["product"]
        return product_info
