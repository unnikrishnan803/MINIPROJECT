import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant

try:
    user = User.objects.get(username='jacky')
    # Find Liberty Burger (owned by usa_diner)
    # OR just pick the first restaurant if usa_diner doesn't exist
    
    restaurant = Restaurant.objects.filter(user__username='usa_diner').first()
    if not restaurant:
        restaurant = Restaurant.objects.first()
        
    if restaurant:
        print(f"Assigning 'jacky' to restaurant: {restaurant.name}")
        user.role = 'staff'
        user.staff_restaurant = restaurant
        user.save()
        print("Successfully updated jacky to Staff role linked to restaurant.")
    else:
        print("No restaurant found to assign.")

except User.DoesNotExist:
    print("User 'jacky' not found.")
except Exception as e:
    print(f"Error: {e}")
