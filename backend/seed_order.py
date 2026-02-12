import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Order, Table, FoodItem, Restaurant

try:
    # Get Restaurant
    restaurant = Restaurant.objects.get(name='Liberty Burger')
    print(f"Restaurant: {restaurant.name}")
    
    # Get Table 1
    table = Table.objects.get(restaurant=restaurant, table_number=1)
    
    # Create Order
    order = Order.objects.create(
        restaurant=restaurant,
        table=table,
        status='Ordered',
        total_amount=15.99
    )
    
    # Add items
    items = FoodItem.objects.filter(restaurant=restaurant)[:2]
    if items.exists():
        order.items.set(items)
        order.save()
        print(f"Created Order #{order.id} for Table 1 with {items.count()} items.")
    else:
        print("No food items found to add to order.")

except Exception as e:
    print(f"Error: {e}")
