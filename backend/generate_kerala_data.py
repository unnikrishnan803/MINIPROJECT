import os
import django
import random
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem, Restaurant
from django.contrib.auth import get_user_model

def generate_data():
    User = get_user_model()
    BATCH_SIZE = 50 # Small batch size to avoid SQLite variables limit

    print("🧹 CLEANUP: Deleting existing data...", flush=True)
    # Delete in correct order to respect Foreign Keys
    FoodItem.objects.all().delete()
    Restaurant.objects.all().delete()
    User.objects.filter(username__startswith="kerala_rest_").delete()
    User.objects.filter(username__startswith="kerala_owner_").delete()
    print("✅ Cleanup complete.", flush=True)

    # Define Kerala Geography
    kerala_map = {
        "Alappuzha": ["Cherthala", "Kuttanadu", "Ambalapuzha", "Haripad", "Mavelikkara", "Chengannur", "Alappuzha Town"],
        "Ernakulam": ["Kochi", "Edapally", "Aluva", "Kalamassery", "Vytilla", "Marine Drive", "Kakkanad", "Fort Kochi"],
        "Thiruvananthapuram": ["Thampanoor", "Kazhakoottam", "Kovalam", "Varkala", "Neyyattinkara", "Pattom"],
        "Kozhikode": ["Mananchira", "Beach Road", "Mavoor", "Feroke", "Vadakara", "Thamarassery"],
        "Malappuram": ["Manjeri", "Tirur", "Perinthalmanna", "Ponnani", "Malappuram Town"],
        "Thrissur": ["Thrissur Round", "Guruvayoor", "Chalakudy", "Kodungallur", "Irinjalakuda"],
        "Kollam": ["Kollam Beach", "Karunagappally", "Punalur", "Kottarakkara"],
        "Kottayam": ["Kottayam Town", "Changanassery", "Pala", "Kanjirappally", "Kumarakom"],
        "Palakkad": ["Palakkad Fort", "Ottapalam", "Mannarkkad", "Pattambi"],
        "Kannur": ["Kannur Town", "Thalassery", "Payyannur", "Taliparamba"],
        "Wayanad": ["Kalpetta", "Sulthan Bathery", "Mananthavady"],
        "Idukki": ["Thodupuzha", "Munnar", "Adimali", "Kattappana"],
        "Pathanamthitta": ["Thiruvalla", "Adoor", "Pathanamthitta Town"],
        "Kasargod": ["Kasargod Town", "Kanhangad", "Udma"]
    }

    # Food Categories
    menu_items = {
        "Kerala": ["Kerala Sadya", "Appam with Stew", "Puttu and Kadala", "Idiyappam with Egg Curry", "Avial", "Thalassery Biryani", "Malabar Parotta", "Beef Roast", "Karimeen Pollichathu", "Fish Molee", "Kappa and Meen Curry", "Pazhampori", "Unniyappam"],
        "Arabian": ["Chicken Mandi", "Al Faham", "Shawarma Plate", "Kuzhimanthi", "Grilled Chicken", "Hummus with Pita"],
        "Chinese": ["Fried Rice", "Chilly Chicken", "Gobi Manchurian", "Chicken Noodles", "Momos"],
        "Desserts": ["Falooda", "Tender Coconut Pudding", "Payasam", "Fruit Salad", "Ice Cream Scoop"],
        "Juices": ["Kulukki Sarbath", "Lime Juice", "Avil Milk", "Shamodu", "Sharjah Shake"]
    }
    restaurant_suffixes = ["Bistro", "Cafe", "Hotel", "Restaurant", "Dhaba", "Kitchen", "Food Court", "Bakery", "Plaza"]

    # 1. Prepare Data in Memory
    print("🏗️  Preparing Restaurant Data...", flush=True)
    temp_data = [] # Stores (name, cuisine, location, rating, img, district)
    
    for district, towns in kerala_map.items():
        # High volume for target districts
        count = 300 if district in ["Ernakulam", "Thiruvananthapuram", "Kozhikode", "Alappuzha"] else 150
        
        for _ in range(count):
            town = random.choice(towns)
            cuisine = random.choice(list(menu_items.keys()))
            name = f"{town} {random.choice(restaurant_suffixes)} {random.randint(1, 999)}"
            img = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=500&q=60" 
            temp_data.append({
                'name': name, 
                'cuisine': cuisine, 
                'town': town, 
                'rating': random.uniform(3.5, 5.0), 
                'img': img,
                'district': district
            })
    
    total_count = len(temp_data)
    print(f"📋 Planned {total_count} restaurants.", flush=True)

    # 2. Create Users (1 per Restaurant)
    print("👤 Creating Owners...", flush=True)
    users_batch = []
    base_id = User.objects.count() # Avoid ID collision assumption, use username uniqueness
    
    for i in range(total_count):
        u = User(username=f"kerala_rest_{base_id + i}", email=f"rest{base_id + i}@test.com", role=User.IS_RESTAURANT)
        u.set_unusable_password() 
        users_batch.append(u)
        
        if len(users_batch) >= BATCH_SIZE:
            User.objects.bulk_create(users_batch)
            users_batch = []
            
    if users_batch:
        User.objects.bulk_create(users_batch)
    
    # 3. Fetch Users
    print("🔙 Fetching Created Users...", flush=True)
    # We fetch ALL the users we just created. 
    # Logic: Filter by the prefix 'kerala_rest_' and take the last N items (since we deleted old ones, these should be the only ones, but safer to take last N)
    created_users = list(User.objects.filter(username__startswith="kerala_rest_").order_by('id'))
    if len(created_users) < total_count:
        print(f"❌ ERROR: Expected {total_count} users, found {len(created_users)}")
        return

    # 4. Create Restaurants
    print("🏪 Creating Restaurants...", flush=True)
    restaurants_batch = []
    
    for i in range(total_count):
        data = temp_data[i]
        owner = created_users[i]
        
        r = Restaurant(
            user=owner,
            name=data['name'],
            cuisine_type=data['cuisine'],
            location=data['town'],
            rating=data['rating'],
            image_url=data['img']
        )
        # Store district temporarily on object for food generation usage
        r._temp_district = data['district'] 
        restaurants_batch.append(r)
        
        if len(restaurants_batch) >= BATCH_SIZE:
            Restaurant.objects.bulk_create(restaurants_batch)
            restaurants_batch = []
            
    if restaurants_batch:
        Restaurant.objects.bulk_create(restaurants_batch)
        
    # 5. Create Food Items
    print("🍔 Creating Food Items...", flush=True)
    
    # We need to fetch restaurants again to get their IDs. 
    # However, we lost the `_temp_district` attribute upon fetching.
    # So we'll need to re-derive district or use a clever mapping.
    # Re-deriving is safer.
    
    saved_restaurants = Restaurant.objects.all()
    food_batch = []
    total_food = 0
    
    # helper for district lookup
    def get_district(town_name):
        for d, t in kerala_map.items():
            if town_name in t: return d
        return "Unknown"

    for r in saved_restaurants:
        district = get_district(r.location)
        num_items = random.randint(25, 35) # Target ~30 items per rest -> ~100k total
        
        menu = menu_items.get(r.cuisine_type, []) + menu_items["Juices"] + menu_items["Desserts"]
        
        for _ in range(num_items):
            fname = random.choice(menu)
            
            # Trend Score boost for target locations
            trend = random.uniform(0, 5)
            if district in ["Alappuzha", "Ernakulam"]:
                trend += random.uniform(2, 5)
                
            f = FoodItem(
                restaurant=r,
                name=fname,
                description=f"Tasty {fname}",
                price=random.randint(60, 450),
                category=r.cuisine_type,
                trend_score=trend,
                is_available=True,
                image_url=""
            )
            food_batch.append(f)
            
            if len(food_batch) >= BATCH_SIZE:
                FoodItem.objects.bulk_create(food_batch)
                total_food += len(food_batch)
                food_batch = []
                if total_food % 5000 == 0:
                    print(f"... {total_food} items", flush=True)

    if food_batch:
        FoodItem.objects.bulk_create(food_batch)
        total_food += len(food_batch)
        
    print(f"🎉 DONE: {total_food} Food Items Generated.", flush=True)

if __name__ == '__main__':
    generate_data()
