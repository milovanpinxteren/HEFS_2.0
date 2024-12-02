import googlemaps
from django.conf import settings
from datetime import datetime, timedelta


class ArrivalTimeCalculator:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)


    def calculate_arrival_times(self, routes_queryset):
        """
        Calculate arrival times for stops in the given routes queryset. The vehicle departs earlier
        if needed to ensure arrival at the first stop after 08:00.
        """
        print("Calculating arrival times...")

        for route in routes_queryset:
            stops = route.stops.order_by("sequence_number")
            coordinates = [
                f"{stop.order.latitude},{stop.order.longitude}" for stop in stops if
                stop.order.latitude and stop.order.longitude
            ]

            if len(coordinates) < 2:
                print(f"Skipping route {route.name} - not enough valid stops.")
                continue

            route_date = datetime.combine(route.date, datetime.min.time())
            earliest_arrival_time = route_date.replace(hour=8, minute=0, second=0, microsecond=0)

            # Request travel time to the first stop
            try:
                first_leg = self.gmaps.directions(
                    origin=coordinates[0],
                    destination=coordinates[1],
                    departure_time=route_date.replace(hour=0, minute=0)
                )
                first_leg_duration = first_leg[0]["legs"][0]["duration"]["value"]  # Duration in seconds
            except Exception as e:
                print(f"Error fetching travel time for first leg of route {route.name}: {e}")
                continue

            # Calculate departure time to arrive at the first stop after 08:00
            departure_time = earliest_arrival_time - timedelta(seconds=first_leg_duration)

            # Request directions for the entire route
            try:
                directions_result = self.gmaps.directions(
                    origin=coordinates[0],
                    destination=coordinates[-1],
                    waypoints=coordinates[1:-1] if len(coordinates) > 2 else None,
                    departure_time=departure_time,
                )
            except Exception as e:
                print(f"Error fetching directions for route {route.name}: {e}")
                continue

            # Initialize cumulative variables
            total_distance = 0
            total_duration = 0
            arrival_time = departure_time

            for i, (stop, leg) in enumerate(zip(stops, directions_result[0]["legs"])):
                distance = leg["distance"]["value"]  # Distance in meters
                duration = leg["duration"]["value"]  # Time in seconds

                stop.arrival_time = arrival_time.time()
                stop.departure_time = (arrival_time + timedelta(minutes=3)).time()
                total_distance += distance
                stop.save()
                total_duration += duration
                arrival_time += timedelta(seconds=duration)

            route.total_distance = total_distance / 1000  # Convert to km
            route.total_travel_time = (route_date + timedelta(seconds=total_duration)).time()
            route.save()

        return
