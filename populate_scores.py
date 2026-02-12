import os
import sys
import django
import random
from django.utils import timezone
from datetime import timedelta

# Add backend to path to find settings
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem

print("🚀 Updating AI scores...")
items = FoodItem.objects.all()
count = 0
for item in items:
    # Trend score: 0-100
    item.trend_score = round(random.uniform(0, 100), 1)
    
    # Popularity score: 0-100
    item.popularity_score = round(random.uniform(0, 100), 1)
    
    # Random quantity for sell-out simulation
    # Ensure some are low stock (<20)
    if random.random() < 0.2: # 20% chance of low stock
        item.quantity_available = random.randint(1, 15)
        item.estimated_sellout_time = timezone.now() + timedelta(hours=random.randint(1, 4))
    else:
        item.quantity_available = random.randint(25, 100)
        item.estimated_sellout_time = None
        
    item.save()
    count += 1

print(f"✅ Updated {count} items with AI scores.")
