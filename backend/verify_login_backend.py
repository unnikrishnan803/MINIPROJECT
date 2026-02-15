import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.test import Client

User = get_user_model()
email = 'unni@gmail.com'
password = 'password12'

print(f"--- Debugging Login for {email} ---")

try:
    user = User.objects.get(email=email)
    print(f"1. User found: {user.username} (ID: {user.id})")
    print(f"   Active: {user.is_active}")
    
    # Check password manually
    is_password_correct = user.check_password(password)
    print(f"2. check_password('{password}'): {is_password_correct}")
    
    # Check authenticate()
    # verify if email login is working 
    user_auth_email = authenticate(email=email, password=password)
    print(f"3. authenticate(email='...'): {user_auth_email is not None}")
    
    # verify if username login is working (if applicable)
    user_auth_username = authenticate(username=user.username, password=password)
    print(f"4. authenticate(username='{user.username}'): {user_auth_username is not None}")

    # Simulate Form Submission
    print("\n--- Simulating Login Request ---")
    c = Client()
    # Try logging in with email
    login_url = '/accounts/login/' # Standard allauth url, might need adjustment if custom
    response = c.post(login_url, {'login': email, 'password': password})
    print(f"5. POST to {login_url} with email: Status {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url} (Success likely)")
    else:
        print(f"   Form errors: {response.context.get('form').errors if response.context else 'No context'}")

    # Try logging in with username
    response_u = c.post(login_url, {'login': user.username, 'password': password})
    print(f"6. POST to {login_url} with username: Status {response_u.status_code}")
    if response_u.status_code == 302:
        print(f"   Redirects to: {response_u.url} (Success likely)")
    else:
        print(f"   Form errors: {response_u.context.get('form').errors if response_u.context else 'No context'}")

except User.DoesNotExist:
    print(f"ERROR: User with email {email} not found.")
