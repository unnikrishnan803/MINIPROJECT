

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Restaurant, FoodItem, Order, FoodAnalytics,
    Offer, UserOffer, Notification, RestaurantCrowd,
    Table, Booking, Reel, Comment, Follow
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('email',)

# Offer Admin
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'restaurant', 'discount_percentage', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'restaurant')
    search_fields = ('title', 'description')

# Notification Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message')

# Register Models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Restaurant)
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(FoodAnalytics)
admin.site.register(Offer, OfferAdmin)
admin.site.register(UserOffer)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(RestaurantCrowd)
admin.site.register(Table)
admin.site.register(Booking)
admin.site.register(Reel)
admin.site.register(Comment)
admin.site.register(Follow)
