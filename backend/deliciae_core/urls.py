"""
URL configuration for deliciae_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import (
    IndexView, LoginView, RegisterView, DashboardView, KitchenView,
    HomeView, ReelsView, OrdersView, ProfileView, SettingsView, SearchView,
    WalletView, BookingsView, OffersView, RestaurantProfileView,
    CartView, CheckoutView, RestaurantVideosView  # New page views
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('accounts/', include('allauth.urls')), # Django Allauth
    
    # Pages
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # New Multi-Page Architecture
    path('home/', HomeView.as_view(), name='home'),
    path('reels/', ReelsView.as_view(), name='reels'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('search/', SearchView.as_view(), name='search'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('bookings/', BookingsView.as_view(), name='bookings'),
    path('offers/', OffersView.as_view(), name='offers'),
    path('cart/', CartView.as_view(), name='cart'),       # NEW
    path('checkout/', CheckoutView.as_view(), name='checkout'), # NEW
    path('restaurant/<int:id>/', RestaurantProfileView.as_view(), name='restaurant_profile'),
    
    # Legacy Dashboard (for restaurant/staff)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('restaurant/dashboard/', DashboardView.as_view(), name='restaurant_dashboard'), # Alias for consistency
    path('kitchen-view/', KitchenView.as_view(), name='kitchen-view'),
    path('restaurant/videos/', RestaurantVideosView.as_view(), name='restaurant_videos'),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
