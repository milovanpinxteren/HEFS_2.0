import time

import googlemaps
from django.conf import settings

from hefs.models import Orders


class CoordinateCalculator:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def geocode_address(self, address):
        """
        Geocode the given address using Google Maps API.
        :param address: str
        :return: tuple (latitude, longitude) or None
        """
        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return location['lat'], location['lng']
        except Exception as e:
            print(f"Error during geocoding: {e}")
        return None

    def calculate_coordinates(self):
        orders = Orders.objects.filter(latitude__isnull=True, longitude__isnull=True)
        for order in orders:
            if order.huisnummer:
                address = f"{order.straatnaam} {order.huisnummer}, {order.postcode} {order.plaats}, {order.land}"
            else:
                address = f"{order.straatnaam}, {order.postcode} {order.plaats}, {order.land}"
            print(address)
            try:
                time.sleep(1)
                coordinates = self.geocode_address(address)
                print(coordinates)
                order.latitude = coordinates[0]
                order.longitude = coordinates[1]
                order.save()
            except Exception as e:
                print(f"Error during geocoding: {e}")

