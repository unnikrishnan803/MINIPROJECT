
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Restaurant, FoodItem, Order
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

def test_dashboard_logic():
    print("Setting up test users...")
    # Clean up previous run
    User.objects.filter(username__in=['testd1', 'testd2']).delete()

    # Create User 1 (Restaurant)
    u1 = User.objects.create_user(username='testd1', password='password123', role='restaurant')
    r1 = Restaurant.objects.create(user=u1, name="Test Rest 1", location="Loc 1")
    
    # Create User 2 (Restaurant)
    u2 = User.objects.create_user(username='testd2', password='password123', role='restaurant')
    r2 = Restaurant.objects.create(user=u2, name="Test Rest 2", location="Loc 2")

    # Create Items
    f1 = FoodItem.objects.create(restaurant=r1, name="Item 1", price=10, category="Test")
    f2 = FoodItem.objects.create(restaurant=r2, name="Item 2", price=20, category="Test")

    client = APIClient()
    
    # --- Test 1: Food Item Isolation ---
    print("\nTest 1: Food Item Isolation")
    client.force_authenticate(user=u1)
    response = client.get('/api/food-items/')
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', data) # Handle pagination if active
        print(f"User 1 sees {len(results)} items.")
        if len(results) == 1 and results[0]['name'] == "Item 1":
            print("PASS: User 1 sees only their own item.")
        else:
            print(f"FAIL: User 1 saw: {results}")
    else:
        print(f"FAIL: API Error {response.status_code}")

    # --- Test 2: Dashboard Context ---
    # Note: APIClient.get on a TemplateView renders the template. 
    # We can check the context if we use django.test.Client, but APIClient inherits from it.
    print("\nTest 2: Dashboard Stats (Context)")
    
    # Create an order for User 1
    Order.objects.create(restaurant=r1, total_amount=50, status='Paid')
    
    response = client.get('/dashboard/')
    if response.status_code == 200:
        context = response.context
        if context:
            print(f"Total Orders: {context.get('total_orders')}")
            print(f"Revenue: {context.get('revenue')}")
            
            if context.get('total_orders') == 1 and context.get('revenue') == 50:
                print("PASS: Dashboard context has correct stats.")
            else:
                 print(f"FAIL: Stats mismatch. Orders: {context.get('total_orders')}, Rev: {context.get('revenue')}")
        else:
            print("FAIL: No context returned (TemplateResponse?)")
    else:
        print(f"FAIL: Dashboard load error {response.status_code}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    test_dashboard_logic()
