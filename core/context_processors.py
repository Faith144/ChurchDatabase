from .models import Member
def admin_context(request):
    """Add admin information to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        
        if hasattr(request.user, 'admin_account'):
            admin_profile = request.user.admin_account

            # Count members in the admin's cell if they are a cell admin
            if admin_profile.is_cell_admin:
                members_count = Member.objects.filter(cell=admin_profile.cell).count()
            
            context.update({
                'admin_profile': admin_profile,
                'is_superadmin': admin_profile.is_superadmin,
                'is_cell_admin': admin_profile.is_cell_admin,
                'is_moderator': admin_profile.is_moderator,
                'is_inventory_admin':admin_profile.is_inventory_admin,
                'has_cell_assignment': admin_profile.cell is not None,  # Add this
                'admin_cell_name': admin_profile.cell.name if admin_profile.cell else 'No Cell Assigned',
                'members_count': members_count if admin_profile.is_cell_admin else Member.objects.count(),
            })
        else:
            print(f"DEBUG: No admin_account found for user {request.user.username}")  # Debug line
    
    return context