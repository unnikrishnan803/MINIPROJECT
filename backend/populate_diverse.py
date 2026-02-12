import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

def populate_diverse():
    print("🌍 Adding Diverse Global & Local Dining Spots (with Phone Numbers)...")

    diverse_data = [
        # Famous Chains (Mock)
        {
            'user': 'burger_king_mock', 'name': 'Burger King (Mock)', 'cuisine': 'Fast Food', 'loc': 'City Center',
            'phone': '+91 9876543210',
            'img': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add',
            'menu': [
                {'name': 'Whopper', 'price': 6.50, 'cat': 'Burgers'},
                {'name': 'Chicken Fries', 'price': 4.50, 'cat': 'Sides'},
                {'name': 'Chocolate Shake', 'price': 3.50, 'cat': 'Dessert'},
            ]
        },
        {
            'user': 'starbucks_mock', 'name': 'Starbucks (Mock)', 'cuisine': 'Cafe', 'loc': 'Mall Road',
            'phone': '+91 9876543211',
            'img': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93',
            'menu': [
                {'name': 'Caramel Macchiato', 'price': 5.50, 'cat': 'Coffee'},
                {'name': 'Java Chip Frappuccino', 'price': 6.00, 'cat': 'Coffee'},
                {'name': 'Blueberry Muffin', 'price': 3.00, 'cat': 'Bakery'},
            ]
        },
        # Fine Dining
        {
            'user': 'golden_dragon', 'name': 'The Golden Dragon', 'cuisine': 'Chinese', 'loc': 'Luxury Heights',
            'phone': '+91 9876543212',
            'img': 'https://images.unsplash.com/photo-1552566626-52f8b828add9',
            'menu': [
                {'name': 'Peking Duck', 'price': 45.00, 'cat': 'Main Course'},
                {'name': 'Dim Sum Platter', 'price': 22.00, 'cat': 'Starters'},
                {'name': 'Kung Pao Chicken', 'price': 18.00, 'cat': 'Main Course'},
            ]
        },
        # Street Food
        {
            'user': 'mumbai_chaat', 'name': 'Mumbai Chaat House', 'cuisine': 'Indian Street Food', 'loc': 'Market Square',
            'phone': '+91 9876543213',
            'img': 'https://images.unsplash.com/photo-1589302168068-964664d93dc0',
            'menu': [
                {'name': 'Pani Puri', 'price': 2.00, 'cat': 'Chaat'},
                {'name': 'Vada Pav', 'price': 1.50, 'cat': 'Snacks'},
                {'name': 'Pav Bhaji', 'price': 4.00, 'cat': 'Main Course'},
            ]
        }
    ]

    for r_data in diverse_data:
        # Create User with Phone
        res_user, created = User.objects.get_or_create(username=r_data['user'], role=User.IS_RESTAURANT)
        if created:
            res_user.set_password('res123')
            res_user.phone_number = r_data['phone'] # Adding Phone!
            res_user.save()

        # Create Restaurant
        restaurant, created = Restaurant.objects.get_or_create(
            user=res_user,
            defaults={
                'name': r_data['name'],
                'cuisine_type': r_data['cuisine'],
                'location': r_data['loc'],
                'rating': round(random.uniform(4.0, 5.0), 1),
                'image_url': r_data['img']
            }
        )
        print(f"📞 Added: {restaurant.name} (Ph: {res_user.phone_number})")

        # Create Menu Items
        for item in r_data['menu']:
            FoodItem.objects.get_or_create(
                restaurant=restaurant,
                name=item['name'],
                defaults={
                    'price': item['price'],
                    'category': item['cat'],
                    'description': f"Tasty {item['name']}",
                    'trend_score': round(random.uniform(5.0, 9.5), 1),
                    'is_available': True,
                    'image_url': f"https://source.unsplash.com/random/500x500/?{item['name'].replace(' ', ',')}"
                }
            )

    print("✅ Diverse data with Phone Numbers added!")

if __name__ == '__main__':
    populate_diverse()
