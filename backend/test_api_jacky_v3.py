import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from django.conf import settings
settings.DEBUG_PROPAGATE_EXCEPTIONS = True
settings.ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']

from rest_framework.test import APIClient
from core.models import User

try:
    user = User.objects.get(username='jacky')
    client = APIClient()
    client.force_authenticate(user=user)
    
    print(f"Testing API for user: {user.username}")
    
    # This should now crash with a traceback if there is an error
    response = client.get('/api/tables/')
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.json()}")

except Exception as e:
    import traceback
    traceback.print_exc()
