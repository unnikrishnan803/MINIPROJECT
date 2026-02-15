import os
import django
import sys

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def check_restaurants():
    print("Checking Restaurants...")
    restaurants = Restaurant.objects.all()
    for r in restaurants:
        print(f"Name: {r.name}")
        print(f"  Location Text: {r.location}")
        print(f"  Coords: {r.latitude}, {r.longitude}")
        print(f"  Is Open: {r.is_open}")
        print("-" * 20)

if __name__ == "__main__":
    check_restaurants()
