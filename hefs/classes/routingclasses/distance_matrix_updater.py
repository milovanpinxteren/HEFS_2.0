import time

import googlemaps
from django.conf import settings

from hefs.models import Orders, DistanceMatrix, VerzendOpties


class DistanceMatrixUpdater:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def chunks(self, data, size=25):
        dict_items = list(data.items())
        return [dict(dict_items[i:i + size]) for i in range(0, len(dict_items), size)]


    def update_distances(self):
        """
        Update the distance matrix using Google Maps API for orders on the same date.
        Exclude locations for which data already exists.
        """
        # Get all unique delivery dates
        verzendopties = VerzendOpties.objects.filter(verzendoptie__icontains="Bezorging")

        for verzendoptie in verzendopties:
            # Fetch all orders linked to this VerzendOptie
            orders = Orders.objects.filter(verzendoptie=verzendoptie)
            geolocations = {order.id: (float(order.latitude), float(order.longitude)) for order in orders if
                            order.latitude and order.longitude}

            # Get existing distances for this date
            existing_distances = DistanceMatrix.objects.filter(
                origin__verzendoptie=verzendoptie,
                destination__verzendoptie=verzendoptie,
            ).values_list("origin_id", "destination_id")

            # Exclude already calculated distances
            existing_distance_set = set(existing_distances)
            geolocation_chunks = self.chunks(geolocations)

            all_distances_dict = {}
            call_counter = 0
            for origin_id, origin_coords in geolocations.items():
                location_distance_dict = {}
                for chunk in geolocation_chunks:
                    # Exclude destinations with existing distances
                    destinations = [
                        (dest_id, coords) for dest_id, coords in chunk.items()
                        if (origin_id, dest_id) not in existing_distance_set
                    ]
                    if not destinations:
                        continue

                    # Prepare destinations for the API
                    destination_coords = [coords for _, coords in destinations]
                    print('google api call counter: ', call_counter)
                    call_counter += 1

                    # Fetch distances from Google Maps
                    try:
                        gmaps_response = self.gmaps.distance_matrix(
                            origins=[origin_coords],
                            destinations=destination_coords,
                            mode="driving",
                        )
                        time.sleep(1)  # Avoid hitting API rate limits

                        # Parse response
                        for idx, distance_row in enumerate(gmaps_response["rows"][0]["elements"]):
                            dest_id = destinations[idx][0]
                            if distance_row["status"] == "OK":
                                distance = distance_row["distance"]["value"]
                                location_distance_dict[dest_id] = distance
                            else:
                                location_distance_dict[dest_id] = float("inf")

                    except Exception as e:
                        print(f"Error fetching distances for origin {origin_id}: {e}")
                        continue

                all_distances_dict[origin_id] = location_distance_dict

            # Save distances for this date
            self.save_distances(all_distances_dict)

        return "Distance Matrix Updated"

    # def update_distances(self):
    #     self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    #     geolocations = {}
    #
    #     locations = Orders.objects.all()
    #     for location in list(locations):
    #         geolocations[location.id] = {'lat': float(location.latitude), 'lon': float(location.longitude)}
    #
    #     geolocation_chunks = self.chunks(geolocations)
    #     all_distances_dict = {}
    #     for origin_location_id, origin_info in geolocations.items():
    #         location_distance_dict = {}
    #         for chunk in geolocation_chunks:
    #             destinations = [(destination_info['lat'], destination_info['lon'])
    #                             for destination_id, destination_info in chunk.items()]
    #             gmaps_response = self.gmaps.distance_matrix((origin_info['lat'], origin_info['lon']), destinations,
    #                                                    mode="driving")
    #             time.sleep(1)
    #             for index, distance_row in enumerate(gmaps_response['rows'][0]['elements']):
    #                 destination_id = list(chunk.keys())[index]
    #                 if distance_row['status'] == 'OK':
    #                     distance = distance_row['distance']['value']
    #                     location_distance_dict[destination_id] = distance
    #                 else:
    #                     location_distance_dict[destination_id] = float('inf')
    #         all_distances_dict[origin_location_id] = location_distance_dict
    #
    #     self.save_distances(all_distances_dict)
    #     return 'Distance Matrix Updated'

    def save_distances(self, all_distances_dict):
        for origin_id, destinations in all_distances_dict.items():
            origin = Orders.objects.get(id=origin_id)
            for destination_id, distance in destinations.items():
                destination = Orders.objects.get(id=destination_id)
                DistanceMatrix.objects.update_or_create(origin=origin, destination=destination,
                                                        defaults={'distance_meters': distance})
        return 'Distances saved'
