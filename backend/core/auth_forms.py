from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant'),
    ]
    COUNTRY_CHOICES = [
        ('India', 'India'),
        ('USA', 'USA'),
        ('UK', 'UK'),
        ('UAE', 'UAE'),
        ('Canada', 'Canada'),
    ]
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        initial='India'
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        initial='customer'
    )

    restaurant_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Restaurant Name'}))
    restaurant_location = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'City/Area'}))
    opening_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    closing_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    restaurant_image_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Image URL'}))
    maps_link = forms.URLField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Google Maps Link (for auto-location)'}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.role = self.cleaned_data['role']
        user.country = self.cleaned_data['country']
        
        # Set Currency based on Country
        currency_map = {
            'India': '₹',
            'USA': '$',
            'UK': '£',
            'UAE': 'AED',
            'Canada': 'C$',
        }
        user.currency_symbol = currency_map.get(user.country, '₹')

        if self.cleaned_data.get('restaurant_location'):
             user.current_location = self.cleaned_data['restaurant_location']
        user.save()

        if user.role == 'restaurant':
            from .models import Restaurant
            from .utils import extract_lat_long_from_url
            
            # Auto-detect coordinates
            lat, lng = None, None
            maps_link = self.cleaned_data.get('maps_link')
            if maps_link:
                lat, lng = extract_lat_long_from_url(maps_link)
            
            # Create Restaurant Profile
            Restaurant.objects.create(
                user=user,
                name=self.cleaned_data.get('restaurant_name') or f"{user.username}'s Kitchen",
                location=self.cleaned_data.get('restaurant_location') or 'Unknown',
                image_url=self.cleaned_data.get('restaurant_image_url'),
                opening_time=self.cleaned_data.get('opening_time'),
                closing_time=self.cleaned_data.get('closing_time'),
                cuisine_type='General', # Default
                is_open=True,
                latitude=lat,
                longitude=lng
            )
        return user
