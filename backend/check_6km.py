import os
import sys
import django
from math import radians, sin, cos, sqrt, asin

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def simulate_6km_away():
    # Grill and Chill Coords
    # Lat: 9.6902, Lng: 76.3422
    
    # Create a user location approx 6km away
    # 1 deg lat = 111km. 6km = 6/111 = 0.054 deg
    user_lat = 9.6902 + 0.054 # North
    user_lng = 76.3422
    
    print(f"Simulating User Location (approx 6km away): {user_lat:.4f}, {user_lng:.4f}")
    
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
        
        if distance <= 100.0: # New default
             print(f"MATCH: {r.name:<20} | Dist: {distance:.2f}km")
             count += 1
        else:
             print(f"SKIP : {r.name:<20} | Dist: {distance:.2f}km")

if __name__ == "__main__":
    simulate_6km_away()
