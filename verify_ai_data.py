import os
import sys
import django
from django.utils import timezone

# Add backend to path to find settings
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem

def verify_data():
    print("🔍 Verifying AI Data...")
    items = FoodItem.objects.all()
    if not items.exists():
        print("❌ No items found!")
        return

    scored_items = items.filter(trend_score__isnull=False, popularity_score__isnull=False)
    print(f"✅ Found {scored_items.count()} items with scores.")
    
    # Check for sellout predictions
    predicted_items = items.filter(estimated_sellout_time__isnull=False)
    print(f"✅ Found {predicted_items.count()} items with sellout predictions.")

    # Check logic
    check_item = items.first()
    print(f"Example Item: {check_item.name}")
    print(f"  Trend Score: {check_item.trend_score}")
    print(f"  Popularity: {check_item.popularity_score}")
    print(f"  Quantity: {check_item.quantity_available}")
    print(f"  Sellout Time: {check_item.estimated_sellout_time}")

if __name__ == "__main__":
    verify_data()
