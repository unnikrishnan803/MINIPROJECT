import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deliciae_core.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Restaurant, Table

User = get_user_model()
client = Client()

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Setup Data
    username = "verify_user"
    password = "password123"
    email = "verify@example.com"
    
    user, created = User.objects.get_or_create(username=username, email=email)
    user.set_password(password)
    user.role = 'customer'
    user.save()
        
    print(f"User {username} ready.")
    
    # Get a restaurant
    restaurant = Restaurant.objects.first()
    if not restaurant:
        print("No restaurant found. Creating one.")
        r_user = User.objects.create_user('rest_owner', 'owner@example.com', 'password')
        r_user.role = 'restaurant'
        r_user.save()
        restaurant = Restaurant.objects.create(
            user=r_user, 
            name="Test Restaurant", 
            location="Kochi",
            is_open=True
        )
    print(f"Using Restaurant: {restaurant.name} (ID: {restaurant.id})")
    
    # Ensure tables
    table, t_created = Table.objects.get_or_create(
        restaurant=restaurant,
        table_number=101,
        defaults={'capacity': 4, 'status': 'Available'}
    )
    print(f"Table 101 ready: {table.status}")
    
    # 2. Login
    client.force_login(user)
    print("Logged in.")
    
    # 3. Test Restaurant Detail API
    print(f"Fetching restaurant details for ID {restaurant.id}...")
    resp = client.get(f'/api/restaurants/{restaurant.id}/')
    if resp.status_code == 200:
        print("Restaurant Detail API success.")
        data = resp.json()
        if data['name'] == restaurant.name:
            print("Restaurant name matches.")
        else:
            print(f"Name mismatch: {data['name']}")
    else:
        print(f"Restaurant Detail API failed: {resp.status_code}")
        print(resp.content)
        
    # 4. Test Table Fetching API
    print("Fetching tables for restaurant...")
    resp = client.get(f'/api/tables/?restaurant={restaurant.id}')
    if resp.status_code == 200:
        tables = resp.json()
        print(f"Table Fetch API success. Found {len(tables)} tables.")
        # Check if our table is in the list
        found = False
        if isinstance(tables, list): # ListSerializer
            found = any(t['id'] == table.id for t in tables)
        elif 'results' in tables: # Pagination
            found = any(t['id'] == table.id for t in tables['results'])
            
        if found:
            print("Created table found in response.")
        else:
            print("Created table NOT found in response.")
            print(tables)
    else:
        print(f"Table Fetch API failed: {resp.status_code}")
        print(resp.content)

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
