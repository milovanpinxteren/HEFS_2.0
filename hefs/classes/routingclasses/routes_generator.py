import datetime
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from hefs.models import Orders, Vehicle, DistanceMatrix, Route, Stop, VerzendOpties


class RoutesGenerator():
    def __init__(self):
        return

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

        data = {
            "distance_matrix": distance_matrix,
            "demands": [0 if order.pk == 99999 else int((order.orderprijs * 0)) + 1 for order in orders],
            "vehicle_capacities": [vehicle.capacity for vehicle in vehicles],
            "num_vehicles": vehicles.count(),
            "depot": 0,
        }
        # Default time if aflevertijd is None or 00:00:00
        # data['time_windows'] = [
        #     (
        #         datetime.datetime.combine(
        #             order.afleverdatum,
        #             datetime.time(6, 0)  # Start time is always 06:00
        #         ).timestamp(),
        #         datetime.datetime.combine(
        #             order.afleverdatum,
        #             order.aflevertijd if order.aflevertijd and order.aflevertijd != datetime.time(0,
        #                                                                                           0) else datetime.time(
        #                 16, 0)  # End time is either aflevertijd or 16:00
        #         ).timestamp(),
        #     )
        #     for order in orders
        # ]

        # Base time: 6:00 AM as the starting reference for normalization
        base_time = datetime.time(6, 0)  # Reference start time (6:00 AM)
        base_seconds = base_time.hour * 3600 + base_time.minute * 60  # Convert base time to seconds

        data['time_windows'] = [
            (
                base_seconds,  # Start time is always 6:00 AM in seconds
                (order.aflevertijd.hour * 3600 + order.aflevertijd.minute * 60)  # End time in seconds
                if order.aflevertijd and order.aflevertijd != datetime.time(0, 0)
                else (16 * 3600)  # Default to 4:00 PM if aflevertijd is null or 00:00:00
            )
            for order in orders
        ]

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
            demand_callback_index, 3600, data["vehicle_capacities"], True, "Capacity"
        )

        # Time Window constraint
        # def time_callback(from_index, to_index):
        #     from_node = manager.IndexToNode(from_index)
        #     to_node = manager.IndexToNode(to_index)
        #     return data["distance_matrix"][from_node][to_node]
        #
        # time_callback_index = routing.RegisterTransitCallback(time_callback)
        # routing.AddDimension(
        #     time_callback_index, 3600, 28800, True, "Time"
        # )

        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        # search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        # search_parameters.time_limit.seconds = 30  # Allow more time to explore solutions

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

    # def create_distance_matrix(self, orders):
    #     """Generate the distance matrix, including the depot with ID 99999."""
    #     matrix = []
    #     for origin in orders:
    #         row = []
    #         for destination in orders:
    #             if origin.pk == 99999 or destination.pk == 99999:
    #                 distance = DistanceMatrix.objects.get(
    #                     origin=origin if origin.pk != 99999 else None,
    #                     destination=destination if destination.pk != 99999 else None
    #                 ).distance_meters
    #             else:
    #                 distance = DistanceMatrix.objects.get(origin=origin, destination=destination).distance_meters
    #             row.append(distance)
    #         matrix.append(row)
    #
    #     return matrix

    def save_routes_to_db(self, orders, vehicles, solution, data, date_obj):
        """Save calculated routes and stops to the database."""
        manager = solution["manager"]
        routing = solution["routing"]
        vrp_solution = solution["solution"]

        # time_dimension = routing.GetDimensionOrDie("Time")


        # Clear old routes
        Route.objects.all().delete()
        Stop.objects.all().delete()

        # Create new routes
        for vehicle_id in range(data["num_vehicles"]):
            route = Route.objects.create(
                name=f"Route {vehicle_id}", vehicle=vehicles[vehicle_id], date=date_obj
            )
            index = routing.Start(vehicle_id)
            sequence_number = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                order = orders[node_index]
                # arrival_time_seconds = vrp_solution.Value(time_dimension.CumulVar(index))
                # departure_time_seconds = arrival_time_seconds
                # start_of_day = datetime.datetime.combine(date_obj, datetime.time(0, 0))
                # arrival_time = start_of_day + datetime.timedelta(seconds=arrival_time_seconds)
                # departure_time = start_of_day + datetime.timedelta(seconds=departure_time_seconds)

                stop, created = Stop.objects.get_or_create(
                    order=order,
                    defaults={
                        "route": route,
                        "sequence_number": sequence_number,
                        "arrival_time": None,  # Add appropriate logic to compute this if needed
                        "departure_time": None,  # Add appropriate logic to compute this if needed
                    },
                )
                if not created:
                    # If the stop exists, update its attributes
                    stop.route = route
                    stop.sequence_number = sequence_number
                    stop.arrival_time = None  # Update logic if needed
                    stop.departure_time = None  # Update logic if needed
                    stop.save()
                sequence_number += 1
                index = vrp_solution.Value(routing.NextVar(index))
