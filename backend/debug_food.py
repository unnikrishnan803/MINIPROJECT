import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, FoodItem, Restaurant

try:
    user = User.objects.get(username='jacky')
    restaurant = user.staff_restaurant
    
    if restaurant:
        print(f"Checking menu for: {restaurant.name}")
        items = FoodItem.objects.filter(restaurant=restaurant)
        print(f"Total Items: {items.count()}")
        
        for item in items:
            print(f" - {item.name}: ${item.price} (Available: {item.is_available})")
            
        if items.count() == 0:
            print("No items found! Generating some defaults...")
            # Seed some items
            FoodItem.objects.create(restaurant=restaurant, name="Classic Burger", price=5.99, category="Main", is_available=True)
            FoodItem.objects.create(restaurant=restaurant, name="Cheese Fries", price=3.99, category="Side", is_available=True)
            FoodItem.objects.create(restaurant=restaurant, name="Coke", price=1.99, category="Drink", is_available=True)
            print("Created 3 default items.")
    else:
        print("User jacky has no restaurant.")

except User.DoesNotExist:
    print("User 'jacky' not found.")
