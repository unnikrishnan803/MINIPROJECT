from django.db import models
from django.contrib.auth.models import AbstractUser
from allauth.account.forms import SignupForm
from django import forms

class User(AbstractUser):
    IS_CUSTOMER = 'customer'
    IS_RESTAURANT = 'restaurant'
    ROLE_CHOICES = [
        (IS_CUSTOMER, 'Customer'),
        (IS_RESTAURANT, 'Restaurant'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=IS_CUSTOMER)
    # Staff linked to a restaurant
    staff_restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    current_location = models.CharField(max_length=100, blank=True, null=True, help_text="User's current city/area for food recommendations")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    currency_symbol = models.CharField(max_length=5, default='₹')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_profile_picture(self):
        """
        Returns the profile picture URL.
        Priority:
        1. User's uploaded profile_picture
        2. Restaurant profile image (if exists)
        3. Social account avatar (if exists)
        4. UI Avatars fallback
        """
        if self.profile_picture:
            return self.profile_picture

        # Check restaurant profile
        # Check restaurant profile
        if hasattr(self, 'restaurant_profile'):
            if self.restaurant_profile.image:
                return self.restaurant_profile.image.url
            if self.restaurant_profile.image_url:
                return self.restaurant_profile.image_url

        # Check social account
        social = self.socialaccount_set.first()
        if social:
            return social.get_avatar_url()
        
        # Fallback
        return f"https://ui-avatars.com/api/?name={self.username}&background=ff6b35&color=fff"

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile')
    name = models.CharField(max_length=100)
    cuisine_type = models.CharField(max_length=50) # e.g. Italian, Indian
    location = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    is_open = models.BooleanField(default=True)
    image = models.ImageField(upload_to='restaurant_profiles/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="URL to a short food video")
    is_available = models.BooleanField(default=True)
    trend_score = models.FloatField(default=0.0) # Calculated by AI logic
    last_updated = models.DateTimeField(auto_now=True)
    
    # New fields for real-time tracking and AI
    quantity_available = models.IntegerField(default=100, help_text="Current quantity available")
    estimated_sellout_time = models.DateTimeField(null=True, blank=True, help_text="Predicted time when item will sell out")
    popularity_score = models.FloatField(default=0.0, help_text="AI-calculated popularity (0-100)")
    preparation_time = models.IntegerField(default=15, help_text="Preparation time in minutes")

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Table(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Booked', 'Booked'),
        ('Occupied', 'Occupied'),
        ('Cleaning', 'Cleaning'),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.IntegerField()
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    class Meta:
        unique_together = ('restaurant', 'table_number')

    def __str__(self):
        return f"Table {self.table_number} ({self.status})"

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    date_time = models.DateTimeField()
    people_count = models.IntegerField()
    status = models.CharField(max_length=20, default='Confirmed') # Confirmed, Cancelled, Completed

    def __str__(self):
        return f"Booking by {self.customer.username} at {self.restaurant.name}"

class Bill(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bills')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Card', 'Card'), ('UPI', 'UPI')], null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='Pending') # Pending, Paid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} for Table {self.table.table_number if self.table else 'Unknown'}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('Preparing', 'Preparing'),
        ('Served', 'Served'), # For Dining
        ('Out for Delivery', 'Out for Delivery'), # For Delivery
        ('Delivered', 'Delivered'), # For Delivery
        ('Paid', 'Paid'),
    ]
    ORDER_TYPE_CHOICES = [
        ('dining', 'Dining'),
        ('delivery', 'Delivery'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True) # Optional for walk-ins
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    items = models.ManyToManyField(FoodItem)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # New Fields for Delivery
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dining')
    delivery_address = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

class FoodAnalytics(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20) # view, click, order

# Social Network Models

class Reel(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reels')
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='reels')
    video_url = models.URLField(help_text="URL to the video file")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reel by {self.restaurant.name}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'restaurant')

    def __str__(self):
        return f"{self.follower.username} follows {self.restaurant.name}"

class ReelLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reel_likes')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reel')

class FoodLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_likes')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food_item')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

# Offer Management Models

class Offer(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percentage = models.IntegerField(help_text="Discount percentage (e.g., 20 for 20%)")
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    target_dishes = models.ManyToManyField(FoodItem, blank=True, related_name='offers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.restaurant.name}"

class UserOffer(models.Model):
    """Track which users have claimed/used offers"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_offers')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='claims')
    claimed_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'offer')
    
    def __str__(self):
        return f"{self.user.username} - {self.offer.title}"

# Notification System

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('offer', 'Offer'),
        ('order', 'Order Update'),
        ('reel', 'New Reel'),
        ('follow', 'Follow Update'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, help_text="Link to relevant content")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

# Restaurant Crowd Tracking

class RestaurantCrowd(models.Model):
    CROWD_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='crowd_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    crowd_level = models.CharField(max_length=20, choices=CROWD_LEVELS, default='Low')
    active_orders = models.IntegerField(default=0)
    occupied_tables = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.crowd_level} at {self.timestamp}"
