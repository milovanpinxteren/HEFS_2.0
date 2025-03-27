import requests


class GraphQLInventoryUpdater:
    def __init__(self):
        return


    def update_inventory(self, inventory_item_id, url, access_token, location_id, available_amount):
        print('Updating quantity for inventory item:', inventory_item_id)
        available_amount = int(available_amount)
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }
        # GraphQL mutation for setting inventory quantities
        query = """
        mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
            inventorySetQuantities(input: $input) {
                inventoryAdjustmentGroup {
                    createdAt
                    reason
                    changes {
                        name
                        delta
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """

        # Construct the input payload
        quantities_input = {
            "inventoryItemId": inventory_item_id,
            "locationId": location_id,
            "quantity": available_amount
        }

        variables = {
            "input": {
                "name": "available",
                "reason": "correction",
                "ignoreCompareQuantity": True,
                "quantities": [quantities_input]
            }
        }

        payload = {
            "query": query,
            "variables": variables
        }

        response = requests.post(
            url=url,
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            response_data = response.json()
            errors = response_data.get("data", {}).get("inventorySetQuantities", {}).get("userErrors", [])
            if not errors:
                print("Quantity updated successfully.")
                return True
            else:
                print("GraphQL errors:", errors)
                return False
        else:
            print("Request failed with status code:", response.status_code)
            print("Response:", response.text)
            return False