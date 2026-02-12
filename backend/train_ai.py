import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import FoodItem, Restaurant, FoodAnalytics, User

def generate_mock_analytics():
    print("🤖 AI Module: Generating User Interaction Data...")
    
    # Create some interactions if they don't exist
    items = FoodItem.objects.all()
    if not items.exists():
        print("No food items found. Please run populate_db.py first.")
        return

    interaction_types = ['view', 'click', 'order']
    
    # Simulate 500 random interactions
    for _ in range(500):
        item = random.choice(items)
        action = random.choices(interaction_types, weights=[70, 20, 10], k=1)[0] # Orders are rarer
        
        FoodAnalytics.objects.create(
            food_item=item,
            interaction_type=action,
            timestamp=timezone.now() - timedelta(minutes=random.randint(1, 1440)) # Last 24h
        )
    
    print(f"✅ Generated {FoodAnalytics.objects.count()} interaction records.")

def train_models():
    print("\n🧠 AI Training: Calculating Trend Scores...")
    
    items = FoodItem.objects.all()
    
    # Weights for our algorithm
    WEIGHTS = {
        'view': 0.5,
        'click': 1.0,
        'order': 5.0
    }
    
    updated_count = 0
    
    for item in items:
        # Fetch analytics for this item
        interactions = FoodAnalytics.objects.filter(food_item=item)
        
        if not interactions.exists():
            continue
            
        score = 0
        for interaction in interactions:
            score += WEIGHTS.get(interaction.interaction_type, 0)
        
        # Update Item
        old_score = item.trend_score
        item.trend_score = round(score, 2)
        item.save()
        
        updated_count += 1
        # print(f"  > {item.name}: Score updated {old_score} -> {item.trend_score}")

    print(f"✅ Training Complete. Updated Trend Scores for {updated_count} items.\n")

def show_results():
    print("📊 TOP 5 TRENDING FOODS:")
    print("-" * 30)
    top_foods = FoodItem.objects.order_by('-trend_score')[:5]
    for i, food in enumerate(top_foods, 1):
        print(f"{i}. {food.name} ({food.restaurant.name}) - Score: {food.trend_score}")
    
    print("\n🏆 TOP TRENDING RESTAURANTS (Avg Food Score):")
    print("-" * 30)
    restaurants = Restaurant.objects.all()
    res_scores = []
    
    for res in restaurants:
        avg_score = 0
        menu_items = res.menu_items.all()
        if menu_items.exists():
            total = sum(item.trend_score for item in menu_items)
            avg_score = total / menu_items.count()
        
        res_scores.append((res.name, avg_score))
        
    # Sort by avg score
    res_scores.sort(key=lambda x: x[1], reverse=True)
    
    for i, (name, score) in enumerate(res_scores[:3], 1):
        print(f"{i}. {name} - Avg Score: {round(score, 2)}")

if __name__ == '__main__':
    generate_mock_analytics()
    train_models()
    show_results()
