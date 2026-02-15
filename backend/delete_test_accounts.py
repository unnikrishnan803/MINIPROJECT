import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

# IDs to delete
test_ids = [5, 6, 8]

print(f"Attempting to delete restaurants with IDs: {test_ids}")

deleted_count = 0
for r_id in test_ids:
    try:
        restaurant = Restaurant.objects.get(id=r_id)
        name = restaurant.name
        user_email = restaurant.user.email
        restaurant.user.delete() # Helper deletes linked restaurant due to CASCADE
        print(f"✅ Deleted Restaurant: {name} (ID: {r_id}, Email: {user_email})")
        deleted_count += 1
    except Restaurant.DoesNotExist:
        print(f"⚠️ Restaurant with ID {r_id} not found.")
    except Exception as e:
        print(f"❌ Error deleting ID {r_id}: {str(e)}")

print("-" * 30)
print(f"Total deleted: {deleted_count}")
