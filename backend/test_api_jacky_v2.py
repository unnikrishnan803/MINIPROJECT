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
    
    print(f"Testing API for user: {user.username} (Role: {user.role}, Restaurant: {user.staff_restaurant})")
    
    response = client.get('/api/tables/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response Data: {response.json()}")
    else:
        # If it's not 200, it might be HTML (500) or JSON (400)
        try:
            print(f"Error JSON: {response.json()}")
        except:
            print(f"Error Content (First 500 chars): {response.content.decode('utf-8')[:500]}")

except User.DoesNotExist:
    print("User 'jacky' not found.")
except Exception as e:
    import traceback
    traceback.print_exc()
