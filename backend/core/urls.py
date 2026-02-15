from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    IndexView, LoginView, RegisterView, DashboardView,
    HomeView, ReelsView, OrdersView, ProfileView, SettingsView, WalletView, BookingsView,  # New page views
    FoodItemViewSet, available_food_items, toggle_food_availability,
    TableViewSet, BookingViewSet, DiningOrderViewSet, BillingView,
    FoodListView, KitchenView, RestaurantViewSet,
    ReelViewSet, FollowViewSet,
    OfferViewSet, NotificationViewSet, RestaurantCrowdViewSet, update_crowd_status,
    NearbyRestaurantsAPIView, RestaurantProfileUpdateView, UserUpdateAPIView,
    RefreshTrendView, DemandPredictionView
)
from .ai_views import RecommendationView, SmartHighlightsView, SellingOutView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'food-items', FoodItemViewSet, basename='fooditem')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'dining-orders', DiningOrderViewSet, basename='dining-orders')
router.register(r'reels', ReelViewSet, basename='reel')
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'crowd', RestaurantCrowdViewSet, basename='crowd')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')


urlpatterns = [
    # API Routes
    path('', include(router.urls)),
    path('food/', FoodListView.as_view(), name='food-list'),
    path('food/available/', available_food_items, name='available_food_items'),
    path('food/<int:pk>/toggle/', toggle_food_availability, name='toggle_food_availability'),
    path('api/billing/', BillingView.as_view(), name='billing'),
    path('crowd/update/', update_crowd_status, name='update-crowd-status'),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('smart-highlights/', SmartHighlightsView.as_view(), name='smart-highlights'),
    path('selling-out/', SellingOutView.as_view(), name='selling-out'),
    path('nearby-restaurants/', NearbyRestaurantsAPIView.as_view(), name='nearby-restaurants'),
    path('restaurant/profile/', RestaurantProfileUpdateView.as_view(), name='restaurant-profile-update'),
    path('user/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('trends/refresh/', RefreshTrendView.as_view(), name='refresh-trends'),
    path('predict/demand/', DemandPredictionView.as_view(), name='predict-demand'),
]
