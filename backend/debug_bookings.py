
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User, Booking, Restaurant
from core.serializers import BookingSerializer
from rest_framework.renderers import JSONRenderer

try:
    user = User.objects.get(username='unni1')
    print(f"User found: {user.username} (ID: {user.id})")
    
    bookings = Booking.objects.filter(customer=user)
    print(f"Bookings found: {bookings.count()}")
    
    for booking in bookings:
        print(f"Booking {booking.id}: Table={booking.table}")
        try:
            serializer = BookingSerializer(booking)
            json_data = JSONRenderer().render(serializer.data)
            print(f"Serialized Data: {json_data}")
        except Exception as e:
            print(f"Serialization Error for Booking {booking.id}: {e}")

except User.DoesNotExist:
    print("User 'unni1' not found. Listing all users:")
    for u in User.objects.all():
        print(f"- {u.username}")

