import os
import sys
import django

sys.path.append('d:\\Mini project\\deliciae\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from core.models import Reel

# Valid sample video
SAMPLE_VIDEO = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4"

count = Reel.objects.count()
print(f"Updating {count} reels with valid sample video...")

Reel.objects.all().update(video_url=SAMPLE_VIDEO)

print("Done! All reels now point to a working video.")
