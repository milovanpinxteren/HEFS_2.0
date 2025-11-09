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
    total_refunded = 0
    total_shipping = 0
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
        if not line_items:
            print(f'no lineitems: {order}')
        try:
            shipping = Decimal(shipping_str)
        except (TypeError, InvalidOperation):
            print(f'error: {order}, shipping_str {shipping_str}')
            shipping = Decimal("0.00")

        try:
            refunded = Decimal(refunded_str)
        except (TypeError, InvalidOperation):
            print(f'error: {order}, refunded_str {refunded_str}')
            refunded = Decimal("0.00")
        try:
            subtotal = Decimal(subtotal_str)
        except (TypeError, InvalidOperation):
            print(f'error: {order}, subtotal_str {subtotal_str}')
            subtotal = Decimal("0.00")
        # print(f'subtotal: {subtotal}, shipping: {shipping}, refunded: {refunded}')
        order_revenue = subtotal + shipping - refunded
        total_refunded += refunded
        total_shipping += shipping
        skip_tag_calculation = any(gw.lower() == 'paypal' for gw in payments)
        added_gateway = False

        for gateway in payments:
            key_name = 'Test Payment' if gateway == 'paypal' else gateway
            entry = grouped_data[channel]["payments"][key_name]
            added_gateway = True
            entry["count"] += 1
            entry["total_revenue"] += order_revenue

        if not added_gateway:
            print(f'No gateway: {channel} on order {order}')
            entry = grouped_data[channel]["payments"]['No payment info']
            entry["count"] += 1
            entry["total_revenue"] += order_revenue

        if not skip_tag_calculation:
            if len(line_items) == 0:
                print(f'no lineitems: {order}')
            for item_edge in line_items:
                item = item_edge["node"]
                quantity = item.get("quantity", 0)

                try:
                    price_str = item["discountedUnitPriceSet"]["shopMoney"]["amount"]
                    price = Decimal(price_str)
                except (KeyError, TypeError, InvalidOperation):
                    print(f"Invalid price: {item}")
                    price = Decimal("0.00")

                product = item.get("product", None)

                # ❗ If no product, fallback: assign revenue to BTW Hoog and skip tags
                if not product:
                    print("Missing product, falling back to BTW Hoog")
                    entry = grouped_data[channel]["tags"]["Geen tag"]
                    entry["total_quantity"] += quantity
                    entry["total_revenue"] += price * quantity
                    continue

                # ❌ Skip statiegeld product lines
                title = product.get("title", "")
                if "Statiegeld" in title:
                    continue

                # ✅ Proceed with tag parsing
                tags = product.get("tags", []) or ["Untagged"]

                # STEP 1: Handle statiegeld (if tagged)
                statiegeld_value = Decimal("0.00")
                for tag in tags:
                    if tag.startswith("Statiegeld:"):
                        try:
                            statiegeld_value = Decimal(tag.split(":")[1].strip())
                            entry = grouped_data[channel]["tags"]["Statiegeld"]
                            entry["total_quantity"] += quantity
                            entry["total_revenue"] += statiegeld_value * quantity
                        except InvalidOperation:
                            print(f"Invalid statiegeld tag: {tag}")
                        continue

                # STEP 2: Handle tax tag (first matching one)
                tax_tag = next((t for t in tags if t in relevant_tags and not t.startswith("Statiegeld")), None)
                if not tax_tag or tax_tag == "Untagged":
                    tax_tag = "Geen tag"  # fallback

                entry = grouped_data[channel]["tags"][tax_tag]
                entry["total_quantity"] += quantity
                entry["total_revenue"] += price * quantity
        else:
            print('skipping paypall order')

    print(f'total refunded: {total_refunded}, total shipping: {total_shipping}')
    return {
        channel: {
            "tags": dict(sorted(data["tags"].items())),
            "payments": dict(data["payments"]),
        }
        for channel, data in grouped_data.items()
    }
