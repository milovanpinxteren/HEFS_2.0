import time

import googlemaps
from django.conf import settings

from hefs.models import Orders
import requests
import re

# Latitude: ~ 50.6° to 53.7°
# Longitude: ~ 3.2°E to 7.3°E

class CoordinateCalculator:
    def geocode_pdok(self, address):
        """
        PDOK geocoder that can handle either 'Kerkstraat 12, 1234AB Plaats'
        or 'Kerkstraat, 1234AB Plaats' (huisnummer optional)
        """
        try:
            # Try to extract pieces for better precision
            straat, huisnr, postcode, plaats = self._parse_dutch_address(address)

            # Prefer postcode + huisnr, fallback to full address text
            if postcode and huisnr:
                q = f"{postcode} {huisnr}"
            elif straat and plaats:
                q = f"{straat} {plaats}"
            else:
                q = address

            url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
            params = {"q": q, "rows": 1, "fl": "centroide_ll"}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()

            docs = r.json().get("response", {}).get("docs", [])
            if not docs:
                return None

            m = re.search(r"POINT\(([-0-9.]+)\s+([-0-9.]+)\)", docs[0].get("centroide_ll", ""))
            if m:
                lat, lon = float(m.group(2)), float(m.group(1))
                return lat, lon
        except Exception as e:
            print(f"[PDOK geocode error] {e}")
        return None

    def _parse_dutch_address(self, address):
        """Return (straat, huisnr, postcode, plaats) if we can extract them."""
        address = (address or "").strip()
        straat, huisnr, postcode, plaats = "", "", "", ""

        # Basic postcode pattern: 4 digits + 2 letters
        m_post = re.search(r"(\d{4}\s?[A-Za-z]{2})", address)
        if m_post:
            postcode = m_post.group(1).replace(" ", "")
            parts = address.split(m_post.group(0))
            left = parts[0].strip(", ")
            right = parts[1].strip(", ") if len(parts) > 1 else ""

            # Try to find house number in left side
            m_hn = re.search(r"(\d{1,4}\w?)", left)
            if m_hn:
                huisnr = m_hn.group(1)
                straat = left.replace(huisnr, "").strip()
            else:
                straat = left

            plaats = right.split(",")[0] if right else ""
        return straat, huisnr, postcode, plaats


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
                # coordinates = self.geocode_address(address)
                coordinates = self.geocode_pdok(address)
                print(coordinates)
                order.latitude = coordinates[0]
                order.longitude = coordinates[1]
                order.save()
            except Exception as e:
                print(f"Error during geocoding: {e}")
