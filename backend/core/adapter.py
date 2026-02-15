from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Call the parent class to do the standard save
        user = super().save_user(request, user, form, commit=False)
        
        # Extract role from request data (works for both JSON and Form handling)
        data = request.POST if request.POST else request.data
        role = data.get('role')
        
        if role in ['customer', 'restaurant']:
            user.role = role
        else:
            # Default to customer if not specified or invalid (safety net)
            user.role = 'customer'

        if commit:
            user.save()
            
        return user

    def get_login_redirect_url(self, request):
        """
        Redirect users based on their role after login.
        """
        user = request.user
        
        # 1. Admin / Superuser
        if user.is_superuser:
            return '/admin/'
            
        # 2. Restaurant
        if user.role == 'restaurant':
            return '/dashboard/'
            
        # 3. Staff (Restaurant specific)
        if user.role == 'staff':
            return '/dashboard/?view=tables'
            
        # 4. Customer (Default)
        return '/home/'
