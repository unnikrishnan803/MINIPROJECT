from rest_framework import serializers
from .models import (
    FoodItem, Restaurant, Table, Booking, Bill, Order, User, Reel, Comment, Follow,
    Offer, UserOffer, Notification, RestaurantCrowd
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'staff_restaurant']

class RestaurantSerializer(serializers.ModelSerializer):
    currency_symbol = serializers.CharField(source='user.currency_symbol', read_only=True)
    stats = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'cuisine_type', 'location', 'rating', 'image_url', 'currency_symbol', 'stats', 'is_following']

    def get_stats(self, obj):
        return {
            'followers': obj.followers.count(),
            'posts': obj.reels.count()
        }

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(follower=request.user).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_avatar', 'text', 'created_at']
        read_only_fields = ['user']

    def get_user_avatar(self, obj):
        return obj.user.get_profile_picture()

class ReelSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_avatar = serializers.CharField(source='restaurant.image_url', read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    # Limiting comments in list view might be good, but for MVP let's return maybe recent 3 or just count?
    # Actually client can fetch comments separately or we just return count. 
    # Let's return just count + maybe top comment later. For now just fields.
    
    # Food Item Details for "Order Now"
    food_item_id = serializers.IntegerField(source='food_item.id', read_only=True)
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_price = serializers.DecimalField(source='food_item.price', max_digits=10, decimal_places=2, read_only=True)
    is_following_restaurant = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = ['id', 'restaurant', 'restaurant_name', 'restaurant_avatar', 'video_url', 'caption', 'likes_count', 'comments_count', 'is_liked', 'created_at', 'food_item', 'food_item_id', 'food_item_name', 'food_item_price', 'is_following_restaurant']
        read_only_fields = ['restaurant']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
        
    def get_is_following_restaurant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.restaurant.followers.filter(follower=request.user).exists()
        return False

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'restaurant', 'created_at']

class FoodItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)

    currency_symbol = serializers.CharField(source='restaurant.user.currency_symbol', read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'description', 'price', 'category', 'image_url', 'video_url', 
            'is_available', 'trend_score', 'restaurant', 'currency_symbol',
            'quantity_available', 'estimated_sellout_time', 'popularity_score', 'preparation_time'
        ]

class TableSerializer(serializers.ModelSerializer):
    booking_details = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'status', 'restaurant', 'booking_details']

    def get_booking_details(self, obj):
        if obj.status == 'Booked':
            # Get the upcoming or current confirmed booking
            # Simple logic: Confirmed booking with date_time >= now (or just latest)
            from django.utils import timezone
            # Ideally filter by date_time range, but for now just get the next confirmed one
            booking = Booking.objects.filter(table=obj, status='Confirmed', date_time__gte=timezone.now() - timezone.timedelta(hours=2)).order_by('date_time').first()
            if booking:
                return {
                    'customer_name': booking.customer.username,
                    'phone_number': booking.customer.phone_number if booking.customer.phone_number else "N/A",
                    'time': booking.date_time.strftime('%I:%M %p'),
                    'people': booking.people_count
                }
        return None

class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'customer_name', 'restaurant', 'table', 'table_number', 'date_time', 'people_count', 'status']

class OrderSerializer(serializers.ModelSerializer):
    # Nested Items for display
    items_details = FoodItemSerializer(source='items', many=True, read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    restaurant_location = serializers.CharField(source='restaurant.location', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'restaurant_name', 'restaurant_location', 'table', 'table_number', 'items', 'items_details', 'total_amount', 'status', 'created_at']
        extra_kwargs = {
            'restaurant': {'read_only': True},
            'customer': {'read_only': True}
        }

class BillSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'restaurant', 'table', 'table_number', 'total_amount', 'tax_amount', 'grand_total', 'payment_method', 'payment_status', 'orders', 'created_at']

# Offer Management Serializers

class OfferSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    is_claimed = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = ['id', 'restaurant', 'restaurant_name', 'title', 'description', 'discount_percentage', 
                  'valid_from', 'valid_until', 'is_active', 'target_dishes', 'created_at', 
                  'is_claimed', 'time_remaining']
        read_only_fields = ['restaurant']
    
    def get_is_claimed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import UserOffer
            return UserOffer.objects.filter(user=request.user, offer=obj).exists()
        return False
    
    def get_time_remaining(self, obj):
        from django.utils import timezone
        if obj.valid_until > timezone.now():
            delta = obj.valid_until - timezone.now()
            hours = delta.total_seconds() // 3600
            return f"{int(hours)} hours remaining"
        return "Expired"

class UserOfferSerializer(serializers.ModelSerializer):
    offer_details = OfferSerializer(source='offer', read_only=True)
    
    class Meta:
        model = UserOffer
        fields = ['id', 'user', 'offer', 'offer_details', 'claimed_at', 'is_used', 'used_at']
        read_only_fields = ['user']

# Notification Serializer

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'link', 'created_at']
        read_only_fields = ['user']

# Restaurant Crowd Serializer

class RestaurantCrowdSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = RestaurantCrowd
        fields = ['id', 'restaurant', 'restaurant_name', 'timestamp', 'crowd_level', 'active_orders', 'occupied_tables']
        read_only_fields = ['restaurant']
