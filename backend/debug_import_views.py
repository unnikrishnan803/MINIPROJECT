import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

print("Attempting to import core.views...")
try:
    import core.views
    print("Imported core.views successfully.")
    if hasattr(core.views, 'FoodItemViewSet'):
        print("FoodItemViewSet is present.")
    else:
        print("FoodItemViewSet is MISSING from core.views dir:", dir(core.views))
except ImportError as e:
    print(f"ImportError during import core.views: {e}")
except Exception as e:
    print(f"Other Error: {e}")
