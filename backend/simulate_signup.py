import os
import django
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.views import RegisterView
from core.forms import RestaurantSignupForm

def simulate_signup():
    factory = RequestFactory()
    url = '/register/'
    
    # Simulate a POST request with all required fields
    data = {
        'role': 'customer',
        'country': 'India',
        'email': 'testuser@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!',
        'csrfmiddlewaretoken': 'fake-token'
    }
    
    request = factory.post(url, data)
    # We need to add session and messages if the view uses them, but let's just check the form first
    
    form = RestaurantSignupForm(data=data)
    print(f"Form fields: {list(form.fields.keys())}")
    for name, field in form.fields.items():
        print(f"Field: {name}, Required: {field.required}")
    
    print(f"Form is valid? {form.is_valid()}")
    if not form.is_valid():
        print(f"Form errors: {form.errors.as_json()}")

if __name__ == "__main__":
    simulate_signup()
