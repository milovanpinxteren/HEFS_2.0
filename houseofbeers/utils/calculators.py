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
        try:
            channel = order.get("channelInformation", {}).get("channelDefinition", {}).get("channelName", "Unknown")
        except AttributeError:
            print('manual order, skipping')
            continue

        line_items = order.get("lineItems", {}).get("edges", [])
        payments = order.get("paymentGatewayNames", [])
        subtotal_str = order.get("currentSubtotalPriceSet", {}).get("shopMoney", {}).get("amount", "0.00")
        shipping_str = order.get("totalShippingPriceSet", {}).get("shopMoney", {}).get("amount", "0.00")
        refunded_str = order.get("totalRefundedSet", {}).get("shopMoney", {}).get("amount", "0.00")

        try:
            shipping = Decimal(shipping_str)
        except (TypeError, InvalidOperation):
            shipping = Decimal("0.00")

        try:
            refunded = Decimal(refunded_str)
        except (TypeError, InvalidOperation):
            refunded = Decimal("0.00")
        try:
            subtotal = Decimal(subtotal_str)
        except (TypeError, InvalidOperation):
            subtotal = Decimal("0.00")
        order_revenue = subtotal + shipping - refunded

        for gateway in payments:
            entry = grouped_data[channel]["payments"][gateway]
            entry["count"] += 1
            entry["total_revenue"] += order_revenue

        for item_edge in line_items:
            item = item_edge["node"]
            quantity = item.get("quantity", 0)
            product = item.get("product", {})
            price = Decimal(item_edge["node"]["discountedUnitPriceSet"]["shopMoney"]["amount"])
            if product:
                tags = product.get("tags", []) or ["Untagged"]

            for tag in tags:
                if tag.startswith("Statiegeld:"):
                    statiegeld_value = Decimal(tag.split(":")[1].strip())
                    revenue = statiegeld_value * quantity
                    entry = grouped_data[channel]["tags"]["Statiegeld"]
                    entry["total_quantity"] += quantity
                    entry["total_revenue"] += revenue
                    continue


                if tag not in relevant_tags:
                    continue

                revenue = price * quantity
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
