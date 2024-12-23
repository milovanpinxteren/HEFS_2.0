from collections import defaultdict

from hefs.classes.routingclasses.map_maker import MapMaker


class RouteShower:
    def __init__(self):
        self.map_maker = MapMaker()

    def prepare_route_showing(self, route):
        map_dict = defaultdict(list)
        stops_table = defaultdict(list)
        # route = route[0]
        vehicle = route.vehicle
        for stop in route.stops.order_by("sequence_number"):
            order = stop.order  # Assuming Orders has required fields
            map_dict[vehicle.vehicle_number].append({
                "name": order.conversieID,  # Replace with actual field in Orders
                "lat": order.latitude,  # Replace with actual field in Orders
                "lon": order.longitude,  # Replace with actual field in Orders
                "address": (order.straatnaam or "") + (order.huisnummer or "") + (order.postcode or "") +
                           (order.plaats or ""),  # Replace with actual field in Orders
                "sequence": stop.sequence_number,
                "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
                "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
                "visited": stop.visited,
                "notes": (stop.notes or "") + (order.opmerkingen or ""),
            })
            route_info = route.name + ' op ' + route.date.strftime('%d-%m') + ' ID: ' + str(
                route.id) + ' || voertuig: ' + str(route.vehicle)
            stops_table[route_info].append({
                "route_id": route.id,
                "sequence": stop.sequence_number,
                "conversieID": order.conversieID,
                "address": f"{order.straatnaam or ''} {order.huisnummer or ''}, {order.postcode or ''}, {order.plaats or ''}",
                "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
                "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
                "visited": stop.visited,
                "notes": (stop.notes or "") + (order.opmerkingen or ""),
                # "google_maps_link": route.google_maps_link,
            })
        maps_links = route.google_maps_link.split('|')  # Split the links

        map = self.map_maker.make_map(map_dict, 'routes')
        context = {'map': map._repr_html_(), 'stops_table': dict(stops_table), 'maps_links': maps_links}


        return context

