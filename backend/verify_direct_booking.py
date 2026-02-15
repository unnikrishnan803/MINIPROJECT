
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, Table, Booking

def verify_booking():
    print("Starting booking verification...")
    
    # Get a user (customer)
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("No customer found. Creating one...")
        customer = User.objects.create_user(username='test_customer', email='test@example.com', password='password123', role='customer')
    
    print(f"Customer: {customer.username} (ID: {customer.id})")

    # Get a restaurant
    restaurant = Restaurant.objects.first()
    if not restaurant:
        print("No restaurant found.")
        return

    print(f"Restaurant: {restaurant.name} (ID: {restaurant.id})")

    # Get a table
    table = Table.objects.filter(restaurant=restaurant).first()
    if not table:
        print("No table found for this restaurant. Creating one...")
        table = Table.objects.create(restaurant=restaurant, table_number="T-99", capacity=4)
        
    print(f"Table: {table.table_number} (ID: {table.id})")
    
    # Create Booking
    booking_time = datetime.now() + timedelta(days=1)
    
    try:
        booking = Booking.objects.create(
            customer=customer,
            restaurant=restaurant,
            table=table,
            date_time=booking_time,
            people_count=2,
            status='Confirmed'
        )
        print(f"Booking created successfully! ID: {booking.id}")
        print(f"Status: {booking.status}")
        print(f"Time: {booking.date_time}")
        
        # Verify it exists
        b = Booking.objects.get(id=booking.id)
        assert b.customer == customer
        assert b.table == table
        print("Verification PASSED: Booking retrieved from DB.")
        
        # Cleanup
        booking.delete()
        print("Test booking deleted.")
        
    except Exception as e:
        print(f"Verification FAILED: {str(e)}")

if __name__ == '__main__':
    verify_booking()
