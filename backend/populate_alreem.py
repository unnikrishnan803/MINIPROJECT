import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant, FoodItem

def populate_alreem():
    try:
        r = Restaurant.objects.get(id=10)
        print(f"Populating menu for: {r.name}")
        
        # Clear existing? Use user request "add". I'll keep existing if any (none found).
        
        items = [
            # Al Faham Mandi
            {"name": "Al Faham Mandi (Quarter)", "price": 240, "cat": "Mandi", "img": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500"},
            {"name": "Al Faham Mandi (Half)", "price": 450, "cat": "Mandi", "img": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500"},
            {"name": "Al Faham Mandi (Full)", "price": 850, "cat": "Mandi", "img": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500"},
            
            # Al Faham Chicken
            {"name": "Al Faham Chicken (Quarter)", "price": 160, "cat": "Grills", "img": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=500"},
            {"name": "Al Faham Chicken (Half)", "price": 310, "cat": "Grills", "img": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=500"},
            {"name": "Al Faham Chicken (Full)", "price": 600, "cat": "Grills", "img": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=500"},

            # Peri Peri Al Faham
            {"name": "Peri Peri Al Faham (Quarter)", "price": 180, "cat": "Grills", "img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500"},
            {"name": "Peri Peri Al Faham (Half)", "price": 350, "cat": "Grills", "img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500"},
            {"name": "Peri Peri Al Faham (Full)", "price": 680, "cat": "Grills", "img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500"},

            # Mandi Chicken [Meat Only]
            {"name": "Mandi Chicken Meat Only (Quarter)", "price": 150, "cat": "Sides", "img": "https://images.unsplash.com/photo-1562967960-f5549285669f?w=500"},
            {"name": "Mandi Chicken Meat Only (Half)", "price": 280, "cat": "Sides", "img": "https://images.unsplash.com/photo-1562967960-f5549285669f?w=500"},
            {"name": "Mandi Chicken Meat Only (Full)", "price": 500, "cat": "Sides", "img": "https://images.unsplash.com/photo-1562967960-f5549285669f?w=500"},

            # Others
            {"name": "Mayonnaise", "price": 30, "cat": "Extras", "img": "https://images.unsplash.com/photo-1577906096429-f739769f3a4b?w=500"},
            {"name": "Kunafa", "price": 250, "cat": "Desserts", "img": "https://images.unsplash.com/photo-1576777647209-e8733d7b851d?w=500"},
        ]

        count = 0
        for data in items:
            # Check if exists
            if not FoodItem.objects.filter(restaurant=r, name=data["name"]).exists():
                FoodItem.objects.create(
                    restaurant=r,
                    name=data["name"],
                    price=data["price"],
                    category=data["cat"],
                    image_url=data["img"],
                    description=f"Delicious {data['name']}",
                    is_available=True
                )
                print(f"Added: {data['name']}")
                count += 1
            else:
                print(f"Skipped: {data['name']} (Exists)")
        
        print(f"Done. Added {count} items.")
        
    except Restaurant.DoesNotExist:
        print("Restaurant ID 10 not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    populate_alreem()
