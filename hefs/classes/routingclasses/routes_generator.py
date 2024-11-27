import datetime
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from hefs.models import Orders, Vehicle, DistanceMatrix, Route, Stop, VerzendOpties


class RoutesGenerator():
    def generate_routes(self, date_obj, date):
        print('generating routes')
        verzend_opties = VerzendOpties.objects.filter(verzenddatum=date,
                                                      verzendoptie__icontains="Bezorging").values_list('id', flat=True)
        depot_order = Orders.objects.get(pk=99999)  # Fetch the depot order
        orders = [depot_order] + list(Orders.objects.filter(
            afleverdatum=date_obj, verzendoptie_id__in=verzend_opties
        ))  # Add depot to the list of orders

        vehicles = Vehicle.objects.all()
        distance_matrix = self.create_distance_matrix(orders)
        travel_time_matrix = self.create_travel_time_matrix(distance_matrix)

        data = {
            "distance_matrix": distance_matrix,
            "travel_times": travel_time_matrix,
            "demands": [0 if order.pk == 99999 else int((order.orderprijs * 0)) + 1 for order in orders],
            "vehicle_capacities": [vehicle.capacity for vehicle in vehicles],
            "num_vehicles": vehicles.count(),
            "depot": 0,
        }

        # Base time: 6:00 AM as the starting reference for normalization
        # base_time = datetime.time(6, 0)  # Reference start time (6:00 AM)
        # base_seconds = base_time.hour * 3600 + base_time.minute * 60  # Convert base time to seconds

        data['time_windows'] = [
            (6 * 3600, 15 * 3600)  # Hub start time (6:00 AM to 6:00 AM)
            if idx == 0 else (8 * 3600, 17 * 3600)  # Other stops: between 8:00 AM and 5:00 PM
            for idx in range(len(data['distance_matrix']))
        ]

        # data['time_windows'] = [
        #     (
        #         base_seconds,  # Start time is always 6:00 AM in seconds
        #         (order.aflevertijd.hour * 3600 + order.aflevertijd.minute * 60)  # End time in seconds
        #         if order.aflevertijd and order.aflevertijd != datetime.time(0, 0)
        #         else (16 * 3600)  # Default to 4:00 PM if aflevertijd is null or 00:00:00
        #     )
        #     for order in orders
        # ]

        solution = self.solve_vrp(data)

        if solution:
            print('solution')
            self.save_routes_to_db(orders, vehicles, solution, data, date_obj)
        else:
            print('no solution')

    def solve_vrp(self, data):
        """Solve the VRP using Google OR-Tools."""
        manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]


        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index, 10200, data["vehicle_capacities"], True, "Capacity"
        )

        # Time Window constraint
        # def time_callback(from_index, to_index):
        #     """Calculate travel time between nodes."""
        #     from_node = manager.IndexToNode(from_index)
        #     to_node = manager.IndexToNode(to_index)
        #     return data["travel_times"][from_node][to_node]
        #
        # time_callback_index = routing.RegisterTransitCallback(time_callback)
        #
        # routing.AddDimension(
        #     time_callback_index,  # Index of the transit callback
        #     10200,  # Allow 1 hour of slack
        #     10 * 3600,  # Maximum route time is 10 hours (6:00 AM to 4:00 PM)
        #     False,  # Don't force vehicles to return to depot
        #     "Time"
        # )

        # time_dimension = routing.GetDimensionOrDie("Time")

        # Set the time windows for each location
        # for idx, time_window in enumerate(data["time_windows"]):
        #     index = manager.NodeToIndex(idx)
        #     time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        #
        # # Set start time for each vehicle
        # for vehicle_id in range(data["num_vehicles"]):
        #     start_index = routing.Start(vehicle_id)
        #     time_dimension.CumulVar(start_index).SetRange(6 * 3600, 6 * 3600)  # Vehicles start at 6:00 AM

        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
        search_parameters.time_limit.seconds = 240  # Allow more time to explore solutions

        #Results:
            # PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH = 2762.52 km
            # AUTOMATIC + AUTOMATIC = 2813.94 km
            # SAVINGS + TABU_SEARCH = no solution
            # BEST_INSERTION + GUIDED_LOCAL_SEARCH = no solution
            # PARALLEL_CHEAPEST_INSERTION + GUIDED_LOCAL_SEARCH = 2947.64 km
            # CHRISTOFIDES + GUIDED_LOCAL_SEARCH = 2880.09 km
            # CHRISTOFIDES + TABU_SEARCH = 2877.12 km
            #PARALLEL_CHEAPEST_INSERTION + SIMULATED_ANNEALING

        solution = routing.SolveWithParameters(search_parameters)

        # return solution
        if solution:
            return {
                "manager": manager,
                "routing": routing,
                "solution": solution,
            }
        return None

    def create_distance_matrix(self, orders):
        """Generate the distance matrix from the DistanceMatrix model."""
        matrix = []
        for origin in orders:
            row = []
            for destination in orders:
                distance = DistanceMatrix.objects.get(origin=origin, destination=destination).distance_meters
                row.append(distance)
            matrix.append(row)
        return matrix

    def create_travel_time_matrix(self, distance_matrix, average_speed_kmh=60):
        """
        Generate a travel time matrix based on the distance matrix and average speed.
        :param distance_matrix: 2D list of distances in meters.
        :param average_speed_kmh: Average vehicle speed in km/h.
        :return: 2D list of travel times in seconds.
        """
        average_speed_ms = (average_speed_kmh * 1000) / 3600  # Convert km/h to m/s
        travel_time_matrix = [
            [int(distance / average_speed_ms) for distance in row]
            for row in distance_matrix
        ]
        return travel_time_matrix

    def save_routes_to_db(self, orders, vehicles, solution, data, date_obj):
        """Save calculated routes and stops to the database."""
        manager = solution["manager"]
        routing = solution["routing"]
        vrp_solution = solution["solution"]

        # time_dimension = routing.GetDimensionOrDie("Time")


        # Clear old routes
        Route.objects.all().delete()
        Stop.objects.all().delete()

        total_distance = 0  # Initialize total distance across all routes

        # Create new routes
        for vehicle_id in range(data["num_vehicles"]):
            route_distance = 0  # Initialize total distance for the current route
            route_stops = []
            route = Route.objects.create(
                name=f"Route {vehicle_id}", vehicle=vehicles[vehicle_id], date=date_obj
            )
            index = routing.Start(vehicle_id)
            sequence_number = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                order = orders[node_index]
                route_stops.append((float(order.latitude), float(order.longitude)))

                # arrival_time_seconds = vrp_solution.Value(time_dimension.CumulVar(index))
                # departure_time_seconds = arrival_time_seconds
                # start_of_day = datetime.datetime.combine(date_obj, datetime.time(0, 0))
                # arrival_time = start_of_day + datetime.timedelta(seconds=arrival_time_seconds)
                # departure_time = start_of_day + datetime.timedelta(seconds=departure_time_seconds)

                next_index = vrp_solution.Value(routing.NextVar(index))
                if not routing.IsEnd(next_index):
                    next_node_index = manager.IndexToNode(next_index)
                    distance_to_next = data["distance_matrix"][node_index][next_node_index]
                    route_distance += distance_to_next

                stop = Stop.objects.create(order=order, route=route, sequence_number=sequence_number)
                # print(stop)

                sequence_number += 1
                index = vrp_solution.Value(routing.NextVar(index))

                # index = next_index
            route_distance_km = route_distance / 1000.0
            print(f"Route {vehicle_id} total distance: {route_distance_km:.2f} km")
            route.total_distance_km = route_distance_km  # Save to DB if you have this field
            total_distance += route_distance
            google_maps_link = self.create_google_maps_link(route_stops)
            print(f"Route {vehicle_id} total distance: {route_distance_km:.2f} km. Link: {google_maps_link}")
            route.google_maps_link = google_maps_link  # Assuming the model has this field
            route.save()

        total_distance_km = total_distance / 1000.0
        print(f"Total distance across all routes: {total_distance_km:.2f} km")


    def create_google_maps_link(self, route_stops):
        """
        Create a Google Maps link for a route.
        :param stops: List of (latitude, longitude) tuples for the stops.
        :return: A Google Maps link as a string.
        """
        # stops = Stop.objects.filter(route=route)
        base_url = "https://www.google.com/maps/dir/"
        waypoints = "/".join([f"{lat},{lng}" for lat, lng in route_stops])
        return base_url + waypoints
