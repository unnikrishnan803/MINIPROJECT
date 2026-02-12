import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Table, Restaurant

try:
    user = User.objects.get(username='jacky')
    print(f"User: {user.username}")
    print(f"Role: {user.role}")
    print(f"Staff Restaurant: {user.staff_restaurant}")
    
    if user.staff_restaurant:
        tables = Table.objects.filter(restaurant=user.staff_restaurant)
        print(f"Tables for {user.staff_restaurant.name}: {tables.count()}")
        for t in tables:
            print(f" - Table {t.table_number}: {t.status}")
    else:
        print("User has no staff_restaurant assigned.")
        
    # Also list all restaurants and tables to see what exists
    print("\n--- All Restaurants ---")
    vals = Restaurant.objects.all()
    for r in vals:
        print(f"Restaurant: {r.name} (User: {r.user.username})")
        print(f"  Tables: {Table.objects.filter(restaurant=r).count()}")

except User.DoesNotExist:
    print("User 'jacky' not found.")
