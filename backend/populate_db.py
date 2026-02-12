import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant, FoodItem

def populate():
    print("Populating database with extensive data...")

    # Ensure Admin exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created.")

    # Data Source
    restaurants_data = [
        {
            'user': 'pizza_paradise', 'name': 'Pizza Paradise', 'cuisine': 'Italian', 'loc': 'Uptown', 
            'img': 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
            'menu': [
                {'name': 'Classic Pepperoni', 'price': 15.50, 'cat': 'Italian', 'trend': 9.8},
                {'name': 'Margherita Pizza', 'price': 12.00, 'cat': 'Italian', 'trend': 8.5},
                {'name': 'BBQ Chicken Pizza', 'price': 16.50, 'cat': 'Italian', 'trend': 6.0},
                {'name': 'Garlic Breadsticks', 'price': 6.50, 'cat': 'Sides', 'trend': 7.5},
            ]
        },
        {
            'user': 'burger_joint', 'name': 'The Burger Joint', 'cuisine': 'American', 'loc': 'Downtown',
            'img': 'https://images.unsplash.com/photo-1571091718767-18b5b1457add',
            'menu': [
                {'name': 'Spicy Beef Burger', 'price': 12.99, 'cat': 'American', 'trend': 9.5},
                {'name': 'Cheeseburger', 'price': 10.00, 'cat': 'American', 'trend': 7.0},
                {'name': 'Crispy Chicken Burger', 'price': 11.50, 'cat': 'American', 'trend': 8.8},
                {'name': 'Onion Rings', 'price': 5.00, 'cat': 'Sides', 'trend': 5.5},
            ]
        },
        {
            'user': 'sushi_zen', 'name': 'Sushi Zen', 'cuisine': 'Japanese', 'loc': 'Midtown',
            'img': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c',
            'menu': [
                {'name': 'Dragon Roll', 'price': 14.00, 'cat': 'Japanese', 'trend': 9.2},
                {'name': 'Salmon Nigiri', 'price': 8.00, 'cat': 'Japanese', 'trend': 7.8},
                {'name': 'Miso Soup', 'price': 4.00, 'cat': 'Japanese', 'trend': 6.5},
                {'name': 'Tempura Platter', 'price': 12.50, 'cat': 'Japanese', 'trend': 8.0},
            ]
        },
        {
            'user': 'kerala_kitchen', 'name': 'Kerala Kitchen', 'cuisine': 'South Indian', 'loc': 'Riverside',
            'img': 'https://images.unsplash.com/photo-1610192244261-3f33de3f55e0',
            'menu': [
                {'name': 'Kerala Porotta', 'price': 2.50, 'cat': 'South Indian', 'trend': 9.9},
                {'name': 'Beef Fry', 'price': 12.00, 'cat': 'South Indian', 'trend': 9.7},
                {'name': 'Appam with Stew', 'price': 8.00, 'cat': 'South Indian', 'trend': 8.8},
                {'name': 'Karimeen Pollichathu', 'price': 18.00, 'cat': 'Seafood', 'trend': 9.2},
                {'name': 'Puttu and Kadala', 'price': 6.00, 'cat': 'Breakfast', 'trend': 7.5},
            ]
        },
        {
            'user': 'spice_world', 'name': 'Spice World', 'cuisine': 'Indian', 'loc': 'Westside',
            'img': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641',
            'menu': [
                {'name': 'Chicken Tikka Masala', 'price': 14.00, 'cat': 'Indian', 'trend': 9.0},
                {'name': 'Butter Naan', 'price': 3.00, 'cat': 'Indian', 'trend': 8.5},
                {'name': 'Paneer Butter Masala', 'price': 13.00, 'cat': 'Indian', 'trend': 7.9},
                {'name': 'Mango Lassi', 'price': 5.00, 'cat': 'Drinks', 'trend': 9.1},
            ]
        }
    ]

    for r_data in restaurants_data:
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
                'rating': round(random.uniform(4.0, 5.0), 1),
                'image_url': r_data['img']
            }
        )
        print(f"Processing Restaurant: {restaurant.name}")

        # Create Menu Items
        for item in r_data['menu']:
            FoodItem.objects.get_or_create(
                restaurant=restaurant,
                name=item['name'],
                defaults={
                    'price': item['price'],
                    'category': item['cat'],
                    'trend_score': item['trend'], # Simulating AI Score
                    'is_available': True,
                    'image_url': f"https://source.unsplash.com/500x500/?{item['name'].replace(' ', ',')}"
                }
            )

    print("Database populated successfully with diverse data!")

if __name__ == '__main__':
    populate()
