from django.utils import timezone
from .models import ActivityLog

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.method != "GET":
            action = request.method  # Get the HTTP method (POST, etc.)
            details = ""  # Initialize details

            # Check for specific actions and capture relevant details
            if action == "POST":
                # Filter out sensitive data such as CSRF token and passwords
                filtered_post_data = request.POST.copy()
                if 'csrfmiddlewaretoken' in filtered_post_data:
                    del filtered_post_data['csrfmiddlewaretoken']
                for sensitive_field in ['password', 'password1', 'password2']:
                    if sensitive_field in filtered_post_data:
                        filtered_post_data[sensitive_field] = '*****'  # Replace password with asterisks
                details = str(filtered_post_data)


            
            # Log user activity with details including path, specific action, and status
            log_details = (f"Path: {request.path} , Action: {details} " 
                           if details else f"Path: {request.path}, Action: No data")
            
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                details=log_details
            )
            
        return response
