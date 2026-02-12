import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_letters, k=length))

def populate_kerala_full():
    print("🌴🚀 Initiating KERALA MEGA POPULATION (All 14 Districts)...")

    districts = [
        'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 
        'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 
        'Kozhikode', 'Wayanad', 'Kannur', 'Kasargod'
    ]

    # Specific flavors/locations for variety
    district_data = {
        'Thiruvananthapuram': {'locs': ['Kovalam', 'Technopark', 'Kazhakkoottam'], 'food': ['Boli', 'Chicken Fry']},
        'Kozhikode': {'locs': ['Mananchira', 'Kozhikode Beach'], 'food': ['Kozhikode Halwa', 'Biryani']},
        'Malappuram': {'locs': ['Manjeri', 'Perinthalmanna'], 'food': ['Mandi', 'Pathiri']},
        'Ernakulam': {'locs': ['Fort Kochi', 'Edappally', 'Marine Drive'], 'food': ['Seafood Platter', 'Beef Roast']},
        'Wayanad': {'locs': ['Kalpetta', 'Sulthan Bathery'], 'food': ['Bamboo Rice', 'Honey Gooseberry']},
        'Kannur': {'locs': ['Payyambalam', 'Thalassery'], 'food': ['Thalassery Biryani', 'Unnakkaya']},
        'Kottayam': {'locs': ['Kumarakom', 'Pala'], 'food': ['Kottayam Fish Curry', 'Duck Roast']},
        # Defaults for others
        'default': {'locs': ['City Center', 'Market Road', 'High Range'], 'food': ['Meals', 'Porotta']}
    }

    restaurants_per_district = 100 # Total 1400 restaurants
    items_per_restaurant = 50     # Total ~70,000 items (Safe limit for Dev)

    print(f"Target: {len(districts) * restaurants_per_district} Restaurants & ~{len(districts) * restaurants_per_district * items_per_restaurant} Food Items")

    all_users = []
    
    # 1. Create Users (Bulk)
    print("  > Generating User Accounts...")
    for district in districts:
        for i in range(restaurants_per_district):
            username = f"{district[:3].lower()}_{i}_{generate_random_string()}"
            all_users.append(User(username=username, role=User.IS_RESTAURANT))
            
    User.objects.bulk_create(all_users, ignore_conflicts=True)
    
    # Fetch them back to assign IDs
    created_users = list(User.objects.filter(role=User.IS_RESTAURANT).order_by('-id')[:len(all_users)])
    
    # 2. Create Restaurants
    print("  > Building Restaurants across Kerala...")
    restaurants = []
    
    # Distribute users among districts
    user_idx = 0
    
    for district in districts:
        info = district_data.get(district, district_data['default'])
        
        for _ in range(restaurants_per_district):
            if user_idx >= len(created_users): break
            
            user = created_users[user_idx]
            user_idx += 1
            
            loc = random.choice(info['locs'])
            name = f"{district} {random.choice(['Spices', 'Palace', 'Dine', 'Cafe', 'Restaurant', 'Bistro'])} {generate_random_string(3).upper()}"
            
            restaurants.append(Restaurant(
                user=user,
                name=name,
                cuisine_type='Kerala Traditional',
                location=f"{loc}, {district}",
                rating=round(random.uniform(3.8, 5.0), 1),
                image_url=f"https://source.unsplash.com/random/500x500/?{district},food"
            ))

    Restaurant.objects.bulk_create(restaurants)
    created_restaurants = Restaurant.objects.order_by('-id')[:len(restaurants)]

    # 3. Create Food Items
    print("  > Cooking up the Mega Menu (This is the big one)...")
    
    food_items = []
    global_count = 0
    
    common_foods = ['Porotta', 'Appam', 'Idiyappam', 'Rice', 'Sambar', 'Avial', 'Fish Fry', 'Beef Roast', 'Chicken Curry']
    
    for res in created_restaurants:
        # Determine district from location string
        district_name = res.location.split(', ')[-1]
        specialties = district_data.get(district_name, district_data['default'])['food']
        
        for _ in range(items_per_restaurant):
            if random.random() > 0.7:
                item_name = f"Special {random.choice(specialties)}"
            else:
                item_name = f"{random.choice(common_foods)} {generate_random_string(2)}"
                
            food_items.append(FoodItem(
                restaurant=res,
                name=item_name,
                description=f"Authentic {district_name} style preparation.",
                price=round(random.uniform(50.0, 500.0), 2),
                category='Kerala Special',
                trend_score=round(random.uniform(6.0, 10.0), 1),
                is_available=True,
                image_url=f"https://source.unsplash.com/random/500x500/?food,{district_name}"
            ))
            global_count += 1
            
            if len(food_items) >= 10000:
                FoodItem.objects.bulk_create(food_items)
                print(f"    Served {global_count} items...")
                food_items = []

    if food_items:
        FoodItem.objects.bulk_create(food_items)
        
    print(f"✅ COMPLETED: {global_count} items generated across all 14 Districts!")

if __name__ == '__main__':
    populate_kerala_full()
