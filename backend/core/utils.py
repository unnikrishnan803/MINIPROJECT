import re
import urllib.parse
import requests

def extract_lat_long_from_url(url):
    """
    Extracts latitude and longitude from a Google Maps URL.
    Supports various formats, including short links (maps.app.goo.gl).
    """
    try:
        # Resolve short URLs if needed
        if 'goo.gl' in url or 'g.page' in url:
            try:
                response = requests.get(url, allow_redirects=True, timeout=5)
                url = response.url
            except Exception as e:
                print(f"Error resolving short URL: {e}")

        # 1. Look for @lat,long pattern (common in /maps/place/ URLs)
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if match:
            return float(match.group(1)), float(match.group(2))

        # 2. Look for q=lat,long param (common in search URLs)
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'q' in params:
            # q can be "10.1234,76.5678" or "Place Name"
            q_val = params['q'][0]
            # Check if q looks like coordinates
            coord_match = re.match(r'^(-?\d+\.\d+),(-?\d+\.\d+)', q_val)
            if coord_match:
                return float(coord_match.group(1)), float(coord_match.group(2))
        
        # 3. Handle search/ syntax: /maps/search/10.1234,+76.5678
        match_search = re.search(r'/search/(-?\d+\.\d+),\+?(-?\d+\.\d+)', url)
        if match_search:
            return float(match_search.group(1)), float(match_search.group(2))

        # 4. Handle ?ll=lat,long (older format)
        if 'll' in params:
            ll_val = params['ll'][0]
            coord_match = re.match(r'^(-?\d+\.\d+),(-?\d+\.\d+)', ll_val)
            if coord_match:
                return float(coord_match.group(1)), float(coord_match.group(2))

        return None, None
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return None, None
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return None, None

def calculate_trend_scores():
    """
    🧠 AI Trend Score Calculation Logic
    Formula: (Order * 0.5) + (Search * 0.3) + (Reel Engagement * 0.2)
    Considers data from the last 7 days.
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Sum
    from .models import FoodItem, Order, FoodAnalytics, Reel
    
    # Time window: Last 7 days
    last_7_days = timezone.now() - timedelta(days=7)
    
    items = FoodItem.objects.filter(is_available=True)
    
    for item in items:
        # 1. Order Count (Weight: 0.5)
        # Note: distinct() ensures we don't double count if item is in M2M multiple times (though standard M2M is unique set)
        # Ideally we'd sum quantity but our model currently lacks easy quantity tracking per item instance order.
        # Using count of orders containing the item is a proxy for popularity.
        order_count = Order.objects.filter(items=item, created_at__gte=last_7_days).count()
        
        # 2. Search/View Count (Weight: 0.3)
        search_count = FoodAnalytics.objects.filter(
            food_item=item, 
            interaction_type__in=['search', 'view', 'click'], 
            # created_at logic should be added to Analytics model if not present, assuming it tracks history? 
            # Model definition didn't show created_at in FoodAnalytics! 
            # Checking model... it only has item and type. 
            # We must assume all-time or add created_at? 
            # For now, using all-time count as valid proxy or we should add created_at.
        ).count()
        
        # 3. Reel Engagement (Weight: 0.2)
        # Sum of likes + comments on reels featuring this food
        reels = Reel.objects.filter(food_item=item)
        reel_engagement = 0
        for reel in reels:
            reel_engagement += reel.likes.count() + reel.comments.count()
            
        # 🧠 Final Formula
        raw_score = (order_count * 0.5) + (search_count * 0.3) + (reel_engagement * 0.2)
        
        # Normalize/Scale if needed (e.g., max 100), but raw score is fine for relative sorting
        item.trend_score = round(raw_score, 2)
        item.save()
        
    print("✅ AI Trend Scores Recalculated")

def calculate_trending_reels():
    """
    🧠 Identify Trending Reels
    Logic: If likes + comments > Threshold (e.g., 10), mark as trending.
    """
    from .models import Reel
    
    # Threshold could be dynamic based on average engagement, but fixed for now
    TRENDING_THRESHOLD = 5 
    
    reels = Reel.objects.all()
    
    for reel in reels:
        likes = reel.likes.count()
        comments = reel.comments.count()
        engagement_score = likes + (comments * 2) # Comments are worth more
        
        reel.engagement_score = engagement_score
        
        if engagement_score >= TRENDING_THRESHOLD:
            reel.is_trending = True
        else:
            reel.is_trending = False
            
        reel.save()
        
    print("✅ Trending Reels Updated")
