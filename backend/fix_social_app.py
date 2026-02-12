
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliciae_core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def fix_auth_config():
    print("🔧 Fixing AllAuth Configuration...")
    
    # 1. Fix Site (ID=1)
    try:
        site = Site.objects.get(id=1)
        site.domain = '127.0.0.1:8000'
        site.name = 'Deliciae Local'
        site.save()
        print("✅ Updated Site (ID=1)")
    except Site.DoesNotExist:
        Site.objects.create(id=1, domain='127.0.0.1:8000', name='Deliciae Local')
        print("✅ Created Site (ID=1)")

    # 2. Fix SocialApp (Google)
    # Even if we don't have real creds, we need a record to prevent 500 errors
    client_id = os.environ.get('GOOGLE_CLIENT_ID', 'dummy_client_id_placeholder')
    secret = os.environ.get('GOOGLE_SECRET', 'dummy_secret_placeholder')
    
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google Login',
            'client_id': client_id,
            'secret': secret,
        }
    )
    if created:
        print("✅ Created Dummy Google SocialApp")
    else:
        print("ℹ️ Google SocialApp already exists")
    
    # Link App to Site
    if not app.sites.filter(id=1).exists():
        app.sites.add(1)
        print("✅ Linked SocialApp to Site")

    print("🎉 Configuration Repaired. Login page should work now.")

if __name__ == "__main__":
    fix_auth_config()
