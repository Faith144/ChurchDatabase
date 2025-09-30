from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import Admin   # import your Admin model

def role_required(*allowed_roles, redirect_to=None):
    """
    Decorator to restrict access to users with specific roles.
    Usage: @role_required("Cell") or @role_required("SUPERADMIN", "MODERATOR")
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")  # or HttpResponseForbidden("Not logged in.")

            try:
                admin_profile = Admin.objects.get(member=request.user)
            except Admin.DoesNotExist:
                return HttpResponseForbidden("No admin profile found.")

            if admin_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # either redirect or return 403
            if redirect_to:
                return redirect(redirect_to)
            return HttpResponseForbidden("You are not authorized to view this page.")
        return _wrapped_view
    return decorator
