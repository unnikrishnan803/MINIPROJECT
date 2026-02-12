import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

try:
    import core
    print(f"Core module: {core}")
    print(f"Core file: {core.__file__}")
    
    import core.auth_forms
    print(f"Auth forms file: {core.auth_forms.__file__}")
    print(f"Dir auth_forms: {dir(core.auth_forms)}")

    from core.auth_forms import CustomSignupForm
    print("Import successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
