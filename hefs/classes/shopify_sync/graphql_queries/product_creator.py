import requests


class GraphQLProductCreator:
    def create_product_with_graphql(self, product_data, domain_name, access_token):
        # GraphQL endpoint
        url = domain_name

        # Headers
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        # GraphQL mutation
        mutation = """
        mutation($input: ProductInput!) {
          productCreate(input: $input) {
            product {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        # Prepare the ProductInput
        input_data = {
            "title": product_data["title"],
            "descriptionHtml": product_data["descriptionHtml"],
            "handle": product_data["handle"],
            "status": product_data["status"],
            "tags": product_data["tags"],
            "metafields": [
                {
                    "namespace": metafield["node"]["namespace"],
                    "key": metafield["node"]["key"],
                    "value": metafield["node"]["value"],
                    "type": metafield["node"]["type"]
                }
                for metafield in product_data["metafields"]["edges"]
            ],
            "variants": [
                {
                    "price": variant["node"]["price"],
                    "sku": variant["node"]["sku"],
                    "inventoryManagement": variant["node"]["inventoryManagement"],
                    "weight": variant["node"]["weight"],
                    "weightUnit": variant["node"]["weightUnit"]
                }
                for variant in product_data["variants"]["edges"]
            ],
            "seo": {
                "title": product_data["seo"]["title"],
                "description": product_data["seo"]["description"]
            }
        }

        # Payload
        payload = {
            "query": mutation,
            "variables": {"input": input_data}
        }

        # Send the request
        response = requests.post(url, json=payload, headers=headers)

        # Check for errors
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("data", {}).get("productCreate", {}).get("userErrors", []):
                print("User Errors:", response_data["data"]["productCreate"]["userErrors"])
                return None, 400
            else:
                created_product = response_data["data"]["productCreate"]["product"]
                print("Created Product:", created_product)
                product_id = created_product["id"]
                print(f"Product created successfully with ID: {product_id}")

                # Extract images from the product data
                images = product_data.get("images", [])

                if images:
                    print("Adding images to product...")
                    self.add_images_to_product(product_id, images, domain_name, access_token)
                else:
                    print("No images to add for this product.")
                return created_product, 201
        else:
            print("HTTP Error:", response.status_code, response.text)
            return None, response.status_code


    def add_images_to_product(self, product_id, images, domain_name, access_token):
        # GraphQL endpoint
        url = domain_name

        # Headers
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        # GraphQL mutation for adding images
        mutation = """
        mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
          productCreateMedia(media: $media, productId: $productId) {
            media {
              alt
              mediaContentType
              status
            }
            mediaUserErrors {
              field
              message
            }
            product {
              id
              title
            }
          }
        }
        """

        # Add each image to the product
        for image in images['edges']:
            input_data = {
                "media": {
                    "alt": image['node']["altText"],
                    "mediaContentType": "IMAGE",
                    "originalSource": image['node']["originalSrc"]
                },
                "productId": product_id
            }

            # Payload
            payload = {
                "query": mutation,
                "variables": input_data
            }

            # Send the request
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("data", {}).get("productCreateMedia", {}).get("userErrors", []):
                    print("User Errors:", response_data["data"]["productCreateMedia"]["userErrors"])
                else:
                    print("Image added:", response_data["data"]["productCreateMedia"]["media"])
            else:
                print("HTTP Error:", response.status_code, response.text)
