def admin_context(request):
    """
    Add admin information to template context
    """
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'admin_account'):
        admin_profile = request.user.admin_account
        context.update({
            'current_admin': admin_profile,
            'admin_level': admin_profile.level,
            'is_superadmin': admin_profile.is_superadmin,
            'is_cell_admin': admin_profile.is_cell_admin,
            'is_moderator': admin_profile.is_moderator,
            'managed_members_count': admin_profile.get_managed_members().count(),
        })
    
    return context
