import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

def populate_alappuzha():
    print("🛶 Adding Authentic Alappuzha (Alleppey) Flavors...")

    alappuzha_data = [
        {
            'user': 'kuttanad_taste', 'name': 'Kuttanad Taste', 'cuisine': 'Kerala Traditional', 'loc': 'Alappuzha',
            'img': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec',
            'desc': 'Authentic food from the heart of the backwaters.',
            'menu': [
                {'name': 'Kuttanad Duck Roast', 'price': 14.50, 'cat': 'non-veg', 'desc': 'Spicy duck slow-cooked in thick gravy, a Kuttanad special.', 'trend': 9.8},
                {'name': 'Karimeen Pollichathu', 'price': 16.00, 'cat': 'Seafood', 'desc': 'Pearl Spot fish marinated in spices and grilled in banana leaf.', 'trend': 9.9},
                {'name': 'Kappa & Meen Curry', 'price': 8.00, 'cat': 'Combo', 'desc': 'Steamed Tapioca served with spicy red fish curry.', 'trend': 9.5},
            ]
        },
        {
            'user': 'vembanad_seafood', 'name': 'Vembanad Catch', 'cuisine': 'Seafood', 'loc': 'Alappuzha Beach',
            'img': 'https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6',
            'desc': 'Fresh catch from the lake, served on your plate.',
            'menu': [
                {'name': 'Alleppey Fish Curry', 'price': 11.00, 'cat': 'Seafood', 'desc': 'Fish cooked in raw mango and coconut milk broth.', 'trend': 9.2},
                {'name': 'Prawns Roast', 'price': 15.00, 'cat': 'Seafood', 'desc': 'Tiger prawns roasted with pepper and curry leaves.', 'trend': 9.4},
                {'name': 'Squid Fry', 'price': 9.00, 'cat': 'Starters', 'desc': 'Crispy fried squid rings with spicy dip.', 'trend': 8.5},
            ]
        },
        {
            'user': 'royal_houseboat', 'name': 'Royal Houseboat Grill', 'cuisine': 'Fusion', 'loc': 'Punnamada Lake',
            'img': 'https://images.unsplash.com/photo-1544148103-0773bf10d330',
            'desc': 'Dine on the water with a mix of Kerala and Continental.',
            'menu': [
                {'name': 'Grilled Seer Fish', 'price': 13.50, 'cat': 'Seafood', 'desc': 'Seer fish fillet grilled with lemon butter sauce.', 'trend': 8.9},
                {'name': 'Coconut Souffle', 'price': 6.00, 'cat': 'Dessert', 'desc': 'Tender coconut pudding, a sweet ending.', 'trend': 8.0},
            ]
        }
    ]

    for r_data in alappuzha_data:
        # Create User
        res_user, created = User.objects.get_or_create(username=r_data['user'], role=User.IS_RESTAURANT)
        if created:
            res_user.set_password('res123')
            res_user.save()

        # Create Restaurant
        restaurant, created = Restaurant.objects.get_or_create(
            user=res_user,
            defaults={
                'name': r_data['name'],
                'cuisine_type': r_data['cuisine'],
                'location': r_data['loc'],
                'rating': round(random.uniform(4.5, 5.0), 1),
                'image_url': r_data['img']
            }
        )
        print(f"📍 Added Restaurant: {restaurant.name} ({restaurant.location})")

        # Create Menu Items
        for item in r_data['menu']:
            FoodItem.objects.get_or_create(
                restaurant=restaurant,
                name=item['name'],
                defaults={
                    'price': item['price'],
                    'category': item['cat'],
                    'description': item['desc'],
                    'trend_score': item['trend'], 
                    'is_available': True,
                    'image_url': f"https://source.unsplash.com/random/500x500/?{item['name'].replace(' ', ',')}"
                }
            )

    print("✅ Alappuzha specific data added successfully!")

if __name__ == '__main__':
    populate_alappuzha()
