import requests
import sys
import os
import django
from math import radians, sin, cos, sqrt, asin

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def get_coords_from_url(url):
    print(f"Resolving URL: {url}")
    try:
        resp = requests.get(url, allow_redirects=True)
        print(f"Final URL: {resp.url}")
        
        # Extract from URL like .../maps/place/.../@9.7083475,76.3077629,17z/...
        # or ...?q=9.7083475,76.3077629...
        import re
        # Look for @lat,lng
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', resp.url)
        if match:
            return float(match.group(1)), float(match.group(2))
            
        # Look for q=lat,lng
        match = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', resp.url)
        if match:
            return float(match.group(1)), float(match.group(2))
            
        # Look for !3d and !4d (Google Maps embed style)
        # !3d9.7083475!4d76.3077629
        lat_match = re.search(r'!3d(-?\d+\.\d+)', resp.url)
        lng_match = re.search(r'!4d(-?\d+\.\d+)', resp.url)
        if lat_match and lng_match:
             return float(lat_match.group(1)), float(lng_match.group(1))
             
        print("Could not extract coordinates with regex.")
        return None, None
    except Exception as e:
        print(f"Error resolving URL: {e}")
        return None, None

def simulate_search(user_lat, user_lng, radius_km=100.0):
    print(f"\nSimulating Search from: {user_lat}, {user_lng} | Radius: {radius_km}km")
    
    candidates = Restaurant.objects.filter(is_open=True)
    count = 0
    
    for r in candidates:
        if r.latitude is None or r.longitude is None:
            continue
            
        lon1, lat1, lon2, lat2 = map(radians, [user_lng, user_lat, r.longitude, r.latitude])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = c * 6371
        
        if distance <= radius_km:
            print(f"MATCH: {r.name:<20} | Dist: {distance:.2f}km | Loc: {r.location}")
            count += 1
        else:
            print(f"SKIP : {r.name:<20} | Dist: {distance:.2f}km (Too Far)")
            
    if count == 0:
        print("No restaurants found within range.")

if __name__ == "__main__":
    url = "https://maps.app.goo.gl/XNJvbJkXpRa3ZWKw5"
    lat, lng = get_coords_from_url(url)
    
    if lat and lng:
        print(f"Extracted Coords: Lat {lat}, Lng {lng}")
        simulate_search(lat, lng)
    else:
        print("Failed to get coordinates.")
