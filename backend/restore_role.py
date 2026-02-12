import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User

try:
    u = User.objects.get(username='jacky')
    print(f"User: {u.username}")
    print(f"Role: {u.role}")
    print(f"Staff Restaurant: {u.staff_restaurant}")
    print(f"Restaurant Profile: {u.restaurant_profile}")
    
    # Restore to restaurant
    if u.role == 'staff':
        print("Restoring jacky to 'restaurant' role...")
        u.role = 'restaurant'
        # Ensure restaurant profile defines the link, not staff_restaurant
        if u.staff_restaurant and not u.restaurant_profile:
             u.restaurant_profile = u.staff_restaurant
             u.staff_restaurant = None
        u.save()
        print(f"New Role: {u.role}")

except User.DoesNotExist:
    print("User jacky not found")
