import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User

print(f"{'Username':<20} | {'Email':<30} | {'Role':<15} | {'Password Set'}")
print("-" * 80)
for user in User.objects.all():
    print(f"{user.username:<20} | {user.email:<30} | {user.role:<15} | {user.has_usable_password()}")
