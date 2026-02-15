import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = 'unni@gmail.com'
users = User.objects.filter(email=email)

if users.exists():
    for u in users:
        print(f"User Found: {u.username}")
        print(f"Email: {u.email}")
        print(f"Active: {u.is_active}")
        print(f"Has Usable Password: {u.has_usable_password()}")
        # Check if password matches 'password123' (we can't check actual hash, but can check if it verifies)
        print(f"Check 'password123': {u.check_password('password123')}")
else:
    print(f"No user found with email {email}")

print("-" * 20)
print("All Users:")
for u in User.objects.all():
    print(f"{u.username} | {u.email}")
