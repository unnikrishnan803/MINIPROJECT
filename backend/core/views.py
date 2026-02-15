from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    FoodItem, User, Table, Booking, Bill, Order, Restaurant, Reel, Comment, Follow, ReelLike, FoodLike,
    Offer, UserOffer, Notification, RestaurantCrowd
)
from .serializers import (
    FoodItemSerializer, TableSerializer, BookingSerializer, BillSerializer, OrderSerializer, 
    RestaurantSerializer, ReelSerializer, CommentSerializer, FollowSerializer,
    OfferSerializer, UserOfferSerializer, NotificationSerializer, RestaurantCrowdSerializer
)
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.conf import settings
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum, F
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from math import radians, sin, cos, sqrt, asin

class IndexView(TemplateView):
    template_name = "index.html"

from allauth.account.views import LoginView as AllauthLoginView, SignupView as AllauthSignupView
from .forms import RestaurantSignupForm

class LoginView(AllauthLoginView):
    template_name = "login.html"

class RegisterView(AllauthSignupView):
    template_name = "register.html"
    form_class = RestaurantSignupForm

from django.contrib.auth.mixins import LoginRequiredMixin

# === NEW MULTI-PAGE VIEWS ===

class HomeView(LoginRequiredMixin, TemplateView):
    """Main home/feed page"""
    template_name = "pages/home.html"
    login_url = '/login/'

class ReelsView(LoginRequiredMixin, TemplateView):
    """Reels video feed page"""
    template_name = "pages/reels.html"
    login_url = '/login/'

class OrdersView(LoginRequiredMixin, TemplateView):
    """Orders tracking page"""
    template_name = "pages/orders.html"
    login_url = '/login/'

class RestaurantVideosView(LoginRequiredMixin, TemplateView):
    """Restaurant videos management page"""
    template_name = "restaurant_videos.html"
    login_url = '/login/'


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile page"""
    template_name = "pages/profile.html"
    login_url = '/login/'

class SettingsView(LoginRequiredMixin, TemplateView):
    """Settings page"""
    template_name = "pages/settings.html"
    login_url = '/login/'

from django.db.models import Q

class SearchView(LoginRequiredMixin, TemplateView):
    """Search page"""
    template_name = "pages/search.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('type', 'all')
        sort_by = self.request.GET.get('sort', '')
        
        context['query'] = query
        context['filter_type'] = filter_type
        context['sort_by'] = sort_by

        restaurants = Restaurant.objects.all()
        food_items = FoodItem.objects.all()

        if query:
            restaurants = restaurants.filter(
                Q(name__icontains=query) | 
                Q(cuisine_type__icontains=query) | 
                Q(location__icontains=query)
            ).distinct()
            
            food_items = food_items.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) | 
                Q(category__icontains=query) |
                Q(restaurant__name__icontains=query)
            ).select_related('restaurant').distinct()
            
            # 🧠 AI Logic: Log 'search' interaction for matched items
            # This feeds into the Trend Score = (search * 0.3) formula
            if self.request.user.is_authenticated:
                for item in food_items:
                    FoodAnalytics.objects.create(food_item=item, interaction_type='search')
        else:
            # Default ordering if no specific query
            if not sort_by:
                restaurants = restaurants.order_by('-rating')
                food_items = food_items.order_by('-trend_score')

        # Apply Sorting
        if sort_by == 'top_rated':
            restaurants = restaurants.order_by('-rating')
            food_items = food_items.order_by('-popularity_score', '-trend_score') # Food doesn't have rating field in model yet, usage popularity/trend

        # Apply Filtering (Type)
        if filter_type == 'restaurants':
            context['restaurants'] = restaurants[:20]
            context['food_items'] = []
        elif filter_type == 'dishes':
            context['restaurants'] = []
            context['food_items'] = food_items[:50]
        else:
            context['restaurants'] = restaurants[:20]
            context['food_items'] = food_items[:50]
            
        return context

class WalletView(LoginRequiredMixin, TemplateView):
    """Wallet page"""
    template_name = "pages/wallet.html"
    login_url = '/login/'

class BookingsView(LoginRequiredMixin, TemplateView):
    """Bookings page"""
    template_name = "pages/bookings.html"
    login_url = '/login/'

# Import shortcut
from django.shortcuts import get_object_or_404

class RestaurantProfileView(LoginRequiredMixin, TemplateView):
    """Dedicated Restaurant Profile Page"""
    template_name = "pages/restaurant_profile.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs.get('id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        context['restaurant'] = restaurant
        context['posts'] = Reel.objects.filter(restaurant=restaurant).order_by('-created_at')
        context['menu'] = FoodItem.objects.filter(restaurant=restaurant, is_available=True)
        # Reviews to be added later
        
        # Check if following
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(follower=self.request.user, restaurant=restaurant).exists()
        else:
            context['is_following'] = False
            
        return context



class WalletView(LoginRequiredMixin, TemplateView):
    """User wallet page"""
    template_name = "pages/wallet.html"
    login_url = '/login/'

class BookingsView(LoginRequiredMixin, TemplateView):
    """Table bookings page"""
    template_name = "pages/bookings.html"
    login_url = '/login/'

class CartView(LoginRequiredMixin, TemplateView):
    """Shopping Cart page"""
    template_name = "pages/cart.html"
    login_url = '/login/'

class CheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout page"""
    template_name = "pages/checkout.html"
    login_url = '/login/'

class OffersView(LoginRequiredMixin, TemplateView):
    """Offers and deals page"""
    template_name = "pages/offers.html"
    login_url = '/login/'

# === LEGACY DASHBOARD VIEW (for restaurant/staff) ===

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect customers to new home page
        if request.user.is_authenticated and request.user.role == 'customer':
            from django.shortcuts import redirect
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        user = self.request.user
        if user.role == 'restaurant':
            if self.request.GET.get('view') == 'tables':
                return ["staff_dashboard.html"]
            return ["restaurant_dashboard.html"]
        elif user.role == 'staff':
            return ["staff_dashboard.html"]
        return ["dashboard.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'restaurant':
            context['is_restaurant'] = True
            user = self.request.user
            
            # Calculate Stats
            context['total_orders'] = Order.objects.filter(restaurant__user=user).count()
            
            # Revenue (Sum of paid bills or just orders for now)
            # customized for simplicity: sum of total_amount of all orders for this restaurant
            from django.db.models import Sum
            revenue = Order.objects.filter(restaurant__user=user).aggregate(Sum('total_amount'))['total_amount__sum']
            context['revenue'] = revenue if revenue else 0
            
            # Trending Count (Arbitrary threshold for now, e.g. trend_score > 50 or top 3)
            context['trending_count'] = FoodItem.objects.filter(restaurant__user=user, trend_score__gt=0).count()
            
        return context

class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = FoodItem.objects.all()
        user = self.request.user
        
        # Role-based filtering
        if user.is_authenticated and user.role == 'restaurant':
            queryset = queryset.filter(restaurant__user=user)

        # Location-based filtering (Optional)
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius') # in km

        if lat and lng and radius:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                
                # Bounding Box Calculation (Approximate)
                # 1 degree lat ~= 111km
                degree_delta = radius / 111.0
                
                lat_min = lat - degree_delta
                lat_max = lat + degree_delta
                # Longitude correction (cos(lat))
                # optimization: just use max degree delta for lng too (slightly larger box is fine)
                lng_min = lng - degree_delta
                lng_max = lng + degree_delta

                queryset = queryset.filter(
                    restaurant__latitude__range=(lat_min, lat_max),
                    restaurant__longitude__range=(lng_min, lng_max)
                )
            except ValueError:
                pass # Ignore invalid params

        return queryset


    def perform_create(self, serializer):
        # Automatically set the restaurant from the logged-in user
        if self.request.user.role == 'restaurant':
            serializer.save(restaurant=self.request.user.restaurant_profile)
        else:
            raise serializers.ValidationError("Only restaurant users can create food items.")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        food = self.get_object()
        like, created = FoodLike.objects.get_or_create(user=request.user, food_item=food)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': food.likes.count()})
        return Response({'status': 'liked', 'likes_count': food.likes.count()})

from rest_framework import filters

class FoodListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['trend_score', 'price', 'rating', 'created_at', 'popularity_score']
    ordering = ['-trend_score'] # Default to trending

    def get_queryset(self):
        queryset = FoodItem.objects.all()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        
        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Location Logic
        if location:
            # Explicit filter from UI
            queryset = queryset.filter(restaurant__location__icontains=location)
        # REMOVED LEGACY TEXT-BASED NEARBY LOGIC
        # Now relying strictly on GPS-based NearbyRestaurantsAPIView
            
        return queryset

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny] # Allow public access

    def get_queryset(self):
        queryset = Restaurant.objects.filter(is_open=True)
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # REMOVED LEGACY LOCATION FILTER
        # if location:
        #    queryset = queryset.filter(location__icontains=location)
            
        return queryset

class TrendView(generics.ListAPIView):
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        # Return top 5 items sorted by trend_score descending
        return FoodItem.objects.order_by('-trend_score')[:5]

from .utils import calculate_trend_scores, calculate_trending_reels

class RefreshTrendView(APIView):
    """
    API to manually trigger AI Trend Calculation.
    In production, this would be a Celery task.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        calculate_trend_scores()
        calculate_trending_reels()
        return Response({'status': 'AI Trend Scores Refreshed', 'message': 'Successfully recalculated trends based on orders, searches, and reels.'})

class AvailabilityToggleView(APIView):
    def post(self, request):
        calculate_trend_scores()
        calculate_trending_reels()
        return Response({'status': 'AI Trend Scores Refreshed', 'message': 'Successfully recalculated trends based on orders, searches, and reels.'})

class DemandPredictionView(APIView):
    """
    🧠 AI Future Demand Prediction (Mock/Basic)
    Predicts demand based on Day of Week and Time.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        import datetime
        today = datetime.datetime.now().strftime("%A") # e.g., 'Friday'
        
        # Simple Rule-Based AI Logic
        if today in ['Friday', 'Saturday', 'Sunday']:
            prediction = {
                "day": today,
                "demand_level": "High 📈",
                "peak_hours": "19:00 - 22:00",
                "reason": "Weekend Rush + High Search Volume",
                "suggested_prep": "Prepare extra biryani and starters."
            }
        elif today in ['Tuesday']:
            prediction = {
                "day": today,
                "demand_level": "Low 📉",
                "peak_hours": "20:00 - 21:00",
                "reason": "Mid-week lull",
                "suggested_prep": "Focus on offers to boost sales."
            }
        else:
            prediction = {
                "day": today,
                "demand_level": "Medium 📊",
                "peak_hours": "19:30 - 21:30",
                "reason": "Standard Weekday",
                "suggested_prep": "Standard inventory sufficient."
            }
            
        return Response(prediction)

class AvailabilityToggleView(APIView):
    def post(self, request, pk):
        try:
            food_item = FoodItem.objects.get(pk=pk)
            # In real app, check if request.user == food_item.restaurant.user
            food_item.is_available = not food_item.is_available
            food_item.save()
            return Response({'status': 'success', 'is_available': food_item.is_available})
        except FoodItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def available_food_items(request):
    """
    List all available food items.
    """
    items = FoodItem.objects.filter(is_available=True)
    serializer = FoodItemSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def toggle_food_availability(request, pk):
    """
    Toggle the availability status of a food item.
    """
    try:
        food_item = FoodItem.objects.get(pk=pk)
        # Check permissions if necessary
        food_item.is_available = not food_item.is_available
        food_item.save()
        return Response({'status': 'success', 'is_available': food_item.is_available})
    except FoodItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

# --- DINE-IN MODULE VIEWS ---

class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Table.objects.all()
        
        # Allow fetching tables for a specific restaurant (e.g., for booking)
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
             return queryset.filter(restaurant_id=restaurant_id)

        if user.role == 'restaurant':
            return Table.objects.filter(restaurant__user=user)
        if user.role == 'staff' and hasattr(user, 'staff_restaurant'):
             return Table.objects.filter(restaurant=user.staff_restaurant)
             
        # By default return nothing if no context
        return Table.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'restaurant':
            serializer.save(restaurant=user.restaurant_profile)
        elif user.role == 'staff' and hasattr(user, 'staff_restaurant'):
            serializer.save(restaurant=user.staff_restaurant)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'restaurant':
            return Booking.objects.filter(restaurant__user=user)
        if user.role == 'staff' and user.staff_restaurant:
             return Booking.objects.filter(restaurant=user.staff_restaurant)
        
        return Booking.objects.filter(customer=user)

    def perform_create(self, serializer):
        # 🧠 Smart Booking Logic: Conflict Detection
        table = serializer.validated_data.get('table')
        date_time = serializer.validated_data.get('date_time')
        restaurant = serializer.validated_data.get('restaurant')
        
        if table:
            # Check for existing confirmed bookings for this table within +/- 1 hour
            # (Assuming strict slot booking, or we can just check exact time)
            from datetime import timedelta
            
            start_time = date_time - timedelta(minutes=59)
            end_time = date_time + timedelta(minutes=59)
            
            conflicts = Booking.objects.filter(
                table=table,
                date_time__range=(start_time, end_time),
                status='Confirmed'
            )
            
            if conflicts.exists():
                # 🧠 AI Suggestion Mock: Suggest next available time (e.g. +1 hour)
                next_slot = date_time + timedelta(hours=1)
                raise serializers.ValidationError(
                    f"Table is already booked at this time. Suggestion: Try {next_slot.strftime('%H:%M')}."
                )
        
        serializer.save(customer=self.request.user)

class DiningOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all()
        
        # Filter by Role
        if user.role == 'restaurant':
            queryset = queryset.filter(restaurant__user=user)
        elif user.role == 'staff' and user.staff_restaurant:
            queryset = queryset.filter(restaurant=user.staff_restaurant)
        elif user.role == 'customer':
            queryset = queryset.filter(customer=user)
            
        # Filter by Status (for Kitchen Display)
        status = self.request.query_params.get('status')
        if status:
            statuses = status.split(',')
            queryset = queryset.filter(status__in=statuses)
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        order = None
        
        # 1. Determine Restaurant & Customer based on Role
        if user.role == 'staff' and user.staff_restaurant:
             order = serializer.save(restaurant=user.staff_restaurant, customer=None)
        elif user.role == 'restaurant':
             order = serializer.save(restaurant=user.restaurant_profile, customer=None)
        else:
             # Customer or Walk-in logic
             restaurant_id = self.request.data.get('restaurant')
             if restaurant_id:
                 try:
                     restaurant = Restaurant.objects.get(id=restaurant_id)
                     order = serializer.save(customer=user, restaurant=restaurant)
                 except Restaurant.DoesNotExist:
                     raise serializers.ValidationError("Invalid restaurant ID")
             else:
                 raise serializers.ValidationError("Restaurant ID required for customer orders")
        
        # 2. Real-Time Availability Logic 🧠
        # Decrement stock and auto-hide if empty
        if order:
            for item in order.items.all():
                if item.quantity_available > 0:
                    item.quantity_available -= 1
                    
                    # Logic: When stock = 0 -> Automatically hide item
                    if item.quantity_available <= 0:
                        item.is_available = False
                    
                    item.save()

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'updated'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class BillingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        action = request.data.get('action') # 'generate' or 'pay'
        table_id = request.data.get('table_id')
        
        if not table_id:
             return Response({'error': 'Table ID required'}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            table = Table.objects.get(pk=table_id)
        except Table.DoesNotExist:
            return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'generate':
            # Fetch unbilled, served orders for this table
            orders = Order.objects.filter(table=table, status='Served', bill__isnull=True)
            if not orders.exists():
                return Response({'error': 'No unbilled orders found for this table'}, status=status.HTTP_400_BAD_REQUEST)
            
            total = sum(order.total_amount for order in orders)
            tax = total * 0.05 # 5% Tax
            grand_total = float(total) + float(tax) # simplified
            
            with transaction.atomic():
                bill = Bill.objects.create(
                    restaurant=table.restaurant,
                    table=table,
                    total_amount=total,
                    tax_amount=tax,
                    grand_total=grand_total
                )
                orders.update(bill=bill)
                
            return Response(BillSerializer(bill).data)

        elif action == 'pay':
            bill_id = request.data.get('bill_id')
            payment_method = request.data.get('payment_method')
            
            try:
                bill = Bill.objects.get(pk=bill_id)
            except Bill.DoesNotExist:
                 return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)
            
            with transaction.atomic():
                bill.payment_method = payment_method
                bill.payment_status = 'Paid'
                bill.save()
                
                # Mark Orders as Paid
                bill.orders.update(status='Paid')
                
                # Mark Table as Available (or Cleaning)
                table.status = 'Cleaning'
                table.save()
                
            return Response({'status': 'Payment Successful', 'table_status': table.status})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth.mixins import LoginRequiredMixin

class KitchenView(LoginRequiredMixin, TemplateView):
    template_name = "kitchen_dashboard.html"
    login_url = '/login/'
    redirect_field_name = 'next'

# --- SOCIAL NETWORK VIEWS ---

class ReelViewSet(viewsets.ModelViewSet):
    serializer_class = ReelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Reel.objects.all().order_by('-created_at')
        
        # Filter by specific restaurant (for "My Posts" page)
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        # Filter by trending
        trending = self.request.query_params.get('trending')
        if trending == 'true':
            queryset = queryset.filter(is_trending=True).order_by('-engagement_score')
            
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role == 'restaurant':
            serializer.save(restaurant=self.request.user.restaurant_profile)
        else:
            raise serializers.ValidationError("Only restaurants can post reels.")
    
    def perform_update(self, serializer):
        """Ensure only the reel owner can edit it"""
        reel = self.get_object()
        if reel.restaurant.user != self.request.user:
            raise PermissionDenied("You can only edit your own reels")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure only the reel owner can delete it"""
        if instance.restaurant.user != self.request.user:
            raise PermissionDenied("You can only delete your own reels")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        reel = self.get_object()
        like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': reel.likes.count()})
        return Response({'status': 'liked', 'likes_count': reel.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        reel = self.get_object()
        text = request.data.get('text')
        if not text:
            return Response({'error': 'Text required'}, status=400)
        comment = Comment.objects.create(user=request.user, reel=reel, text=text)
        return Response(CommentSerializer(comment).data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        reel = self.get_object()
        comments = reel.comments.order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload(self, request):
        if request.user.role != 'restaurant':
            return Response({'error': 'Only restaurants can upload reels'}, status=403)
        
        video_file = request.FILES.get('video_file')
        image_file = request.FILES.get('image_file')
        caption = request.data.get('caption', '')
        
        if not video_file and not image_file:
            return Response({'error': 'No media file provided'}, status=400)
        
        import os
        from django.conf import settings
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import uuid

        restaurant = request.user.restaurant_profile
        
        if video_file:
            # Handle Video
            ext = os.path.splitext(video_file.name)[1]
            filename = f"reels/videos/{uuid.uuid4()}{ext}"
            path = default_storage.save(filename, ContentFile(video_file.read()))
            video_url = f"{settings.MEDIA_URL}{path}"
            
            reel = Reel.objects.create(
                restaurant=restaurant,
                video_url=video_url,
                is_video=True,
                caption=caption
            )
        else:
            # Handle Image
            # Use the model's ImageField which handles storage automatically
            reel = Reel.objects.create(
                restaurant=restaurant,
                image=image_file,
                is_video=False,
                caption=caption
            )
            # Populate image_url for API consistency if needed (though serializer handles image.url)
            if reel.image:
                reel.image_url = reel.image.url
                reel.save()

        return Response(ReelSerializer(reel).data)

class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        restaurant_id = request.data.get('restaurant_id')
        if not restaurant_id:
             return Response({'error': 'Restaurant ID required'}, status=400)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant not found'}, status=404)

        follow, created = Follow.objects.get_or_create(follower=request.user, restaurant=restaurant)
        if not created:
            follow.delete()
            return Response({'status': 'unfollowed', 'followers_count': restaurant.followers.count()})
        return Response({'status': 'followed', 'followers_count': restaurant.followers.count()})

# --- OFFER MANAGEMENT VIEWS ---

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        # Restaurant Admin: View ALL their own offers (Active & Inactive)
        if user.is_authenticated and user.role == 'restaurant':
            # Assuming One-to-One or Foreign Key from User to RestaurantProfile
            # Check if restaurant_profile exists
            if hasattr(user, 'restaurant_profile'):
                return Offer.objects.filter(restaurant=user.restaurant_profile).order_by('-created_at')
        
        # Customers / Public: View ONLY Active offers
        queryset = Offer.objects.filter(is_active=True)
        
        # Filter by location if user is authenticated
        if user.is_authenticated and user.current_location:
            queryset = queryset.filter(restaurant__location__icontains=user.current_location)
        
        # Filter by followed restaurants
        followed = self.request.query_params.get('followed')
        if followed == 'true' and user.is_authenticated:
            followed_restaurants = user.following.values_list('restaurant', flat=True)
            queryset = queryset.filter(restaurant__in=followed_restaurants)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Only restaurant users can create offers
        if self.request.user.role == 'restaurant':
            serializer.save(restaurant=self.request.user.restaurant_profile)
        else:
            raise serializers.ValidationError("Only restaurant users can create offers.")
            
    def perform_update(self, serializer):
        if self.request.user.role != 'restaurant':
             raise serializers.PermissionDenied("Only restaurants can edit offers.")
        serializer.save()

    def perform_destroy(self, instance):
         if self.request.user.role != 'restaurant' or instance.restaurant != self.request.user.restaurant_profile:
             raise serializers.PermissionDenied("You do not have permission to delete this offer.")
         instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def claim(self, request, pk=None):
        """Allow users to claim an offer"""
        offer = self.get_object()
        user_offer, created = UserOffer.objects.get_or_create(user=request.user, offer=offer)
        
        if created:
            # Create notification for user
            Notification.objects.create(
                user=request.user,
                title="Offer Claimed!",
                message=f"You've claimed: {offer.title}",
                notification_type='offer',
                link=f"/offers/{offer.id}"
            )
            return Response({'status': 'claimed', 'message': 'Offer claimed successfully!'})
        return Response({'status': 'already_claimed', 'message': 'You have already claimed this offer.'})

# --- NOTIFICATION VIEWS ---

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own notifications
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked_read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all_marked_read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

# --- RESTAURANT CROWD TRACKING ---

class RestaurantCrowdViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RestaurantCrowdSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = RestaurantCrowd.objects.all()
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset.order_by('-timestamp')[:1]  # Get latest crowd data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_crowd_status(request):
    """Restaurant owners can update their crowd status"""
    if request.user.role != 'restaurant':
        return Response({'error': 'Only restaurants can update crowd status'}, status=403)
    
    restaurant = request.user.restaurant_profile
    
    # Calculate crowd level based on active orders and occupied tables
    active_orders = Order.objects.filter(
        restaurant=restaurant, 
        status__in=['Ordered', 'Preparing']
    ).count()
    
    occupied_tables = Table.objects.filter(
        restaurant=restaurant,
        status__in=['Occupied', 'Booked']
    ).count()
    
    # Determine crowd level
    if active_orders < 5 and occupied_tables < 3:
        crowd_level = 'Low'
    elif active_orders < 15 and occupied_tables < 8:
        crowd_level = 'Medium'
    else:
        crowd_level = 'High'
    
    # Create crowd record
    crowd = RestaurantCrowd.objects.create(
        restaurant=restaurant,
        crowd_level=crowd_level,
        active_orders=active_orders,
        occupied_tables=occupied_tables
    )
    
    serializer = RestaurantCrowdSerializer(crowd)
    return Response(serializer.data)





# === LOCATION BASED SEARCH VIEW ===

from math import radians, cos, sin, asin, sqrt

class NearbyRestaurantsAPIView(APIView):
    """
    API View to fetch restaurants based on user's location (latitude, longitude).
    Defaults to 5km radius.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_lat = float(request.query_params.get('lat'))
            user_lng = float(request.query_params.get('lng'))
            radius_km = float(request.query_params.get('radius', 20.0)) # Default to 20km as requested
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid latitude, longitude, or radius Parameters. Must be numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optimization: First filter by a rough bounding box
        # 1 deg lat ~= 111km. 
        degrees_delta = radius_km / 111.0
        # Add a small buffer for edge cases, but keep it tight
        degrees_delta *= 1.1 
        
        lat_min = user_lat - degrees_delta
        lat_max = user_lat + degrees_delta
        lng_min = user_lng - degrees_delta
        lng_max = user_lng + degrees_delta

        print(f"DEBUG: Bounding Box: {lat_min} to {lat_max}, {lng_min} to {lng_max}")

        candidates = Restaurant.objects.filter(
            latitude__range=(lat_min, lat_max),
            longitude__range=(lng_min, lng_max),
            is_open=True
        )
        print(f"DEBUG: Candidates found: {candidates.count()}")

        nearby_restaurants = []

        for restaurant in candidates:
            if restaurant.latitude is None or restaurant.longitude is None:
                continue

            # Haversine Formula
            lon1, lat1, lon2, lat2 = map(radians, [user_lng, user_lat, restaurant.longitude, restaurant.latitude])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371 # Radius of earth in kilometers
            distance = c * r

            print(f"DEBUG: User Location: {user_lat}, {user_lng} | Radius: {radius_km}")

            if distance <= radius_km:
                print(f"DEBUG: Keeping {restaurant.name} (Dist: {distance:.2f}km)")
                serializer = RestaurantSerializer(restaurant, context={'request': request})
                data = serializer.data
                data['distance_km'] = round(distance, 2)
                nearby_restaurants.append(data)
            else:
                print(f"DEBUG: Skipping {restaurant.name} (Dist: {distance:.2f}km > {radius_km}km)")

        # Sort by distance
        nearby_restaurants.sort(key=lambda x: x['distance_km'])

        return Response(nearby_restaurants)

class RestaurantProfileUpdateView(generics.UpdateAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure the user has a restaurant profile
        if not hasattr(self.request.user, 'restaurant_profile'):
             raise serializers.ValidationError("User is not a restaurant.")
        return self.request.user.restaurant_profile

    def update(self, request, *args, **kwargs):
        # Handle 'image' file upload specifically if present
        # The serializer handles it, but we need to ensure request.FILES is used
        return super().update(request, *args, **kwargs)

class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
