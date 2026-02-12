import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User

print("Fixing missing emails...")
updated_count = 0
for user in User.objects.all():
    if not user.email:
        user.email = f"{user.username}@example.com"
        user.save()
        print(f"Updated {user.username} -> {user.email}")
        updated_count += 1
    else:
        print(f"Skipping {user.username} (already has email: {user.email})")

print(f"Fixed {updated_count} users.")
