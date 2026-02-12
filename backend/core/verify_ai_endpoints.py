import os
import sys
import django
from django.conf import settings

# Add backend to path to find settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from core.ai_views import SellingOutView, SmartHighlightsView, RecommendationView
from core.models import User

def test_endpoints():
    factory = APIRequestFactory()
    
    # 1. Test SellingOutView
    print("\n🔮 Testing SellingOutView...")
    view = SellingOutView.as_view()
    request = factory.get('/api/selling-out/')
    response = view(request)
    print(f"Status Code: {response.status_code}")
    data = response.data
    print(f"Items found: {len(data)}")
    if len(data) > 0:
        print(f"Sample Item: {data[0]['name']} | Sellout: {data[0]['estimated_sellout_time']}")

    # 2. Test SmartHighlightsView
    print("\n🌟 Testing SmartHighlightsView...")
    view = SmartHighlightsView.as_view()
    request = factory.get('/api/smart-highlights/')
    response = view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Keys: {response.data.keys()}")
    print(f"Trending Count: {len(response.data['trending'])}")
    print(f"Fast Selling Count: {len(response.data['fast_selling'])}")

    # 3. Test RecommendationView (Mock User)
    print("\n💡 Testing RecommendationView...")
    user = User.objects.first()
    if user:
        print(f"Simulating for user: {user.username}")
        view = RecommendationView.as_view()
        request = factory.get('/api/recommendations/')
        request.user = user # Force authentication
        response = view(request)
        print(f"Status Code: {response.status_code}")
        print(f"Recommendations count: {len(response.data)}")
    else:
        print("Skipping RecommendationView (No users found)")

if __name__ == "__main__":
    test_endpoints()
