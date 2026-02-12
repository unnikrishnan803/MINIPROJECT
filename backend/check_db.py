import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem, Restaurant
print(f"Restaurants: {Restaurant.objects.count()}")
print(f"Food Items: {FoodItem.objects.count()}")
if FoodItem.objects.count() > 0:
    print(f"Sample: {FoodItem.objects.first().name}")
