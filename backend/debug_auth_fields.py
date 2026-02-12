import os
import django
from django.conf import settings

# Configure Django settings (minimal needed)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from allauth.account.forms import SignupForm

form = SignupForm()
print("SignupForm fields:")
for name, field in form.fields.items():
    print(f"- Name: '{name}', Label: '{field.label}', Required: {field.required}")
