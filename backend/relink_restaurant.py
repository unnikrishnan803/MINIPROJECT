import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant

try:
    u = User.objects.get(username='jacky')
    r = Restaurant.objects.get(name='Liberty Burger')
    
    print(f"User: {u.username}, Role: {u.role}")
    print(f"Restaurant: {r.name}, Current Owner: {r.user.username if r.user else 'None'}")
    
    # Re-link
    print("Linking Liberty Burger to jacky...")
    r.user = u
    r.save()
    
    # Update User Role
    u.role = 'restaurant'
    u.staff_restaurant = None # Clear staff role link
    u.save()
    
    print("Done. Jacky is now the owner of Liberty Burger.")
    
except User.DoesNotExist:
    print("User jacky not found")
except Restaurant.DoesNotExist:
    print("Restaurant Liberty Burger not found")
except Exception as e:
    print(f"Error: {e}")
