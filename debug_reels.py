
import os
import django
from django.conf import settings

import sys
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend')) # Add backend to path specifically
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings') 
django.setup()

from rest_framework.test import APIRequestFactory
from core.models import Reel
from core.serializers import ReelSerializer

def debug_reels():
    print("Debugging Reels Serialization...")
    reels = Reel.objects.all()
    count = reels.count()
    print(f"Found {count} reels.")
    
    factory = APIRequestFactory()
    request = factory.get('/api/reels/')
    # Mock user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.first()
        request.user = user
        print(f"Mocking request with user: {user.username}")
    except:
        print("No users found.")
        
    context = {'request': request}
    
    for reel in reels:
        try:
            print(f"Serializing Reel ID: {reel.id}")
            serializer = ReelSerializer(reel, context=context)
            data = serializer.data
            print("Success.")
            # print(data) 
        except Exception as e:
            print(f"Error serializing Reel {reel.id}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_reels()
