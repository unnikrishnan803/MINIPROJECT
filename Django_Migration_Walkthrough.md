# Migration to Full Django App

I have successfully converted your application into a fully integrated Django application. This ensures that both the frontend and backend are served by Django, making it ready for hosting on platforms like PythonAnywhere.

## Changes Made

### 1. Frontend Integration
- **Templates**: Moved `index.html`, `login.html`, `register.html`, and `dashboard.html` to be served as Django templates.
- **Static Files**: configured `settings.py` to serve CSS and JS files from the `frontend` directory using Django's static file system.
- **Tags**: Updated all HTML files to use `{% load static %}` for resources and `{% url 'name' %}` for navigation.

### 2. URL Routing
The URL structure has been updated to serve pages directly:
- `/` -> Index Page
- `/login/` -> Login Page
- `/register/` -> Register Page
- `/dashboard/` -> Dashboard Page
- `/api/` -> API Endpoints

### 3. Authentication
- **Hybrid Auth**: Kept Firebase for the Google/Email sign-in UI.
- **Backend Sync**: Added `FirebaseLoginView` and updated `auth.js` to automatically create a Django session after a successful Firebase login. This means `@login_required` decorators in Django will now work!

### 4. Configuration
- **CORS**: Configured to allow credentials (cookies) for local development.
- **CSRF**: Prepared for CSRF protection (though currently using basic session auth).

## How to Run
1. Start the Django server:
   ```bash
   cd backend
   python manage.py runserver
   ```
2. Open your browser to `http://127.0.0.1:8000/`.
3. You should see the Landing Page. Navigation to Login/Register should work seamlessly.

## Deployment to PythonAnywhere
Since this is now a WSGI application, you can deploy it easily:
1. Push code to GitHub.
2. Pull on PythonAnywhere.
3. Set up a Virtualenv.
4. Configure the WSGI file to point to `deliciae_core.wsgi`.
5. Set up Static Files mapping in the Web tab.
