import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Restaurant

def check_image():
    try:
        # 1. Try to find by name "Mehar" (case-insensitive)
        r = Restaurant.objects.filter(name__iexact="Mehar").first()
        
        if not r:
            print("Restaurant 'Mehar' not found.")
            # List all restaurants to see what exists
            print("Available restaurants:", list(Restaurant.objects.values_list('name', flat=True)))
            return

        print(f"Restaurant: {r.name}")
        print(f"ID: {r.id}")
        print(f"Image Field: {r.image}")
        print(f"Image URL Field: {r.image_url}")
        
        if r.image:
            print(f"Image Path: {r.image.path}")
            print(f"File Exists: {os.path.exists(r.image.path)}")
            print(f"Image URL (Computed): {r.image.url}")
        else:
            print("No image in 'image' field.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_image()
