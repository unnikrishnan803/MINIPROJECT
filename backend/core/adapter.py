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
