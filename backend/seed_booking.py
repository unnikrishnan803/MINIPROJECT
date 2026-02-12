import os
import django
import sys
from django.utils import timezone

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Table, Booking, Restaurant

try:
    # Get Restaurant
    restaurant = Restaurant.objects.get(name='Liberty Burger')
    print(f"Restaurant: {restaurant.name}")
    
    # Get Table 1
    table = Table.objects.get(restaurant=restaurant, table_number=1)
    
    # Get Customer (let's use the restaurant user itself or create a dummy one)
    # We'll check if a customer exists, else create one
    customer, created = User.objects.get_or_create(username='hungry_diner', defaults={'email': 'diner@example.com', 'role': 'customer'})
    if created:
        customer.set_password('password123')
        customer.phone_number = '9876543210'
        customer.save()
        print("Created dummy customer 'hungry_diner'")
    else:
        print("Using customer 'hungry_diner'")
        
    # Create Booking in 1 hour
    booking_time = timezone.now() + timezone.timedelta(hours=1)
    
    booking = Booking.objects.create(
        customer=customer,
        restaurant=restaurant,
        table=table,
        date_time=booking_time,
        people_count=2,
        status='Confirmed'
    )
    print(f"Created Booking: {booking}")
    
    # Update Table Status
    table.status = 'Booked'
    table.save()
    print(f"Updated Table 1 status to 'Booked'")

except Exception as e:
    print(f"Error: {e}")
