import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant, User

print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Image':<10} {'Created':<20}")
print("-" * 90)

for r in Restaurant.objects.all():
    image_status = "IMG" if r.image else ("URL" if r.image_url else "NONE")
    print(f"{r.id:<5} {r.name:<25} {r.user.email:<30} {image_status:<10} {r.user.date_joined.strftime('%Y-%m-%d %H:%M')}")

print("\n--- Users with role 'restaurant' without profiles ---")
for u in User.objects.filter(role='restaurant'):
    if not hasattr(u, 'restaurant_profile'):
        print(f"User ID: {u.id}, Email: {u.email} (No Profile)")
