import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Order

try:
    user = User.objects.get(username='jacky')
    restaurant = user.staff_restaurant
    
    if restaurant:
        print(f"Checking Active Orders for: {restaurant.name}")
        orders = Order.objects.filter(restaurant=restaurant, status__in=['Ordered', 'Preparing'])
        print(f"Total Active Orders: {orders.count()}")
        
        for order in orders:
            print(f" - Order #{order.id} | Table {order.table.table_number if order.table else 'N/A'} | Status: {order.status} | Total: {order.total_amount}")
    else:
        print("User jacky has no restaurant.")

except User.DoesNotExist:
    print("User 'jacky' not found.")
