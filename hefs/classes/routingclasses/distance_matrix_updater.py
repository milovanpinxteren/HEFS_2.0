import time

import googlemaps
from django.conf import settings

from hefs.models import Orders, DistanceMatrix, VerzendOpties


class DistanceMatrixUpdater:
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



        return "Distance Matrix Updated"



