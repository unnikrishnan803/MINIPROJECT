import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def check_restaurant():
    try:
        # Check for all matches
        restaurants = Restaurant.objects.filter(name__icontains="Grill and Chill")
        
        print(f"Found {restaurants.count()} restaurants matching 'Grill and Chill':")
        
        for r in restaurants:
            print(f"--- ID: {r.id} ---")
            print(f"Name: {r.name}")
            print(f"Location Text: {r.location}")
            print(f"Coords: {r.latitude}, {r.longitude}")
            print(f"Is Open: {r.is_open}")
            print(f"Open Time: {r.opening_time}")
            print(f"Close Time: {r.closing_time}")
            print("------------------")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_restaurant()
