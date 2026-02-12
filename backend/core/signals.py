from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.db import transaction
from .models import Restaurant

@receiver(user_signed_up)
def handle_user_signup(request, user, **kwargs):
    # Extract data from request.POST
    data = request.POST if request.POST else {}
    
    role = data.get('role', 'customer')
    country = data.get('country', 'India')
    
    user.role = role
    user.country = country
    
    # Set Currency based on Country
    currency_map = {
        'India': '₹',
        'USA': '$',
        'UK': '£',
        'UAE': 'AED',
        'Canada': 'C$',
    }
    user.currency_symbol = currency_map.get(user.country, '₹')
    
    restaurant_location = data.get('restaurant_location')
    if restaurant_location:
         user.current_location = restaurant_location
         
    user.save()
    
    if role == 'restaurant':
        restaurant_name = data.get('restaurant_name') or f"{user.username}'s Kitchen"
        image_url = data.get('restaurant_image_url')
        opening_time = data.get('opening_time')
        closing_time = data.get('closing_time')
        
        # Avoid duplicates if signal runs twice (rare but possible)
        Restaurant.objects.get_or_create(
            user=user,
            defaults={
                'name': restaurant_name,
                'location': restaurant_location or 'Unknown',
                'image_url': image_url,
                'opening_time': opening_time if opening_time else None,
                'closing_time': closing_time if closing_time else None,
                'cuisine_type': 'General',
                'is_open': True
            }
        )
