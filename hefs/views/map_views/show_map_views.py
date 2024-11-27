from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from hefs.models import Route, Stop

from hefs.classes.routingclasses.map_maker import MapMaker


def show_map(request):
    map_maker = MapMaker()
    map_dict = defaultdict(list)

    selected_date = request.GET.get("date")
    route_id = request.GET.get("route_id")
    conversie_id = request.GET.get("conversie_id")
    # Build the query
    query = Q()
    if selected_date:
        query &= Q(date=selected_date)
    if route_id:
        query &= Q(id=route_id)
    if conversie_id:
        query &= Q(stops__order__ConversieID=conversie_id)
    routes_queryset = Route.objects.filter(query).distinct()

    for route in routes_queryset:
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
                "notes": stop.notes or "",
            })

    map = map_maker.make_map(map_dict, 'routes')
    context = {'map': map._repr_html_()}
    return render(request, 'map.html', context)
