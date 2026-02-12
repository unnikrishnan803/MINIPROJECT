import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

apps = SocialApp.objects.filter(provider='google')
if apps.exists():
    for app in apps:
        print(f"Found Google App: Name='{app.name}', Client ID='{app.client_id}'")
else:
    print("No Google SocialApp found.")
