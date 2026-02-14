import requests
import django
import os
import sys

# Setup Django environment
sys.path.append('d:\\Mini project\\deliciae\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Reel

reels = Reel.objects.all()
print(f"Found {reels.count()} reels.")

for reel in reels:
    url = reel.video_url
    print(f"Checking Reel {reel.id}: {url}")
    
    if url.startswith('http'):
        try:
            # use stream=True to avoid downloading the whole file, just check headers
            r = requests.head(url, allow_redirects=True, timeout=5)
            print(f"  Status: {r.status_code}")
            if r.status_code != 200:
                print(f"  Link broken!")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        # Local file
        if url.startswith('/media/'):
            # Check if file exists on disk
            path = url.replace('/media/', 'd:\\Mini project\\deliciae\\backend\\media\\')
            import os.path
            path = path.replace('/', '\\') # Fix slashes for windows
            exists = os.path.exists(path)
            print(f"  Local file path: {path}")
            print(f"  Exists: {exists}")
        else:
            print(f"  Unknown URL format: {url}")
