from hefs.models import Orders


class MakeFactuurOverview():
    def prepare_overview(self):
        result_dict = {}

        orders = Orders.objects.all()

        for order in orders:
            conversie_id = order.conversieID
            order_price = float(order.orderprijs)
            shipping_cost = float(order.verzendkosten)

            # Calculate the desired values
            calculated_values = [
                [order_price],
                [order_price - shipping_cost],
                [(order_price - shipping_cost) / 1.09],
                [((order_price - shipping_cost) / 1.09) * 0.85]
            ]

            result_dict[conversie_id] = calculated_values

        return result_dict
