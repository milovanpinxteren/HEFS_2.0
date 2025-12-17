from math import radians, sin, cos, atan2, sqrt
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from datetime import time, timedelta

from django.core.exceptions import MultipleObjectsReturned
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from hefs.models import Orders, Vehicle, DistanceMatrix, Route, Stop, VerzendOpties


@dataclass
class RoutingConfig:
    """
    Centralized configuration for route optimization parameters.
    Tweak these values to adjust routing behavior.
    """
    first_solution_strategy: str = 'SAVINGS'
    local_search_metaheuristic: str = 'AUTOMATIC'
    # Results:
    # PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH = 2762.52 km
    # AUTOMATIC + AUTOMATIC = 2813.94 km
    # SAVINGS + TABU_SEARCH = no solution
    # BEST_INSERTION + GUIDED_LOCAL_SEARCH = no solution
    # PARALLEL_CHEAPEST_INSERTION + GUIDED_LOCAL_SEARCH = 2947.64 km
    # CHRISTOFIDES + GUIDED_LOCAL_SEARCH = 2880.09 km
    # CHRISTOFIDES + TABU_SEARCH = 2877.12 km
    # PARALLEL_CHEAPEST_INSERTION + SIMULATED_ANNEALING

    # Distance and Speed Parameters
    haversine_road_multiplier: float = 1.25  # Road distance multiplier (reduced from 1.3 for shorter routes)
    average_speed_kmh: float = 65  # Average speed for travel time calculation (reduced from 80 for realism)

    # Time Window Parameters (in hours, converted to seconds in code)
    depot_start_hour: int = 6
    depot_end_hour: int = 21
    customer_start_hour: int = 8
    customer_end_hour: int = 15
    vehicle_earliest_start_hour: int = 5
    vehicle_latest_start_hour: int = 16

    # Service and Route Parameters
    service_time_minutes: int = 10  # Time spent at each stop
    max_route_duration_hours: int = 16  # Maximum time a route can take
    slack_time_seconds: int = 25200  # Allow slack for delays (in seconds)

    # Capacity and Demand Parameters
    order_price_demand_divisor: int = 300  # Divides order price to calculate demand
    base_demand: int = 1  # Minimum demand per order
    vehicle_capacity_slack: int = 10200  # Slack capacity for vehicles

    # Optimization Parameters
    vehicle_fixed_cost: int = 50000  # Cost to use a vehicle (higher = fewer vehicles used)
    optimization_time_limit_seconds: int = 70  # Time limit for optimization
    force_depot_return: bool = False  # Whether routes must return to depot

    # Special Order IDs
    depot_order_id: int = 99999
    special_order_ids: List[int] = None

    def __post_init__(self):
        """Initialize special order IDs if not provided"""
        if self.special_order_ids is None:
            self.special_order_ids = [99999, 99998, 99997]

    def get_time_window_seconds(self, is_depot: bool = False) -> Tuple[int, int]:
        """Get time window in seconds for depot or customer"""
        if is_depot:
            return (self.depot_start_hour * 3600, self.depot_end_hour * 3600)
        return (self.customer_start_hour * 3600, self.customer_end_hour * 3600)

    def get_vehicle_start_window_seconds(self) -> Tuple[int, int]:
        """Get vehicle start time window in seconds"""
        return (self.vehicle_earliest_start_hour * 3600, self.vehicle_latest_start_hour * 3600)

    def get_service_time_seconds(self) -> int:
        """Get service time in seconds"""
        return self.service_time_minutes * 60

    def get_max_route_duration_seconds(self) -> int:
        """Get maximum route duration in seconds"""
        return self.max_route_duration_hours * 3600

    def calculate_demand(self, order_price: float, order_id: int) -> int:
        """Calculate demand for an order based on price"""
        if order_id in self.special_order_ids:
            return 0
        return max(self.base_demand, int(order_price // self.order_price_demand_divisor) + 1)

    def get_first_solution_strategy_enum(self):
        """Convert strategy string to OR-Tools enum"""
        strategies = {
            'PATH_CHEAPEST_ARC': routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
            'AUTOMATIC': routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC,
            'SAVINGS': routing_enums_pb2.FirstSolutionStrategy.SAVINGS,
            'BEST_INSERTION': routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION,
            'PARALLEL_CHEAPEST_INSERTION': routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
            'CHRISTOFIDES': routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES,
        }
        return strategies.get(self.first_solution_strategy, strategies['PATH_CHEAPEST_ARC'])

    def get_local_search_metaheuristic_enum(self):
        """Convert metaheuristic string to OR-Tools enum"""
        metaheuristics = {
            'GUIDED_LOCAL_SEARCH': routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
            'TABU_SEARCH': routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH,
            'SIMULATED_ANNEALING': routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING,
            'AUTOMATIC': routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC,
        }
        return metaheuristics.get(self.local_search_metaheuristic, metaheuristics['GUIDED_LOCAL_SEARCH'])


class RoutesGenerator:
    """
    Vehicle Routing Problem (VRP) solver using Google OR-Tools.
    Optimizes delivery routes with capacity, time window, and distance constraints.
    """

    def __init__(self, config: Optional[RoutingConfig] = None):
        """
        Initialize the routes generator with optional configuration.

        Args:
            config: RoutingConfig object. If None, uses default configuration.
        """
        self.config = config or RoutingConfig()
        self.route_datum = None
        print(f'Routes Generator initialized with config: depot_return={self.config.force_depot_return}')

    def _seconds_to_time(self, seconds: int) -> time:
        """
        Convert seconds since midnight to a time object.

        Args:
            seconds: Seconds since midnight (can be > 86400 for next day)

        Returns:
            time object
        """
        # Handle cases where time goes past midnight
        seconds = seconds % 86400
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return time(hour=hours, minute=minutes, second=secs)

    def _seconds_to_timedelta(self, seconds: int) -> timedelta:
        """
        Convert seconds to a timedelta object for total_travel_time.

        Args:
            seconds: Total seconds of travel

        Returns:
            timedelta object
        """
        return timedelta(seconds=seconds)

    def generate_routes(self, date_obj, date):
        """
        Main entry point for route generation.

        Args:
            date_obj: Date object for the delivery date
            date: Date string for filtering

        Returns:
            bool: True if routes were generated successfully, False otherwise
        """
        print(f'Generating routes for {date} with config parameters:')
        print(f'  - Average speed: {self.config.average_speed_kmh} km/h')
        print(f'  - Service time: {self.config.service_time_minutes} minutes')
        print(f'  - Depot return: {self.config.force_depot_return}')
        print(f'  - Vehicle fixed cost: {self.config.vehicle_fixed_cost}')
        print(f'  - depot_start_hour: {self.config.depot_start_hour}')
        print(f'  - depot_end_hour: {self.config.depot_end_hour}')
        print(f'  - customer_start_hour: {self.config.customer_start_hour}')
        print(f'  - customer_end_hour: {self.config.customer_end_hour}')
        print(f'  - vehicle_earliest_start_hour: {self.config.vehicle_earliest_start_hour}')
        print(f'  - vehicle_latest_start_hour: {self.config.vehicle_latest_start_hour}')
        print(f'  - service_time_minutes: {self.config.service_time_minutes}')
        print(f'  - max_route_duration_hours: {self.config.max_route_duration_hours}')
        print(f'  - slack_time_seconds: {self.config.slack_time_seconds}')
        print(f'  - vehicle_capacity_slack: {self.config.vehicle_capacity_slack}')
        print(f'  - optimization_time_limit_seconds: {self.config.optimization_time_limit_seconds}')

        self.route_datum = date

        # Fetch delivery orders and add depot
        verzend_opties = VerzendOpties.objects.filter(
            verzenddatum=date,
            verzendoptie__icontains="Bezorging"
        ).values_list('id', flat=True)

        depot_order = Orders.objects.get(pk=self.config.depot_order_id)
        orders = [depot_order] + list(Orders.objects.filter(
            afleverdatum=date_obj,
            verzendoptie_id__in=verzend_opties
        ))

        vehicles = Vehicle.objects.filter(capacity__gt=0)

        print(f'\n=== Problem Size ===')
        print(f'Orders (including depot): {len(orders)}')
        print(f'Customer orders: {len(orders) - 1}')
        print(f'Vehicles available: {vehicles.count()}')

        # Create matrices
        distance_matrix = self.create_distance_matrix(orders)
        if distance_matrix is False:
            print('Failed to create distance matrix')
            return False

        travel_time_matrix = self.create_travel_time_matrix(distance_matrix)

        # Calculate demands using config
        demands = [self.config.calculate_demand(order.orderprijs, order.pk) for order in orders]
        total_demand = sum(demands)
        total_capacity = sum([v.capacity for v in vehicles])

        print(f'Total demand: {total_demand}')
        print(f'Total capacity: {total_capacity}')
        print(f'Capacity utilization: {(total_demand / total_capacity * 100):.1f}%')

        # Prepare VRP data
        data = {
            "distance_matrix": distance_matrix,
            "travel_times": travel_time_matrix,
            "demands": demands,
            "vehicle_capacities": [vehicle.capacity for vehicle in vehicles],
            "num_vehicles": vehicles.count(),
            "depot": 0,
        }

        # Set time windows
        data['time_windows'] = [
            self.config.get_time_window_seconds(is_depot=(idx == 0))
            for idx in range(len(data['distance_matrix']))
        ]

        # FIXED: Set service times - depot has 0, customers have configured service time
        data["service_times"] = [0] + [self.config.get_service_time_seconds()] * (len(orders) - 1)
        print(f'Service times: Depot=0s, Customers={self.config.get_service_time_seconds()}s')

        # Solve VRP
        solution = self.solve_vrp(data)

        if solution:
            print('Solution found, saving routes to database...')
            self.save_routes_to_db(orders, vehicles, solution, data, date_obj)
            return True
        else:
            print('No solution found for the given constraints')
            return False

    def solve_vrp(self, data: Dict) -> Optional[Dict]:
        """
        Solve the Vehicle Routing Problem using Google OR-Tools.

        Args:
            data: Dictionary containing VRP problem data

        Returns:
            Dictionary with manager, routing, and solution if successful, None otherwise
        """
        # manager = pywrapcp.RoutingIndexManager(
        #     len(data["distance_matrix"]),
        #     data["num_vehicles"],
        #     data["depot"]
        # )
        # routing = pywrapcp.RoutingModel(manager)
        # Create start and end depot arrays (all vehicles use same depot)
        starts = [data["depot"]] * data["num_vehicles"]
        ends = [data["depot"]] * data["num_vehicles"]

        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]),
            data["num_vehicles"],
            starts,
            ends
        )
        routing = pywrapcp.RoutingModel(manager)

        # Disjunctions allow the solver to skip stops if needed, but we penalize heavily
        penalty = 100000000  # Very high penalty = must visit all stops
        for node in range(1, len(data["distance_matrix"])):  # Skip depot
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

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
            demand_callback_index,
            self.config.vehicle_capacity_slack,
            data["vehicle_capacities"],
            True,
            "Capacity"
        )

        # FIXED: Time callback with service time at DESTINATION (not origin)
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel = data["travel_times"][from_node][to_node]
            # Service time happens at the destination where we perform service
            return travel + data["service_times"][to_node]

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        # Time dimension with depot return setting
        routing.AddDimension(
            time_callback_index,
            self.config.slack_time_seconds,
            self.config.get_max_route_duration_seconds(),
            self.config.force_depot_return,  # CRITICAL: Force return to depot
            "Time"
        )

        time_dimension = routing.GetDimensionOrDie("Time")

        # Set time windows for all location nodes (depot + customers)
        for idx, time_window in enumerate(data["time_windows"]):
            index = manager.NodeToIndex(idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        depot_window = data["time_windows"][0]
        for vehicle_id in range(data["num_vehicles"]):
            end_index = routing.End(vehicle_id)
            time_dimension.CumulVar(end_index).SetRange(depot_window[0], depot_window[1])

        # Set vehicle start times
        start_range = self.config.get_vehicle_start_window_seconds()
        for vehicle_id in range(data["num_vehicles"]):
            start_index = routing.Start(vehicle_id)
            time_dimension.CumulVar(start_index).SetRange(start_range[0], start_range[1])

        # Set fixed cost per vehicle
        routing.SetFixedCostOfAllVehicles(self.config.vehicle_fixed_cost)

        # Configure search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = self.config.get_first_solution_strategy_enum()
        search_parameters.local_search_metaheuristic = self.config.get_local_search_metaheuristic_enum()
        search_parameters.solution_limit = 20000  # Don't stop at first solution
        print(f'search_parameters.first_solution_strategy: {self.config.first_solution_strategy}')
        print(f'search_parameters.local_search_metaheuristic: {self.config.local_search_metaheuristic}')
        search_parameters.time_limit.seconds = self.config.optimization_time_limit_seconds
        search_parameters.log_search = True

        print(f'\nStarting optimization (time limit: {self.config.optimization_time_limit_seconds}s)...')
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            return {
                "manager": manager,
                "routing": routing,
                "solution": solution,
            }
        return None

    def create_distance_matrix(self, orders: List[Orders]) -> List[List[int]]:
        """Generate the distance matrix from the DistanceMatrix model."""
        matrix = []
        for origin in orders:
            row = []
            for destination in orders:
                try:
                    distance = self.haversine((origin.latitude, origin.longitude),
                                              (destination.latitude, destination.longitude))
                    row.append(int(distance))
                except Exception as e:
                    try:
                        if origin.conversieID == 99999:
                            origin = Orders.objects.get(conversieID=origin.conversieID,
                                                        afleverdatum=destination.afleverdatum)
                            distance = DistanceMatrix.objects.get(origin=origin,
                                                                  destination=destination).distance_meters
                            row.append(distance)
                        elif destination.conversieID == 99999:
                            destination = Orders.objects.get(conversieID=destination.conversieID,
                                                             afleverdatum=origin.afleverdatum)
                            distance = DistanceMatrix.objects.get(origin=origin,
                                                                  destination=destination).distance_meters
                            row.append(distance)
                        else:
                            print('DM exception: ', e)
                            try:
                                distance = DistanceMatrix.objects.get(origin=origin.conversieID,
                                                                      destination=destination.conversieID).distance_meters
                                row.append(distance)
                            except Exception as e:
                                try:
                                    distance = self.haversine((origin.latitude, origin.longitude),
                                                              (destination.latitude, destination.longitude))

                                    row.append(distance)
                                    print('created', origin, destination)
                                except Exception as e:
                                    print(
                                        f"Error fetching distance from Google Maps for origin {origin.id} and destination {destination.id}: {e}")

                    except MultipleObjectsReturned:
                        distance = DistanceMatrix.objects.filter(origin=origin, destination=destination)[
                            0].distance_meters
                        row.append(distance)
                    except DistanceMatrix.DoesNotExist:
                        print('doesnt exist', origin, destination)
                        try:
                            distance = DistanceMatrix.objects.filter(origin__conversieID=origin.conversieID,
                                                                     destination__conversieID=destination.conversieID)[
                                0].distance_meters
                            row.append(distance)
                        except Exception as e:
                            try:
                                distance = self.haversine((origin.latitude, origin.longitude),
                                                          (destination.latitude, destination.longitude))
                                row.append(distance)
                                print('created', origin, destination)
                            except Exception as e:
                                print(
                                    f"Error fetching distance from Google Maps for origin {origin.id} and destination {destination.id}: {e}")

            matrix.append(row)
        return matrix

    def haversine(self, coord1, coord2):
        """Calculate the Haversine distance between two points in meters."""
        # Radius of the Earth in meters
        R = 6371000.0

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance * self.config.haversine_road_multiplier

    def create_travel_time_matrix(self, distance_matrix: List[List[int]]) -> List[List[int]]:
        """
        Generate travel time matrix based on distance matrix and configured average speed.

        Args:
            distance_matrix: 2D list of distances in meters

        Returns:
            2D list of travel times in seconds
        """
        average_speed_ms = (self.config.average_speed_kmh * 1000) / 3600  # Convert km/h to m/s
        travel_time_matrix = [
            [int(distance / average_speed_ms) for distance in row]
            for row in distance_matrix
        ]
        return travel_time_matrix

    def save_routes_to_db(self, orders: List[Orders], vehicles: List[Vehicle],
                          solution: Dict, data: Dict, date_obj) -> None:
        """
        Save calculated routes and stops to the database.

        Args:
            orders: List of orders
            vehicles: List of vehicles
            solution: Solution dictionary from solver
            data: VRP data dictionary
            date_obj: Date object for the routes
        """
        manager = solution["manager"]
        routing = solution["routing"]
        vrp_solution = solution["solution"]
        time_dimension = routing.GetDimensionOrDie("Time")

        # Clear old routes for this date
        Route.objects.filter(date=self.route_datum).delete()

        total_distance = 0
        routes_created = 0

        # Create routes for each vehicle
        for vehicle_id in range(data["num_vehicles"]):
            route_distance = 0
            route_stops = []

            index = routing.Start(vehicle_id)

            # Check if vehicle is actually used
            if routing.IsEnd(vrp_solution.Value(routing.NextVar(index))):
                continue  # Skip unused vehicles

            # Get departure time from depot (start of route)
            # start_time_seconds = vrp_solution.Min(time_dimension.CumulVar(index))
            # departure_time = self._seconds_to_time(start_time_seconds)

            # Calculate actual departure time from first customer arrival
            # We need to find when the vehicle actually needs to leave
            first_customer_index = routing.Start(vehicle_id)
            next_index = vrp_solution.Value(routing.NextVar(first_customer_index))
            next_node = manager.IndexToNode(next_index)
            first_customer_arrival = vrp_solution.Min(time_dimension.CumulVar(next_index))

            # Calculate departure time: first customer arrival - travel time to first customer
            travel_time_to_first = data["travel_times"][0][next_node]
            actual_departure_seconds = first_customer_arrival - travel_time_to_first
            departure_time = self._seconds_to_time(actual_departure_seconds)

            # Create route
            route = Route.objects.create(
                name=f"Route {self.route_datum} - Vehicle {vehicle_id + 1}",
                vehicle=vehicles[vehicle_id],
                date=date_obj,
                departure_time=departure_time
            )
            routes_created += 1

            sequence_number = 0

            # Build route stops
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                order = orders[node_index]
                route_stops.append((float(order.latitude), float(order.longitude)))

                # Get timing information for this stop
                # arrival_time_seconds = vrp_solution.Min(time_dimension.CumulVar(index))
                # arrival_time = self._seconds_to_time(arrival_time_seconds)
                #
                # # Departure time = arrival time + service time
                # service_time_seconds = data["service_times"][node_index]
                # departure_time_seconds = arrival_time_seconds + service_time_seconds
                # stop_departure_time = self._seconds_to_time(departure_time_seconds)

                # Get timing information for this stop
                # For depot (first stop), use calculated actual departure time
                if sequence_number == 0:
                    arrival_time_seconds = actual_departure_seconds
                    departure_time_seconds = actual_departure_seconds  # Depot has 0 service time
                else:
                    arrival_time_seconds = vrp_solution.Min(time_dimension.CumulVar(index))
                    service_time_seconds = data["service_times"][node_index]
                    departure_time_seconds = arrival_time_seconds + service_time_seconds

                arrival_time = self._seconds_to_time(arrival_time_seconds)
                stop_departure_time = self._seconds_to_time(departure_time_seconds)

                # Calculate distance to next stop
                next_index = vrp_solution.Value(routing.NextVar(index))
                if not routing.IsEnd(next_index):
                    next_node_index = manager.IndexToNode(next_index)
                    distance_to_next = data["distance_matrix"][node_index][next_node_index]
                    route_distance += distance_to_next

                # Create stop with timing information
                Stop.objects.create(
                    order=order,
                    route=route,
                    sequence_number=sequence_number,
                    arrival_time=arrival_time,
                    departure_time=stop_departure_time
                )

                sequence_number += 1
                index = next_index

            # Get end time of route (at last stop or back at depot if force_depot_return is True)
            if self.config.force_depot_return:
                # If we return to depot, get the time at the end node
                end_index = routing.End(vehicle_id)
                end_time_seconds = vrp_solution.Min(time_dimension.CumulVar(end_index))
            else:
                # If we don't return, the end time is at the last customer stop
                # We already have this from the last iteration of the loop
                end_time_seconds = departure_time_seconds

            # Calculate total travel time
            # total_seconds = end_time_seconds - start_time_seconds
            total_seconds = end_time_seconds - actual_departure_seconds

            # Convert to time for total_travel_time (HH:MM:SS format)
            # For durations longer than 24 hours, this will wrap around
            # If you need to handle routes > 24 hours, consider using DurationField instead
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            total_travel_time = time(hour=min(hours, 23), minute=minutes, second=seconds)

            # Save route details
            route_distance_km = route_distance / 1000.0
            route.total_distance = route_distance_km  # FIXED: Changed from total_distance_km to total_distance
            route.total_travel_time = total_travel_time
            total_distance += route_distance

            # Generate Google Maps link
            google_maps_link = self.create_google_maps_link(route_stops)
            route.google_maps_link = google_maps_link
            route.save()

            # Print route summary
            print(f"Route {vehicle_id + 1}: {route_distance_km:.2f} km with {sequence_number} stops")
            print(f"  Departure: {departure_time}, Total Time: {total_travel_time}")
            print(f"  Google Maps: {google_maps_link}")

        total_distance_km = total_distance / 1000.0
        print(f"\n=== Summary ===")
        print(f"Routes created: {routes_created}")
        print(f"Total distance: {total_distance_km:.2f} km")
        if routes_created > 0:
            print(f"Average per route: {total_distance_km / routes_created:.2f} km")

    def create_google_maps_link(self, route_stops: List[Tuple[float, float]], max_waypoints: int = 25) -> str:
        """
        Create a Google Maps link with up to max_waypoints stops.

        Args:
            route_stops: List of (latitude, longitude) tuples
            max_waypoints: Maximum waypoints to include (default 25)

        Returns:
            Google Maps directions URL
        """
        base_url = "https://www.google.com/maps/dir/"

        # Take only the first max_waypoints stops
        limited_stops = route_stops[:max_waypoints]
        waypoints = "/".join([f"{lat},{lng}" for lat, lng in limited_stops])

        return base_url + waypoints
