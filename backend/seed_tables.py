import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, Table

try:
    user = User.objects.get(username="usa_diner")
    restaurant = user.restaurant_profile
    
    print(f"Seeding tables for {restaurant.name}...")
    
    # Create 5 tables
    for i in range(1, 6):
        table, created = Table.objects.get_or_create(
            restaurant=restaurant,
            table_number=i,
            defaults={'capacity': 4, 'status': 'Available'}
        )
        if created:
            print(f"Created Table {i}")
        else:
            print(f"Table {i} already exists")
            
    print("Tables seeded successfully.")
    
except User.DoesNotExist:
    print("User 'usa_diner' not found. Please create it first.")
except Exception as e:
    print(f"Error: {e}")
