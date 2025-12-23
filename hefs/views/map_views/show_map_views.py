from collections import defaultdict

from django.db.models import Q
from django.shortcuts import render

from hefs.classes.routingclasses.map_maker import MapMaker
from hefs.models import Route, Productinfo, PickItems, Stop


# def show_map(request):
#     map_maker = MapMaker()
#     map_dict = defaultdict(list)
#
#     selected_date = request.GET.get("date")
#     route_id = request.GET.get("route_id")
#     conversie_id = request.GET.get("conversie_id")
#     # Build the query
#     query = Q()
#     if selected_date:
#         query &= Q(date=selected_date)
#     if route_id:
#         query &= Q(id=route_id)
#     if conversie_id:
#         query &= Q(stops__order__conversieID=conversie_id)
#     routes_queryset = Route.objects.filter(query).distinct().order_by('name')
#
#     for route in routes_queryset:
#         vehicle = route.vehicle
#         for stop in route.stops.order_by("sequence_number"):
#             order = stop.order  # Assuming Orders has required fields
#             map_dict[vehicle.vehicle_number].append({
#                 "name": order.conversieID,  # Replace with actual field in Orders
#                 "lat": order.latitude,  # Replace with actual field in Orders
#                 "lon": order.longitude,  # Replace with actual field in Orders
#                 "address": (order.straatnaam or "") + (order.huisnummer or "") + (order.postcode or "") +
#                            (order.plaats or ""),  # Replace with actual field in Orders
#                 "sequence": stop.sequence_number,
#                 "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
#                 "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
#                 "telephone_number": stop.order.telefoonnummer,
#                 "notes": (stop.notes or "") + (order.opmerkingen or ""),
#             })
#
#     map = map_maker.make_map(map_dict, 'routes')
#     context = {'map': map._repr_html_()}
#
#     if selected_date:
#         stops_table = generate_stops_table(routes_queryset)
#         context['stops_table'] = stops_table
#     return render(request, 'map.html', context)


def show_map(request):
    map_maker = MapMaker()
    map_dict = defaultdict(list)

    selected_date = request.GET.get("date")
    route_id = request.GET.get("route_id")
    conversie_id = request.GET.get("conversie_id")

    # Fixed product IDs
    product_ids = ['21001', '21002', '21003']

    # Build the query
    query = Q()
    if selected_date:
        query &= Q(date=selected_date)
    if route_id:
        query &= Q(id=route_id)
    if conversie_id:
        query &= Q(stops__order__conversieID=conversie_id)
    routes_queryset = Route.objects.filter(query).distinct().order_by('name')

    # Collect all order IDs
    order_ids = Stop.objects.filter(
        route__in=routes_queryset
    ).values_list('order_id', flat=True)

    # Build product lookup: {order_id: {productID: quantity}}
    product_lookup = defaultdict(lambda: {pid: 0 for pid in product_ids})

    pickitems = PickItems.objects.filter(
        pick_order__order_id__in=order_ids,
        product__productID__in=product_ids
    ).values(
        'pick_order__order_id',
        'product__productID',
        'hoeveelheid'
    )

    for item in pickitems:
        order_id = item['pick_order__order_id']
        pid = item['product__productID']
        qty = item['hoeveelheid']
        product_lookup[order_id][pid] += qty

    # Get product omschrijving for display
    product_names = dict(
        Productinfo.objects.filter(
            productID__in=product_ids
        ).values_list('productID', 'omschrijving')
    )

    for route in routes_queryset:
        vehicle = route.vehicle
        for stop in route.stops.order_by("sequence_number"):
            order = stop.order
            stop_data = {
                "name": order.conversieID,
                "lat": order.latitude,
                "lon": order.longitude,
                "address": (order.straatnaam or "") + (order.huisnummer or "") + (order.postcode or "") +
                           (order.plaats or ""),
                "sequence": stop.sequence_number,
                "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
                "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
                "telephone_number": stop.order.telefoonnummer,
                "notes": (stop.notes or "") + (order.opmerkingen or ""),
            }

            # Add product quantities
            for pid in product_ids:
                stop_data[product_names.get(pid, pid)] = product_lookup[order.id][pid]

            map_dict[vehicle.vehicle_number].append(stop_data)

    map = map_maker.make_map(map_dict, 'routes')
    context = {'map': map._repr_html_()}

    if selected_date:
        stops_table = generate_stops_table(routes_queryset, product_lookup, product_names, product_ids)
        context['stops_table'] = stops_table
        context['product_names'] = [product_names.get(pid, pid) for pid in product_ids]

    return render(request, 'map.html', context)


def generate_stops_table(routes_queryset, product_lookup, product_names, product_ids):
    """Generate a table of stops for each route with Google Maps links."""
    stops_table = defaultdict(list)

    for route in routes_queryset:
        for stop in route.stops.order_by("sequence_number"):
            order = stop.order
            route_info = route.name + ' op ' + route.date.strftime('%d-%m') + ' ID: ' + str(
                route.id) + ' || voertuig: ' + str(route.vehicle)

            stop_data = {
                "sequence": stop.sequence_number,
                "conversieID": order.conversieID,
                "address": f"{order.straatnaam or ''} {order.huisnummer or ''}, {order.postcode or ''}, {order.plaats or ''}",
                "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
                "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
                "telephone_number": stop.order.telefoonnummer if stop.order.telefoonnummer else '',
                "notes": (stop.notes or "") + (order.opmerkingen or ""),
                "google_maps_link": route.google_maps_link,
                "products": [product_lookup[order.id][pid] for pid in product_ids],
                "has_any_product": any(product_lookup[order.id][pid] > 0 for pid in product_ids),

            }
            stops_table[route_info].append(stop_data)
    return dict(stops_table)

# def generate_stops_table(routes_queryset):
#     """Generate a table of stops for each route with Google Maps links."""
#     stops_table = defaultdict(list)
#
#     for route in routes_queryset:
#         for stop in route.stops.order_by("sequence_number"):
#             order = stop.order
#             route_info = route.name + ' op ' + route.date.strftime('%d-%m') + ' ID: ' + str(
#                 route.id) + ' || voertuig: ' + str(route.vehicle)
#             stops_table[route_info].append({
#                 "sequence": stop.sequence_number,
#                 "conversieID": order.conversieID,
#                 "address": f"{order.straatnaam or ''} {order.huisnummer or ''}, {order.postcode or ''}, {order.plaats or ''}",
#                 "arrival_time": stop.arrival_time.strftime("%H:%M") if stop.arrival_time else None,
#                 "departure_time": stop.departure_time.strftime("%H:%M") if stop.departure_time else None,
#                 "telephone_number": stop.order.telefoonnummer if stop.order.telefoonnummer else '',
#                 "notes": (stop.notes or "") + (order.opmerkingen or ""),
#                 "google_maps_link": route.google_maps_link,
#             })
#     return dict(stops_table)
