from datetime import datetime, timedelta
from math import radians, sin, cos, atan2, sqrt

from hefs.classes.routingclasses.routes_generator import RoutesGenerator


class ArrivalTimeCalculator:
    def __init__(self, config=None):
        self.routes_generator = RoutesGenerator(config)
        self.config = self.routes_generator.config

    def haversine(self, coord1, coord2):
        """Calculate distance between two coordinates in meters"""
        R = 6371000.0  # Earth radius in meters
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance * self.config.haversine_road_multiplier

    def calculate_travel_time(self, distance_meters):
        """Calculate travel time in seconds based on distance and average speed"""
        average_speed_ms = (self.config.average_speed_kmh * 1000) / 3600
        return int(distance_meters / average_speed_ms)

    def calculate_arrival_times(self, routes_queryset):
        """
        Calculate arrival times for stops in the given routes queryset.
        Uses haversine distance and configured average speed instead of Google Maps API.
        """
        print("Calculating arrival times...")

        for route in routes_queryset:
            stops = list(route.stops.order_by("sequence_number"))

            if len(stops) < 2:
                print(f"Skipping route {route.name} - not enough stops.")
                continue

            # Start from the configured earliest customer service time
            route_date = datetime.combine(route.date, datetime.min.time())
            current_time = route_date.replace(
                hour=self.config.customer_start_hour,
                minute=0,
                second=0,
                microsecond=0
            )

            # Calculate backward from first customer to determine departure time
            first_stop = stops[0]
            second_stop = stops[1]
            first_distance = self.haversine(
                (first_stop.order.latitude, first_stop.order.longitude),
                (second_stop.order.latitude, second_stop.order.longitude)
            )
            first_travel_time = self.calculate_travel_time(first_distance)
            departure_time = current_time - timedelta(seconds=first_travel_time)

            # Update route departure time
            route.departure_time = departure_time.time()

            # Reset current time to departure time
            current_time = departure_time

            total_distance = 0
            total_travel_time = 0

            # Calculate times for each stop
            for i, stop in enumerate(stops):
                # Set arrival time
                stop.arrival_time = current_time.time()

                # Add service time
                service_time_seconds = 0 if i == 0 else self.config.get_service_time_seconds()
                departure_time = current_time + timedelta(seconds=service_time_seconds)
                stop.departure_time = departure_time.time()
                stop.save()

                # Calculate travel to next stop
                if i < len(stops) - 1:
                    next_stop = stops[i + 1]
                    distance = self.haversine(
                        (stop.order.latitude, stop.order.longitude),
                        (next_stop.order.latitude, next_stop.order.longitude)
                    )
                    travel_time = self.calculate_travel_time(distance)

                    total_distance += distance
                    total_travel_time += travel_time

                    # Move to next arrival time
                    current_time = departure_time + timedelta(seconds=travel_time)

            # Update route totals
            route.total_distance = total_distance / 1000  # Convert to km

            # Calculate total time from departure to last stop departure
            total_seconds = (departure_time - route_date.replace(
                hour=route.departure_time.hour,
                minute=route.departure_time.minute,
                second=route.departure_time.second
            )).total_seconds()

            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            route.total_travel_time = datetime.min.replace(
                hour=min(hours, 23),
                minute=minutes,
                second=seconds
            ).time()

            # Regenerate Google Maps link
            coordinates_for_map_link = [
                (float(stop.order.latitude), float(stop.order.longitude))
                for stop in stops
            ]
            route.google_maps_link = self.routes_generator.create_google_maps_link(
                coordinates_for_map_link
            )

            route.save()
            print(f"Updated {route.name}: {route.total_distance:.2f} km, {len(stops)} stops")

        print("Arrival times calculation complete!")
