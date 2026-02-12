import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem, Restaurant

def reset_db():
    print("⚠️ Deleting all existing data...")
    FoodItem.objects.all().delete()
    Restaurant.objects.all().delete()
    print("✅ Database cleared.")

    print("🌱 Seeding minimal 'Trending' data...")
    
    # Create 3 Sample Users for Restaurants
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Clean up test users first
    User.objects.filter(username__startswith="test_owner_").delete()

    u1 = User.objects.create_user(username="test_owner_1", email="owner1@test.com", password="password123", role=User.IS_RESTAURANT)
    u2 = User.objects.create_user(username="test_owner_2", email="owner2@test.com", password="password123", role=User.IS_RESTAURANT)
    u3 = User.objects.create_user(username="test_owner_3", email="owner3@test.com", password="password123", role=User.IS_RESTAURANT)

    # Create 3 Sample Restaurants
    r1 = Restaurant.objects.create(user=u1, name="The Burger Joint", cuisine_type="American", location="Downtown", rating=4.8, image_url="https://images.unsplash.com/photo-1571091718767-18b5b1457add?auto=format&fit=crop&w=500&q=60")
    r2 = Restaurant.objects.create(user=u2, name="Pizza Paradise", cuisine_type="Italian", location="Uptown", rating=4.7, image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=500&q=60")
    r3 = Restaurant.objects.create(user=u3, name="Kerala Kitchen", cuisine_type="Indian", location="Alappuzha", rating=4.9, image_url="https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=500&q=60")

    # Create 6 Trending Items
    items = [
        (r1, "Spicy Beef Burger", "Juicy beef patty with jalapenos", 12.99, "American"),
        (r1, "Cheesy Fries", "Crispy fries topped with melted cheese", 5.99, "Fast Food"),
        (r2, "Classic Pepperoni", "Traditional pepperoni pizza", 15.50, "Italian"),
        (r2, "Garlic Breadsticks", "Soft breadsticks with marinara", 6.50, "Italian"),
        (r3, "Karimeen Pollichathu", "Pearl spot fish marinated and grilled in banana leaf", 18.00, "Seafood"),
        (r3, "Chicken Biryani", "Aromatic rice with spiced chicken", 14.00, "Indian"),
    ]

    for rest, name, desc, price, cat in items:
        FoodItem.objects.create(
            restaurant=rest,
            name=name,
            description=desc,
            price=price,
            category=cat,
            trend_score=random.uniform(8.0, 10.0), # High score for trending
            is_available=True,
            image_url="" # Let frontend smart matcher handle it or use placeholders
        )

    print(f"✅ Created {Restaurant.objects.count()} restaurants and {FoodItem.objects.count()} trending items.")

if __name__ == '__main__':
    reset_db()
