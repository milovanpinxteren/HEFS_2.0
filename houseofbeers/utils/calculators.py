from collections import defaultdict
from decimal import Decimal, InvalidOperation


def group_orders_by_channel_and_tag(orders):
    grouped_data = defaultdict(lambda: {
        "tags": defaultdict(lambda: {
            "total_quantity": 0,
            "total_revenue": Decimal("0.00"),
        }),
        "payments": defaultdict(lambda: {
            "count": 0,
            "total_revenue": Decimal("0.00"),
        }),
    })
    relevant_tags = [
        "BTW 0", "BTW Hoog", "BTW Laag", "Statiegeld: 0.0", "Statiegeld: 0", "Statiegeld: 0.10", "Statiegeld: 0.15"
        , "Statiegeld: 0.20", "Statiegeld: 0.30", "Statiegeld: 0.40", "Statiegeld: 0.50"
    ]
    for order in orders:
        channel = order.get("channelInformation", {}).get("channelDefinition", {}).get("channelName", "Unknown")
        line_items = order.get("lineItems", {}).get("edges", [])
        payments = order.get("paymentGatewayNames", [])
        subtotal_str = order.get("subtotalPriceSet", {}).get("shopMoney", {}).get("amount", "0.00")
        try:
            subtotal = Decimal(subtotal_str)
        except (TypeError, InvalidOperation):
            subtotal = Decimal("0.00")
        for gateway in payments:
            entry = grouped_data[channel]["payments"][gateway]
            entry["count"] += 1
            entry["total_revenue"] += subtotal

        for item_edge in line_items:
            item = item_edge["node"]
            quantity = item.get("quantity", 0)
            product = item.get("product", {})
            if product:
                tags = product.get("tags", []) or ["Untagged"]
            else:
                print('No product in line item')

            # Extract price
            try:
                price = Decimal(product["variants"]["edges"][0]["node"]["price"])
            except (KeyError, IndexError, TypeError):
                price = Decimal("0.00")

            for tag in tags:
                if tag not in relevant_tags:
                    continue

                revenue = price * quantity

                if tag.startswith("Statiegeld:"):
                    try:
                        statiegeld_value = Decimal(tag.split(":")[1].strip())
                        revenue = statiegeld_value * quantity
                    except (IndexError, InvalidOperation):
                        # Fallback to normal revenue if statiegeld can't be parsed
                        pass

                entry = grouped_data[channel]["tags"][tag]
                entry["total_quantity"] += quantity
                entry["total_revenue"] += revenue

    return {
        channel: {
            "tags": dict(sorted(data["tags"].items())),
            "payments": dict(data["payments"]),
        }
        for channel, data in grouped_data.items()
    }
