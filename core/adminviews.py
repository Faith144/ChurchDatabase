from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Admin, Member, Assembly, Cell
from .adminforms import (
    SuperAdminCreationForm,
    SuperAdminUpdateForm,
    AdminLevelChangeForm,
    AdminFilterForm,
)


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


# Dashboard and Overview Views
@login_required
def admin_dashboard(request):
    """Dashboard for admins - shows different content based on admin level"""
    try:
        admin_profile = request.user.admin_account

        context = {
            "admin": admin_profile,
        }

        # Different context based on admin level
        if admin_profile.is_superadmin:
            context.update(
                {
                    "total_admins": Admin.objects.filter(
                        assembly=admin_profile.assembly
                    ).count(),
                    "total_members": Member.objects.filter(
                        assembly=admin_profile.assembly
                    ).count(),
                    "recent_admins": Admin.objects.filter(
                        assembly=admin_profile.assembly
                    ).order_by("-id")[:5],
                }
            )
        elif admin_profile.is_cell_admin:
            context.update(
                {
                    "managed_members": admin_profile.get_managed_members().count(),
                    "cell": admin_profile.cell,
                }
            )
        elif admin_profile.is_moderator:
            context.update(
                {
                    "total_members": Member.objects.filter(
                        assembly=admin_profile.assembly
                    ).count(),
                }
            )

        return render(request, "admins/dashboard.html", context)

    except Admin.DoesNotExist:
        messages.error(request, "Admin profile not found.")
        return redirect("home")


# Admin Management Views
class AdminListView(SuperAdminRequiredMixin, ListView):
    """List all admins in the system - Super Admin only"""

    model = Admin
    template_name = "admins/admin_list.html"
    context_object_name = "admins"
    paginate_by = 20

    def get_queryset(self):
        queryset = Admin.objects.select_related(
            "member", "assembly", "cell", "user_account"
        ).filter(assembly=self.request.user.admin_account.assembly)

        # Apply filters
        level = self.request.GET.get("level")
        search = self.request.GET.get("search")
        cell_id = self.request.GET.get("cell")

        if level:
            queryset = queryset.filter(level=level)
        if search:
            queryset = queryset.filter(
                Q(member__first_name__icontains=search)
                | Q(member__last_name__icontains=search)
                | Q(member__email__icontains=search)
            )
        if cell_id:
            queryset = queryset.filter(cell_id=cell_id)

        return queryset.order_by("member__first_name", "member__last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AdminFilterForm(self.request.GET)
        context["total_count"] = self.get_queryset().count()
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
            return redirect("admin_dashboard")

        if request.method == "POST":
            form = SuperAdminCreationForm(request.POST, current_user=request.user)
            if form.is_valid():
                admin = form.save()

                # Log the action
                messages.success(
                    request,
                    f"Admin account created successfully for {admin.get_full_name()}. "
                    f"Username: {admin.user_account.username}",
                )

                # Optional: Send credentials via email (you can implement this)
                # send_admin_credentials(admin, request)

                return redirect("admin_list")
        else:
            # Pre-fill assembly with current admin's assembly
            initial_data = {"assembly": request.user.admin_account.assembly}
            form = SuperAdminCreationForm(
                initial=initial_data, current_user=request.user
            )

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
        # Check if current user is super admin
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can update admin accounts."
            )
            return redirect("admin_dashboard")

        admin = get_object_or_404(
            Admin.objects.select_related("member", "assembly", "cell", "user_account"),
            pk=pk,
            assembly=request.user.admin_account.assembly,  # Only admins from same assembly
        )

        if request.method == "POST":
            form = SuperAdminUpdateForm(
                request.POST, instance=admin, current_user=request.user
            )
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    f"Admin account updated successfully for {admin.get_full_name()}",
                )
                return redirect("admin_list")
        else:
            form = SuperAdminUpdateForm(instance=admin, current_user=request.user)

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
    admin = get_object_or_404(
        Admin.objects.select_related("member", "assembly", "cell", "user_account"),
        pk=pk,
    )

    # Check permissions - users can view their own profile or super admins can view any
    current_user_admin = getattr(request.user, "admin_account", None)
    if not current_user_admin or (
        current_user_admin != admin and not current_user_admin.is_superadmin
    ):
        messages.error(request, "You don't have permission to view this admin profile.")
        return redirect("admin_dashboard")

    context = {
        "admin_profile": admin,
        "managed_members": admin.get_managed_members().select_related("cell")[
            :10
        ],  # Recent members
    }

    return render(request, "admins/admin_detail.html", context)


@login_required
def admin_change_level(request, pk):
    """Change admin level - Super Admin only"""
    try:
        # Check if current user is super admin
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can change admin levels."
            )
            return redirect("admin_dashboard")

        admin = get_object_or_404(
            Admin.objects.select_related("member", "assembly", "cell"),
            pk=pk,
            assembly=request.user.admin_account.assembly,
        )

        if request.method == "POST":
            form = AdminLevelChangeForm(
                request.POST, instance=admin, current_user=request.user
            )
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"Admin level updated for {admin.get_full_name()}"
                )
                return redirect("admin_list")
        else:
            form = AdminLevelChangeForm(instance=admin, current_user=request.user)

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
        # Check if current user is super admin
        if (
            not hasattr(request.user, "admin_account")
            or not request.user.admin_account.is_superadmin
        ):
            messages.error(
                request, "Only super administrators can delete admin accounts."
            )
            return redirect("admin_dashboard")

        admin = get_object_or_404(
            Admin.objects.select_related("member"),
            pk=pk,
            assembly=request.user.admin_account.assembly,
        )

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
