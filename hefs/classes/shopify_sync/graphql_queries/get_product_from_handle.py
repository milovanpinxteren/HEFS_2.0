import requests


class GetProductFromHandle:
    def get_product(self, product_handle, url, access_token):
        # GraphQL query to retrieve product information by handle
        query = """
        query productByHandle($handle: String!) {
          productByHandle(handle: $handle) {
            id
            title
            handle
            descriptionHtml
            variants(first: 10) {
              edges {
                node {
                  id
                  title
                  price
                    inventoryItem {
                        id
                    }                 
                }
              }
            }
          }
        }
        """

        # Define the variables for the query
        variables = {"handle": product_handle}

        # Set up headers for the request
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        }

        # Make the POST request to the Shopify GraphQL endpoint
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers
        )

        # Check for a successful response
        if response.status_code == 200:
            data = response.json()['data']['productByHandle']
            return data
        else:
            # Handle errors appropriately
            raise Exception(f"Failed to fetch product: {response.status_code} {response.text}")
