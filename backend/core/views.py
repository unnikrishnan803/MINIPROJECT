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
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated

class IndexView(TemplateView):
    template_name = "index.html"

class LoginView(TemplateView):
    template_name = "login.html"

class RegisterView(TemplateView):
    template_name = "register.html"

from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    
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
        user = self.request.user
        if user.is_authenticated and user.role == 'restaurant':
            return FoodItem.objects.filter(restaurant__user=user)
        return FoodItem.objects.all()

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

class FoodListView(generics.ListAPIView):
    serializer_class = FoodItemSerializer

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
        elif self.request.user.is_authenticated and self.request.user.current_location:
            # Auto-filter by user's location (Nearby)
            # You might want to make this optional or a default separate section
            # For now, if no explicit location is asked, prioritize nearby?
            # Or maybe only if a 'nearby' param is passed? 
            # The user asked: "share user nearby location based on hotel sets"
            # Let's assume the main feed SHOULD be location based.
            queryset = queryset.filter(restaurant__location__icontains=self.request.user.current_location)
            
        return queryset

class RestaurantListView(generics.ListAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny] # Allow public access

    def get_queryset(self):
        queryset = Restaurant.objects.filter(is_open=True)
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset

class TrendView(generics.ListAPIView):
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        # Return top 5 items sorted by trend_score descending
        return FoodItem.objects.order_by('-trend_score')[:5]

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
        if user.role == 'restaurant':
            return Table.objects.filter(restaurant__user=user)
        if user.role == 'staff' and user.staff_restaurant:
             return Table.objects.filter(restaurant=user.staff_restaurant)
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
        # Staff creating order for a table
        if user.role == 'staff' and user.staff_restaurant:
             serializer.save(restaurant=user.staff_restaurant, customer=None)
        # Restaurant creating order
        elif user.role == 'restaurant':
             serializer.save(restaurant=user.restaurant_profile, customer=None)
        # Customer creating order (if allowed)
        # Customer creating order (if allowed)
        else:
             # Find restaurant from request data
             restaurant_id = self.request.data.get('restaurant')
             if restaurant_id:
                 try:
                     restaurant = Restaurant.objects.get(id=restaurant_id)
                     serializer.save(customer=user, restaurant=restaurant)
                 except Restaurant.DoesNotExist:
                     raise serializers.ValidationError("Invalid restaurant ID")
             else:
                 # Try to infer from first item? Too complex for now.
                 # Let's require restaurant ID in payload.
                 raise serializers.ValidationError("Restaurant ID required for customer orders")

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
    queryset = Reel.objects.all().order_by('-created_at')
    serializer_class = ReelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role == 'restaurant':
            serializer.save(restaurant=self.request.user.restaurant_profile)
        else:
            raise serializers.ValidationError("Only restaurants can post reels.")

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



# --- SOCIAL FEATURES VIEWS ---

class ReelViewSet(viewsets.ModelViewSet):
    serializer_class = ReelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Reel.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.role == 'restaurant':
            serializer.save(restaurant=self.request.user.restaurant_profile)
        else:
            raise serializers.ValidationError("Only restaurant users can upload reels.")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        reel = self.get_object()
        like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': reel.likes.count()})
        return Response({'status': 'liked', 'likes_count': reel.likes.count()})

class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_follow(self, request):
        restaurant_id = request.data.get('restaurant_id')
        if not restaurant_id:
            return Response({'error': 'Restaurant ID required'}, status=400)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            follow, created = Follow.objects.get_or_create(follower=request.user, restaurant=restaurant)
            
            if not created:
                follow.delete()
                return Response({'status': 'unfollowed', 'restaurant_id': restaurant_id})
            
            return Response({'status': 'followed', 'restaurant_id': restaurant_id})
        except Restaurant.DoesNotExist:
            return Response({'error': 'Restaurant not found'}, status=404)
