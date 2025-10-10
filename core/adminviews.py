from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Admin, Member, Assembly, Cell
from .adminforms import AdminForm, AdminLevelChangeForm, AdminFilterForm


class SuperAdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only super admins can access the view"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Check if user has admin account and is super admin
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(request, "Only super administrators can access this page.")
            return redirect("dashboard")

        return super().dispatch(request, *args, **kwargs)


class AdminListView(SuperAdminRequiredMixin, ListView):
    """List all admins in the system - Super Admin only"""

    model = Admin
    template_name = "admins/admin_list.html"
    context_object_name = "admins"
    paginate_by = 20

    def get_queryset(self):
        # Show all admins, not filtered by current user's assembly
        queryset = Admin.objects.all()

        # Apply filters
        level = self.request.GET.get("level")
        search = self.request.GET.get("search")
        cell_id = self.request.GET.get("cell")
        assembly_id = self.request.GET.get("assembly")

        if level:
            queryset = queryset.filter(level=level)
        if search:
            queryset = queryset.filter(
                Q(member__first_name__icontains=search)
                | Q(member__last_name__icontains=search)
                | Q(member__email__icontains=search)
                | Q(user_account__username__icontains=search)
            )
        if cell_id:
            queryset = queryset.filter(cell_id=cell_id)
        if assembly_id:
            queryset = queryset.filter(assembly_id=assembly_id)

        return queryset.select_related(
            "member", "assembly", "cell", "user_account"
        ).order_by("member__first_name", "member__last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AdminFilterForm(self.request.GET)
        context["total_count"] = self.get_queryset().count()
        context["assemblies"] = Assembly.objects.all()  # Add assemblies for filter
        return context


@login_required
def admin_create(request):
    """Create a new admin account - Super Admin only"""
    try:
        # Check if current user is super admin
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can create new admin accounts."
            )
            return redirect("dashboard")

        if request.method == "POST":
            form = AdminForm(request.POST, current_user=request.user)
            if form.is_valid():
                admin = form.save()
                messages.success(
                    request,
                    f"Admin account created successfully for {admin.get_full_name()}. "
                    f"Username: {admin.user_account.username}",
                )
                return redirect("admin_list")
        else:
            # Pre-fill assembly with current admin's assembly as default
            initial_data = {"assembly": request.user.admin_account.assembly}
            form = AdminForm(initial=initial_data, current_user=request.user)

        context = {
            "form": form,
            "title": "Create New Admin",
        }
        return render(request, "admins/admin_form.html", context)

    except Exception as e:
        messages.error(request, f"Error creating admin: {str(e)}")
        return redirect("admin_list")


@login_required
def admin_update(request, pk):
    """Update an existing admin account - Super Admin only"""
    try:
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can update admin accounts."
            )
            return redirect("dashboard")

        admin = get_object_or_404(Admin, pk=pk)

        if request.method == "POST":
            form = AdminForm(request.POST, instance=admin, current_user=request.user)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    f"Admin account updated successfully for {admin.get_full_name()}",
                )
                return redirect("admin_list")
        else:
            form = AdminForm(instance=admin, current_user=request.user)

        context = {
            "form": form,
            "admin": admin,
            "title": "Update Admin",
        }
        return render(request, "admins/admin_form.html", context)

    except Exception as e:
        messages.error(request, f"Error updating admin: {str(e)}")
        return redirect("admin_list")


@login_required
def admin_detail(request, pk):
    """View admin details"""
    admin = get_object_or_404(Admin, pk=pk)

    current_user_admin = getattr(request.user, "admin_account", None)
    if not current_user_admin or (
        current_user_admin != admin and not current_user_admin.is_superadmin
    ):
        messages.error(request, "You don't have permission to view this admin profile.")
        return redirect("dashboard")

    # Get managed members without invalid select_related
    managed_members = admin.get_managed_members()

    context = {
        "admin_profile": admin,
        "managed_members": managed_members[:10],
    }

    return render(request, "admins/admin_detail.html", context)


@login_required
def admin_change_level(request, pk):
    """Change admin level - Super Admin only"""
    try:
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can change admin levels."
            )
            return redirect("dashboard")

        admin = get_object_or_404(Admin, pk=pk)

        if request.method == "POST":
            form = AdminLevelChangeForm(request.POST, instance=admin)
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Admin level updated for {admin.get_full_name()}"
                )
                return redirect("admin_list")
        else:
            form = AdminLevelChangeForm(instance=admin)

        context = {
            "form": form,
            "admin": admin,
            "title": f"Change Level for {admin.get_full_name()}",
        }
        return render(request, "admins/admin_level_form.html", context)

    except Exception as e:
        messages.error(request, f"Error changing admin level: {str(e)}")
        return redirect("admin_list")


@login_required
def admin_delete(request, pk):
    """Delete an admin account - Super Admin only"""
    try:
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can delete admin accounts."
            )
            return redirect("dashboard")

        admin = get_object_or_404(Admin, pk=pk)

        if request.method == "POST":
            admin_name = admin.get_full_name()
            admin.delete()
            messages.success(
                request, f"Admin account for {admin_name} has been deleted."
            )
            return redirect("admin_list")

        context = {
            "admin": admin,
        }
        return render(request, "admins/admin_confirm_delete.html", context)

    except Exception as e:
        messages.error(request, f"Error deleting admin: {str(e)}")
        return redirect("admin_list")
