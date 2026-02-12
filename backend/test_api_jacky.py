import os
import django
import sys

# Add backend to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from rest_framework.test import APIClient
from core.models import User

try:
    user = User.objects.get(username='jacky')
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.get('/api/tables/')
    print(f"Status Code: {response.status_code}")
    # Decode response content to string if it's bytes
    print(f"Response Data: {response.content.decode('utf-8')}")

except User.DoesNotExist:
    print("User 'jacky' not found.")
except Exception as e:
    import traceback
    traceback.print_exc()
