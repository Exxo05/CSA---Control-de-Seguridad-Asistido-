# utils/helpers.py
from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="csa_app")

def geocode_address(address, retries=2):
    for i in range(retries+1):
        try:
            loc = geolocator.geocode(address, timeout=10)
            if loc:
                return loc.latitude, loc.longitude
            return None, None
        except Exception:
            time.sleep(1)
    return None, None
