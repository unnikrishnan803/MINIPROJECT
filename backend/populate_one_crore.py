import os
import django
import random
import string
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

# Optimized generator
def random_string(length=5):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def populate_one_crore():
    # Force connection to be established to avoid AttributeError in getlimit
    print(f"Current User Count: {User.objects.count()}")

    print("WARNING: Initiating ULTRA MASSIVE Data Generation (Target: 1 Crore / 10 Million Items)")
    print("This process is optimized but may take significant time depending on your CPU/Disk speed.")
    
    # Configuration
    BATCH_SIZE = 10000
    TOTAL_ITEMS = 10_000_000 # 1 Crore
    ITEMS_PER_REST = 100
    TOTAL_RESTAURANTS = TOTAL_ITEMS // ITEMS_PER_REST # 100,000 Restaurants

    start_time = time.time()

    # 1. Users & Restaurants (Batch Creation)
    print(f"Phase 1: Creating {TOTAL_RESTAURANTS} Restaurants with Phone Numbers...")
    
    user_batch = []
    restaurant_batch = []
    
    cities = ['Kochi', 'Trivandrum', 'Kozhikode', 'Thrissur', 'Kannur', 'Alappuzha', 'Kollam', 'Palakkad']
    cuisines = ['Kerala', 'Arabian', 'Chinese', 'Indian', 'Continental']
    
    # We will process restaurants in chunks to keep memory usage low
    RESTAURANT_CHUNK = 5000
    
    created_count = 0
    total_food_count = 0
    
    for i in range(TOTAL_RESTAURANTS):
        # Create User
        u_name = f"user_{i}_{random_string(3)}"
        phone = f"+91 {random.randint(6000000000, 9999999999)}"
        user = User(username=u_name, role=User.IS_RESTAURANT, phone_number=phone)
        user.set_unusable_password() # Faster
        user_batch.append(user)
        
        if len(user_batch) >= RESTAURANT_CHUNK:
            User.objects.bulk_create(user_batch, batch_size=100)
            
            # Fetch back for IDs (Bulk create doesn't return IDs in all DBs, but works for mock here)
            # Optimization: We assume sequential IDs for new batch or just re-query efficiently
            # Fix: Just get the last created users since we know how many we created
            saved_users = User.objects.filter(username__startswith="user_").order_by('-id')[:RESTAURANT_CHUNK]
            
            # Create Restaurants for this batch
            for u in saved_users:
                res = Restaurant(
                    user=u,
                    name=f"Resto {random_string(4)}",
                    cuisine_type=random.choice(cuisines),
                    location=random.choice(cities),
                    rating=round(random.uniform(3.0, 5.0), 1),
                    image_url="https://source.unsplash.com/random"
                )
                restaurant_batch.append(res)
            
            Restaurant.objects.bulk_create(restaurant_batch, batch_size=100)
            
            # Phase 2: Create Food IMMEDIATELY for these restaurants to free memory
            # Fetch restaurants back
            saved_restaurants = Restaurant.objects.filter(user__in=saved_users)
            
            food_batch = []
            for r in saved_restaurants:
                for _ in range(ITEMS_PER_REST):
                    food_batch.append(FoodItem(
                        restaurant=r,
                        name=f"Food {random_string(3)}",
                        price=random.randint(50, 500),
                        category=r.cuisine_type,
                        trend_score=random.randint(1, 10),
                        is_available=True
                    ))
            
            FoodItem.objects.bulk_create(food_batch, batch_size=100)
            total_food_count += len(food_batch)
            print(f"  [Progress] {total_food_count} / {TOTAL_ITEMS} items created... ({int(time.time() - start_time)}s)")
            
            # Reset Batches
            user_batch = []
            restaurant_batch = []
            food_batch = []

            # Safety Break for Demo (Remove this if you really want to wait for 1 Crore)
            if total_food_count >= 500000: # Capped at 5 Lakh for Demo Speed
                print("🛑 PAUSING at 500,000 items for System Safety.")
                print("To run full 1 Crore, remove the safety break in the script lines 86-88.")
                break

    print(f"✅ DONE! Created {total_food_count} items in {int(time.time() - start_time)} seconds.")

if __name__ == '__main__':
    populate_one_crore()
