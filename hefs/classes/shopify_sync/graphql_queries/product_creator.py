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
                product_id = created_product["id"]
                # Extract images from the product data
                images = product_data.get("images", [])
                if images:
                    added_images = self.add_images_to_product(product_id, images, domain_name, access_token)
                    if added_images:
                        published = self.publish_product_to_all_channels(product_id, domain_name, access_token)
                        if published:
                            return True
                        else:
                            return False
                else:
                    print("No images to add for this product.")
                return created_product, 201
        else:
            print("HTTP Error:", response.status_code, response.text)
            return None, response.status_code

    #TODO: Publish to sales channels

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
                    return False
                else:
                    print("Image added:", response_data["data"]["productCreateMedia"]["media"])
                    return True
            else:
                print("HTTP Error:", response.status_code, response.text)
                return False

    def publish_product_to_all_channels(self, product_id, domain_name, access_token):
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

        sales_channels_query = """
         query {
           publications(first: 100) {
             edges {
               node {
                 id
                 name
               }
             }
           }
         }
         """
        response = requests.post(domain_name, json={"query": sales_channels_query}, headers=headers)
        response_data = response.json()

        # Check for errors
        if "errors" in response_data:
            raise Exception(response_data["errors"])
        #Publish it to all

        channels = response_data["data"]["publications"]["edges"]

        # Step 2: Publish product to all channels
        mutation = """
            mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
              publishablePublish(id: $id, input: $input) {
                shop {
                  publicationCount
                }
                userErrors {
                  field
                  message
                }
              }
            }
        """


        for channel in channels:
            publication_id = channel["node"]["id"]
            variables = {
                "id": product_id,
                "input": {"publicationId": publication_id}
            }
            publish_response = requests.post(
                domain_name,
                json={"query": mutation, "variables": variables},
                headers=headers
            )
            publish_data = publish_response.json()

            # Handle errors in publishing
            if publish_data.get("data", {}).get("publishablePublish", {}).get("userErrors"):
                errors = publish_data["data"]["publishablePublish"]["userErrors"]
                for error in errors:
                    print(f"Error publishing to channel {channel['node']['name']}: {error['message']}")

        return True
