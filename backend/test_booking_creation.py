import os
import sys
import django

# Setup Django
sys.path.append('d:\\Mini project\\deliciae\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Restaurant, User, Booking

User = get_user_model()

def test_booking_creation():
    print("Setting up test data...")
    # Create or get a customer
    customer, _ = User.objects.get_or_create(username='test_customer', email='test@example.com', role='customer')
    customer.set_password('pass123')
    customer.save()
    
    # Create or get a restaurant
    rest_user, _ = User.objects.get_or_create(username='test_rest', email='rest@example.com', role='restaurant')
    rest_user.set_password('pass123')
    rest_user.save()
    
    restaurant, _ = Restaurant.objects.get_or_create(user=rest_user, defaults={
        'name': 'Test Bistro',
        'location': 'Kochi',
        'cuisine_type': 'Italian'
    })
    
    # Initialize API Client
    client = APIClient(enforce_csrf_checks=False)
    client.force_login(user=customer)
    
    print(f"Customer: {customer.username} (ID: {customer.id})")
    print(f"Attempting to book at {restaurant.name} (ID: {restaurant.id})...")
    
    data = {
        'restaurant': restaurant.id,
        'date_time': '2026-05-20T19:00:00Z',
        'people_count': 2
    }
    
    response = client.post('/api/bookings/', data, format='json')
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 201:
        print("Booking Created Successfully!")
        print(response.data)
        
        # Verify in DB
        booking = Booking.objects.get(id=response.data['id'])
        print(f"Verified in DB: Booking {booking.id} for {booking.customer.username} at {booking.restaurant.name}")
        
    else:
        print("Failed to create booking.")
        print(response.content)

if __name__ == "__main__":
    test_booking_creation()
