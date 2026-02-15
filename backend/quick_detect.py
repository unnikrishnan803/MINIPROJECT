import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.utils import extract_lat_long_from_url

url = "https://maps.app.goo.gl/XNJvbJkXpRa3ZWKw5"
print(f"Resolving URL: {url}")
lat, lng = extract_lat_long_from_url(url)
print(f"Latitude: {lat}")
print(f"Longitude: {lng}")
