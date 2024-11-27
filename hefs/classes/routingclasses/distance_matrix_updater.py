import time

import googlemaps
from django.conf import settings

from hefs.models import Orders, DistanceMatrix


class DistanceMatrixUpdater:
    def chunks(self, data, size=25):
        dict_items = list(data.items())
        return [dict(dict_items[i:i + size]) for i in range(0, len(dict_items), size)]

    def update_distances(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        geolocations = {}

        locations = Orders.objects.all()
        for location in list(locations):
            geolocations[location.id] = {'lat': float(location.latitude), 'lon': float(location.longitude)}

        geolocation_chunks = self.chunks(geolocations)
        all_distances_dict = {}
        for origin_location_id, origin_info in geolocations.items():
            location_distance_dict = {}
            for chunk in geolocation_chunks:
                destinations = [(destination_info['lat'], destination_info['lon'])
                                for destination_id, destination_info in chunk.items()]
                gmaps_response = self.gmaps.distance_matrix((origin_info['lat'], origin_info['lon']), destinations,
                                                       mode="driving")
                time.sleep(1)
                for index, distance_row in enumerate(gmaps_response['rows'][0]['elements']):
                    destination_id = list(chunk.keys())[index]
                    if distance_row['status'] == 'OK':
                        distance = distance_row['distance']['value']
                        location_distance_dict[destination_id] = distance
                    else:
                        location_distance_dict[destination_id] = float('inf')
            all_distances_dict[origin_location_id] = location_distance_dict

        self.save_distances(all_distances_dict)
        return 'Distance Matrix Updated'

    def save_distances(self, all_distances_dict):
        for origin_id, destinations in all_distances_dict.items():
            origin = Orders.objects.get(id=origin_id)
            for destination_id, distance in destinations.items():
                destination = Orders.objects.get(id=destination_id)
                DistanceMatrix.objects.update_or_create(origin=origin, destination=destination,
                                                        defaults={'distance_meters': distance})
        return 'Distances saved'
