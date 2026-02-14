
import os
import django
from django.test import RequestFactory
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deliciae_core.settings")
django.setup()

from core.views import RestaurantViewSet
from core.models import Restaurant

def verify_list_api():
    print("--- Verifying Restaurant List API ---")
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/api/restaurants/')
    
    # Initialize ViewSet
    view = RestaurantViewSet.as_view({'get': 'list'})
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response Data found.")
            # Check if paginated
            data = response.data
            if 'results' in data:
                print(f"Paginated response. Count: {data['count']}")
                results = data['results']
            else:
                print(f"List response. Count: {len(data)}")
                results = data
                
            if len(results) > 0:
                print(f"First restaurant: {results[0]['name']}")
            else:
                print("No restaurants found.")
                
            print("API Verification SUCCESS")
        else:
            print(f"API Failed: {response.status_code}")
            print(response.data)
            
    except Exception as e:
        print(f"API Exception: {e}")

if __name__ == "__main__":
    verify_list_api()
