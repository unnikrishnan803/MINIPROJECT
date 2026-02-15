import os
import sys
import django
from math import radians, sin, cos, sqrt, asin

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def simulate_search(user_lat, user_lng, radius_km=20.0):
    print(f"User Location: {user_lat}, {user_lng} | Radius: {radius_km}km")
    
    degrees_delta = radius_km / 111.0 * 1.1
    lat_min = user_lat - degrees_delta
    lat_max = user_lat + degrees_delta
    lng_min = user_lng - degrees_delta
    lng_max = user_lng + degrees_delta
    
    print(f"Bounding Box: Lat {lat_min:.4f}-{lat_max:.4f}, Lng {lng_min:.4f}-{lng_max:.4f}")
    
    candidates = Restaurant.objects.filter(
        latitude__range=(lat_min, lat_max),
        longitude__range=(lng_min, lng_max),
        is_open=True
    )
    
    print(f"Candidates found in box: {candidates.count()}")
    
    matching_restaurants = []

    for r in candidates:
        if r.latitude is None or r.longitude is None:
            continue
            
        lon1, lat1, lon2, lat2 = map(radians, [user_lng, user_lat, r.longitude, r.latitude])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = c * 6371
        
        print(f"Restaurant: {r.name}, Coords: {r.latitude},{r.longitude}, Dist: {distance:.2f}km")
        
        if distance <= radius_km:
            print(f"  MATCH: {r.name} is within range. Dist: {distance:.2f}km")
            matching_restaurants.append(r)
        else:
            print(f"  SKIP: {r.name} is too far. Dist: {distance:.2f}km")
    
    print(f"\nTotal matches found: {len(matching_restaurants)}")
    return matching_restaurants

if __name__ == "__main__":
    # Test with approximate user location (derived from restaurant location + 6km)
    # Restaurant: 9.6902, 76.3422
    # User roughly 9.74, 76.34 (approx 5-6km north)
    # User roughly 9.74, 76.34 (approx 5-6km north) -> Should PASS with 20km
    simulate_search(9.7400, 76.3422, 20.0)
    print("-" * 20)
    # User closer (approx 1km north) -> Should PASS
    # 1km = 0.009 deg
    simulate_search(9.6990, 76.3422, 20.0)
