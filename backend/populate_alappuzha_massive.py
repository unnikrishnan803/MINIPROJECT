import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_letters, k=length))

def populate_alappuzha_massive():
    print("🛶🚀 Starting Massive Alappuzha Data Population (10,000+ Items)...")

   
    num_restaurants = 150  # 150 restaurants * 70 items = ~10,500 items
    items_per_restaurant = 70 

    
    locations = [
        'Alappuzha Beach', 'Kuttanad', 'Punnamada Lake', 'Mararikulam', 
        'Ambalapuzha', 'Haripad', 'Cherthala', 'Thanneermukkom', 
        'Mullakkal', 'Kaipuzha'
    ]
    
    prefixes = ['Royal', 'Grand', 'Alleppey', 'Lake View', 'Backwater', 'Kuttanad', 'Vembanad', 'Travancore', 'Coastal', 'Spice']
    suffixes = ['Kitchen', 'Bistro', 'Houseboat Grill', 'Toddy Shop', 'Dine', 'Palace', 'Eatery', 'Cafe', 'Resort', 'Catch']
    
    cuisines = ['Kerala Traditional', 'Seafood', 'South Indian', 'Toddy Shop Special', 'Houseboat Fusion']

    
    seafood = ['Karimeen', 'Prawns', 'Crab', 'Squid', 'Clams (Kakku)', 'King Fish', 'Seer Fish', 'Anchovy (Natholi)']
    meats = ['Duck', 'Beef', 'Chicken']
    veg = ['Kappa (Tapioca)', 'Appam', 'Porotta', 'Puttu', 'Avial', 'Thoran']
    preps = ['Roast', 'Fry', 'Curry', 'Pollichathu', 'Mappas', 'Stew', 'Varutharacha', 'Biryani']

    print(f"Creating {num_restaurants} Alappuzha Restaurants...")
    
    # 1. Create Users
    users = []
    for i in range(num_restaurants):
        username = f"alp_res_{i}_{generate_random_string()}"
        users.append(User(username=username, role=User.IS_RESTAURANT))
    
    User.objects.bulk_create(users, ignore_conflicts=True)
    created_users = User.objects.filter(username__startswith='alp_res_').order_by('-id')[:num_restaurants]

    # 2. Create Restaurants
    restaurants = []
    base_img = "https://source.unsplash.com/random/500x500/?kerala,food"
    
    for i, user in enumerate(created_users):
        name = f"{random.choice(prefixes)} {random.choice(suffixes)} {generate_random_string(2).upper()}"
        restaurants.append(Restaurant(
            user=user,
            name=name,
            cuisine_type=random.choice(cuisines),
            location=random.choice(locations),
            rating=round(random.uniform(3.5, 5.0), 1),
            image_url=base_img
        ))
    
    Restaurant.objects.bulk_create(restaurants)
    # Fetch back specific created restaurants
    target_restaurants = Restaurant.objects.filter(user__username__startswith='alp_res_').order_by('-id')[:num_restaurants]

    # 3. Create Food Items
    print("Generating Authentic Food Items...")
    food_items = []
    count = 0
    
    for res in target_restaurants:
        for _ in range(items_per_restaurant):
            # Generate Authentic Name
            category = res.cuisine_type
            
            if category == 'Seafood' or category == 'Toddy Shop Special':
                main_ing = random.choice(seafood)
            elif category == 'Kerala Traditional':
                main_ing = random.choice(meats + veg)
            else:
                main_ing = random.choice(seafood + meats + veg)
                
            prep = random.choice(preps)
            name = f"Alappuzha Style {main_ing} {prep}"
            
            # Add some variety
            if random.random() > 0.7:
                name = f"{res.location} Special {main_ing}"

            food_items.append(FoodItem(
                restaurant=res,
                name=name,
                description=f"Freshly prepared {main_ing} with authentic Kuttanad spices.",
                price=round(random.uniform(3.0, 25.0), 2),
                category=category,
                trend_score=round(random.uniform(5.0, 10.0), 1), # High trends for local food
                is_available=random.choices([True, False], weights=[80, 20])[0],
                image_url=f"https://source.unsplash.com/random/500x500/?{main_ing.split(' ')[0]}"
            ))
            count += 1
            
            if len(food_items) >= 5000:
                FoodItem.objects.bulk_create(food_items)
                print(f"  Inserted {count} items...")
                food_items = []

    if food_items:
        FoodItem.objects.bulk_create(food_items)

    print(f"✅ MISSION ACCOMPLISHED! Added {count} authentic items across {num_restaurants} Alappuzha restaurants.")

if __name__ == '__main__':
    populate_alappuzha_massive()
