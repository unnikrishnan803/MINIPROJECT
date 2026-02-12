from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Order, FoodItem, Restaurant
from .serializers import FoodItemSerializer
from django.db.models import Count, Q, F
from collections import Counter
import datetime

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get personalized recommendations based on user's order history.
        Logic: Content-based filtering (Category & Cuisine preference).
        """
        user = request.user
        
        # 1. Analyze User History (Last 10 orders)
        last_orders = Order.objects.filter(customer=user).order_by('-created_at')[:10]
        
        # Cold Start: If no history, return Trending items
        if not last_orders.exists():
            return self.get_trending_response()
            
        ordered_items_ids = []
        categories = []
        cuisines = []
        
        for order in last_orders:
            for item in order.items.all():
                ordered_items_ids.append(item.id)
                categories.append(item.category)
                cuisines.append(item.restaurant.cuisine_type)
        
        if not categories:
             return self.get_trending_response()
             
        # Determine preferences
        fav_category = Counter(categories).most_common(1)[0][0]
        fav_cuisine = Counter(cuisines).most_common(1)[0][0] if cuisines else None
        
        # 2. Find Similar Items (Same Category OR Same Cuisine)
        # Exclude items already ordered recently
        recommendations = FoodItem.objects.filter(
            is_available=True
        ).filter(
            Q(category=fav_category) | Q(restaurant__cuisine_type=fav_cuisine)
        ).exclude(
            id__in=ordered_items_ids
        ).order_by('-popularity_score', '-trend_score')[:5]
        
        # Fill with trending if not enough recommendations
        if recommendations.count() < 5:
            needed = 5 - recommendations.count()
            trending = FoodItem.objects.filter(is_available=True).exclude(
                id__in=[r.id for r in recommendations]
            ).order_by('-trend_score')[:needed]
            recommendations = list(recommendations) + list(trending)
        
        return Response(FoodItemSerializer(recommendations, many=True).data)

    def get_trending_response(self):
        # Fallback to general trending items
        items = FoodItem.objects.filter(is_available=True).order_by('-trend_score')[:5]
        return Response(FoodItemSerializer(items, many=True).data)

class SmartHighlightsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get Smart Highlights for the dashboard:
        - Trending: High trend_score
        - Fast Selling: Low quantity + High popularity
        - Top Rated: High popularity_score (Proxy for rating)
        """
        # 1. Trending
        trending = FoodItem.objects.filter(
            is_available=True
        ).order_by('-trend_score')[:5]
        
        # 2. Fast Selling (Quantity < 20 and Popular)
        fast_selling = FoodItem.objects.filter(
            is_available=True, 
            quantity_available__lt=20,
            quantity_available__gt=0
        ).order_by('-popularity_score')[:5]
        
        # 3. Top Rated (Using popularity_score as proxy since FoodItem has no direct rating)
        # Or fetch items from Top Rated Restaurants
        # Let's use popularity_score for now
        top_rated = FoodItem.objects.filter(
            is_available=True
        ).order_by('-popularity_score')[:5]
        
        return Response({
            'trending': FoodItemSerializer(trending, many=True).data,
            'fast_selling': FoodItemSerializer(fast_selling, many=True).data,
            'top_rated': FoodItemSerializer(top_rated, many=True).data
        })

class SellingOutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get items predicted to sell out soon.
        """
        selling_out = FoodItem.objects.filter(
            is_available=True,
            estimated_sellout_time__isnull=False
        ).order_by('estimated_sellout_time')[:10]
        
        return Response(FoodItemSerializer(selling_out, many=True).data)
