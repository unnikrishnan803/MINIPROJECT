import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Restaurant

username = "usa_diner"
if User.objects.filter(username=username).exists():
    print(f"User {username} already exists. Deleting...")
    User.objects.get(username=username).delete()

print(f"Creating user {username} with Country=USA...")
user = User.objects.create_user(username=username, email="usa@test.com", password="testpassword123")
user.role = 'restaurant'
user.country = 'USA'
user.currency_symbol = '$'
user.save()

# Create Restaurant Profile
Restaurant.objects.create(
    user=user,
    name="Liberty Burger",
    cuisine_type="American",
    location="New York",
    image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd"
)

print(f"User {username} created successfully.")
print(f"Currency Symbol: {user.currency_symbol}")
