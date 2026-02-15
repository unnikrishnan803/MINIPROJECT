import os
import django
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import User
from allauth.account.models import EmailAddress

def test_login(login_input, password):
    print(f"Testing login with: {login_input}")
    user = authenticate(request=None, login=login_input, password=password)
    if user:
        print(f"SUCCESS: Logged in as {user.username} (Email: {user.email})")
    else:
        print(f"FAILED: Could not authenticate {login_input}")

# Find a user with an email
user = User.objects.filter(email__contains='@').first()
if user:
    # We might not know the password, so let's set it to something known for testing
    password = "password123"
    user.set_password(password)
    user.save()
    
    print(f"User found: {user.username} with email: {user.email}")
    
    # Ensure EmailAddress exist for allauth
    EmailAddress.objects.get_or_create(user=user, email=user.email, primary=True, verified=True)
    
    test_login(user.username, password)
    test_login(user.email, password)
else:
    print("No user with email found to test.")
