import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from allauth.account.forms import SignupForm as AllauthSignupForm
from core.forms import RestaurantSignupForm

print(f"Allauth SignupForm path: {AllauthSignupForm.__module__}")
print(f"RestaurantSignupForm base classes: {RestaurantSignupForm.__bases__}")

for base in RestaurantSignupForm.__mro__:
    print(f"MRO: {base}")

print(f"Issubclass? {issubclass(RestaurantSignupForm, AllauthSignupForm)}")
