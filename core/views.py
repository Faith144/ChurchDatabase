from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Assembly, Unit, Member, Cell, Admin
from .forms import MemberForm, AssemblyForm, UnitForm, CellForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        admin_profile = request.user.admin_account
        if admin_profile.is_superadmin:
            return render(request, "home.html")
        if admin_profile.is_cell_admin:
            return redirect("member_list")
    return redirect("login")


@login_required
def dashboard(request):
    """Main dashboard with overview and all functionality"""
    try:
        # Statistics
        total_members = Member.objects.count()
        # total_families = Family.objects.count()
        total_assemblies = Assembly.objects.count()
        total_units = Unit.objects.count()
        total_cells = Cell.objects.count()

        # Get active members count
        active_members = Member.objects.filter(membership_status="ACTIVE").count()

        # New members today
        new_members_today = Member.objects.filter(
            created_at__date=timezone.now().date()
        ).count()

        # Month Mapping
        MONTH_MAP = [
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ]

        # Recent activities
        recent_members = Member.objects.select_related(
            "assembly", "unit", "cell"
        ).order_by("-created_at")[:10]
        # recent_families = Family.objects.select_related('assembly').order_by('-created_at')[:5]

        # Get all filter parameters for member list
        assembly_filter = request.GET.get("assembly", "")
        unit_filter = request.GET.get("unit", "")
        family_filter = request.GET.get("family", "")
        cell_filter = request.GET.get("cell", "")
        status_filter = request.GET.get("status", "")
        month_filter = request.GET.get("month", "")

        # Filter members based on parameters
        admin_profile = request.user.admin_account
        if admin_profile.is_superadmin:
            members = (
                Member.objects.all()
                .select_related("assembly", "unit", "cell")
                .order_by("first_name", "last_name")
            )
        if admin_profile.is_cell_admin:
            members = Member.objects.filter(cell=admin_profile.cell).order_by(
                "first_name", "last_name"
            )

        if assembly_filter:
            members = members.filter(assembly_id=assembly_filter)
        if unit_filter:
            members = members.filter(unit_id=unit_filter)
        if family_filter:
            members = members.filter(family_id=family_filter)
        if cell_filter:
            members = members.filter(cell_id=cell_filter)
        if status_filter:
            members = members.filter(membership_status=status_filter)
        if month_filter:
            month_of_birth = members.get_month_of_birth()
            members = members.filter(month_of_birth=month_filter)

        # Get all options for filters
        assemblies = Assembly.objects.all()
        units = Unit.objects.all()
        # families = Family.objects.all()
        cells = Cell.objects.all()

        context = {
            # Statistics
            "total_members": total_members,
            # 'total_families': total_families,
            "total_assemblies": total_assemblies,
            "total_units": total_units,
            "total_cells": total_cells,
            "active_members": active_members,
            "new_members_today": new_members_today,
            # Month mapp
            "month_map": MONTH_MAP,
            # Recent data
            "recent_members": recent_members,
            # 'recent_families': recent_families,
            # Filtered members
            "members": members,
            # Filter options
            "assemblies": assemblies,
            "units": units,
            # 'families': families,
            "cells": cells,
            # Selected filters
            "selected_assembly": assembly_filter,
            "selected_unit": unit_filter,
            "selected_family": family_filter,
            "selected_cell": cell_filter,
            "selected_status": status_filter,
        }

        return render(request, "dashboard/dashboard.html", context)

    except Exception as e:
        # Return a simple error page for debugging
        return JsonResponse({"error": str(e)}, status=500)


def ajax_search(request):
    """AJAX search for members, families, assemblies, units, and cells"""
    try:
        query = request.GET.get("q", "").strip()
        results = {}

        if query:
            # Search members
            members = Member.objects.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(middle_name__icontains=query)
                | Q(email__icontains=query)
                | Q(phone__icontains=query)
            ).select_related("assembly", "unit", "cell")[:10]

            # Search families
            # families = Family.objects.filter(
            #     Q(family_name__icontains=query) |
            #     Q(email__icontains=query) |
            #     Q(phone__icontains=query)
            # ).select_related('assembly')[:10]

            # Search assemblies
            assemblies = Assembly.objects.filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)
                | Q(state__icontains=query)
            )[:10]

            # Search units
            units = Unit.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).select_related("leader")[:10]

            # Search cells
            cells = Cell.objects.filter(name__icontains=query)[:10]

            results = {
                "members": [
                    {
                        "id": member.id,
                        "name": f"{member.first_name} {member.last_name}",
                        "type": "Member",
                        "email": member.email,
                        "phone": member.phone,
                        "assembly": member.assembly.name if member.assembly else "",
                        "url": f"/dashboard/members/{member.id}/",
                    }
                    for member in members
                ],
                # 'families': [
                #     {
                #         'id': family.id,
                #         'name': family.family_name,
                #         'type': 'Family',
                #         'email': family.email,
                #         'phone': family.phone,
                #         'assembly': family.assembly.name if family.assembly else '',
                #     }
                #     for family in families
                # ],
                "assemblies": [
                    {
                        "id": assembly.id,
                        "name": assembly.name,
                        "type": "Assembly",
                        "city": assembly.city,
                        "state": assembly.state,
                    }
                    for assembly in assemblies
                ],
                "units": [
                    {
                        "id": unit.id,
                        "name": unit.name,
                        "type": "Unit",
                        "description": (
                            unit.description[:100] + "..."
                            if unit.description and len(unit.description) > 100
                            else unit.description
                        ),
                    }
                    for unit in units
                ],
                "cells": [
                    {
                        "id": cell.id,
                        "name": cell.name,
                        "type": "Cell",
                        "created_at": (
                            cell.created_at.strftime("%Y-%m-%d")
                            if cell.created_at
                            else ""
                        ),
                    }
                    for cell in cells
                ],
            }

        return JsonResponse(results)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def quick_stats(request):
    """AJAX endpoint for quick statistics"""
    try:
        total_members = Member.objects.count()
        active_members = Member.objects.filter(membership_status="ACTIVE").count()
        new_members_today = Member.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        # total_families = Family.objects.count()

        return JsonResponse(
            {
                "total_members": total_members,
                "active_members": active_members,
                "new_members_today": new_members_today,
                # 'total_families': total_families,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Member AJAX Views
def member_detail_modal(request, pk):
    """Return member details for modal display"""
    try:
        member = get_object_or_404(
            Member.objects.select_related("assembly", "unit", "cell"), pk=pk
        )

        html = render_to_string(
            "dashboard/partials/member_detail_modal.html", {"member": member}
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_member_form(request, pk=None):
    """Return member form for modal (both create and update)"""
    try:
        if pk:
            member = get_object_or_404(Member, pk=pk)
            form = MemberForm(instance=member)
            title = f"Edit Member: {member.first_name} {member.last_name}"
        else:
            form = MemberForm()
            title = "Add New Member"

        # Filter cell field for cell admins using admin_account
        if hasattr(request.user, "admin_account"):
            admin_account = request.user.admin_account
            if (
                hasattr(admin_account, "is_cell_admin")
                and admin_account.is_cell_admin
                and hasattr(admin_account, "cell")
                and admin_account.cell
            ):
                form.fields["cell"].queryset = Cell.objects.filter(
                    id=admin_account.cell.id
                )
                form.fields["cell"].empty_label = None
                if not pk:  # For new members, set initial value
                    form.fields["cell"].initial = admin_account.cell

        admin_profile = request.user.admin_account
        html = render_to_string(
            "dashboard/partials/member_form_modal.html",
            {"form": form, "title": title, "member_id": pk, "user": admin_profile},
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def create_member(request):
    """Create new member from dashboard"""
    try:
        if request.method == "POST":
            form = MemberForm(request.POST, request.FILES)

            if form.is_valid():
                member = form.save(commit=False)

                # Auto-assign cell for cell admins using admin_account
                if hasattr(request.user, "admin_account"):
                    admin_account = request.user.admin_account
                    if (
                        hasattr(admin_account, "is_cell_admin")
                        and admin_account.is_cell_admin
                        and hasattr(admin_account, "cell")
                        and admin_account.cell
                    ):
                        member.cell = admin_account.cell

                member.save()

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Member {member.first_name} {member.last_name} created successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def update_member(request, pk):
    """Update member from dashboard"""
    try:
        member = get_object_or_404(Member, pk=pk)

        if request.method == "POST":
            form = MemberForm(request.POST, request.FILES, instance=member)
            if form.is_valid():
                member = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Member {member.first_name} {member.last_name} updated successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def delete_member(request, pk):
    """Delete member from dashboard"""
    try:
        member = get_object_or_404(Member, pk=pk)

        if request.method == "POST":
            member_name = f"{member.first_name} {member.last_name}"
            member.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Member {member_name} deleted successfully!",
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# # Family AJAX Views
# def family_detail_modal(request, pk):
#     """Return family details for modal display"""
#     # try:
#     #     family = get_object_or_404(Family.objects.select_related('assembly'), pk=pk)
#     #     family_members = Member.objects.filter(family=family).select_related('unit', 'cell')

#     #     html = render_to_string('dashboard/partials/family_detail_modal.html', {
#     #         'family': family,
#     #         'family_members': family_members,
#     #     })
#     #     return JsonResponse({'html': html})
#     # except Exception as e:
#     #     return JsonResponse({'error': str(e)}, status=500)

# def get_family_form(request, pk=None):
#     """Return family form for modal (both create and update)"""
#     try:
#         if pk:
#             family = get_object_or_404(Family, pk=pk)
#             form = FamilyForm(instance=family)
#             title = f'Edit Family: {family.family_name}'
#         else:
#             form = FamilyForm()
#             title = 'Add New Family'

#         html = render_to_string('dashboard/partials/family_form_modal.html', {
#             'form': form,
#             'title': title,
#             'family_id': pk
#         })
#         return JsonResponse({'html': html})
#     except Exception as e:
#         print(e)
#         return JsonResponse({'error': str(e)}, status=500)

# @csrf_exempt
# def create_family(request):
#     """Create new family from dashboard"""
#     try:
#         if request.method == 'POST':
#             form = FamilyForm(request.POST)
#             if form.is_valid():
#                 family = form.save()
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Family {family.family_name} created successfully!'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'errors': form.errors.as_json()
#                 }, status=400)
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Only POST method allowed'
#             }, status=405)

#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=500)

# @csrf_exempt
# def update_family(request, pk):
#     """Update family from dashboard"""
#     try:
#         family = get_object_or_404(Family, pk=pk)

#         if request.method == 'POST':
#             form = FamilyForm(request.POST, instance=family)
#             if form.is_valid():
#                 family = form.save()
#                 return JsonResponse({
#                     'success': True,
#                     'message': f'Family {family.family_name} updated successfully!'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'errors': form.errors.as_json()
#                 }, status=400)
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Only POST method allowed'
#             }, status=405)

#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=500)

# @csrf_exempt
# def delete_family(request, pk):
#     """Delete family from dashboard"""
#     try:
#         family = get_object_or_404(Family, pk=pk)

#         if request.method == 'POST':
#             family_name = family.family_name
#             family.delete()
#             return JsonResponse({
#                 'success': True,
#                 'message': f'Family {family_name} deleted successfully!'
#             })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Only POST method allowed'
#             }, status=405)

#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=500)


# Cell AJAX Views
def get_cell_form(request, pk=None):
    """Return cell form for modal (both create and update)"""
    try:
        if pk:
            cell = get_object_or_404(Cell, pk=pk)
            form = CellForm(instance=cell)
            title = f"Edit Cell: {cell.name}"
        else:
            form = CellForm()
            title = "Add New Cell"

        html = render_to_string(
            "dashboard/partials/cell_form_modal.html",
            {"form": form, "title": title, "cell_id": pk},
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def create_cell(request):
    """Create new cell from dashboard"""
    try:
        if request.method == "POST":
            form = CellForm(request.POST)
            if form.is_valid():
                cell = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Cell {cell.name} created successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def update_cell(request, pk):
    """Update cell from dashboard"""
    try:
        cell = get_object_or_404(Cell, pk=pk)

        if request.method == "POST":
            form = CellForm(request.POST, instance=cell)
            if form.is_valid():
                cell = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Cell {cell.name} updated successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def delete_cell(request, pk):
    """Delete cell from dashboard"""
    try:
        cell = get_object_or_404(Cell, pk=pk)

        if request.method == "POST":
            cell_name = cell.name
            cell.delete()
            return JsonResponse(
                {"success": True, "message": f"Cell {cell_name} deleted successfully!"}
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# Assembly AJAX Views
def get_assembly_form(request, pk=None):
    """Return assembly form for modal (both create and update)"""
    try:
        if pk:
            assembly = get_object_or_404(Assembly, pk=pk)
            form = AssemblyForm(instance=assembly)
            title = f"Edit Assembly: {assembly.name}"
        else:
            form = AssemblyForm()
            title = "Add New Assembly"

        html = render_to_string(
            "dashboard/partials/assembly_form_modal.html",
            {"form": form, "title": title, "assembly_id": pk},
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def create_assembly(request):
    """Create new assembly from dashboard"""
    try:
        if request.method == "POST":
            form = AssemblyForm(request.POST)
            if form.is_valid():
                assembly = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Assembly {assembly.name} created successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def update_assembly(request, pk):
    """Update assembly from dashboard"""
    try:
        assembly = get_object_or_404(Assembly, pk=pk)

        if request.method == "POST":
            form = AssemblyForm(request.POST, instance=assembly)
            if form.is_valid():
                assembly = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Assembly {assembly.name} updated successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def delete_assembly(request, pk):
    """Delete assembly from dashboard"""
    try:
        assembly = get_object_or_404(Assembly, pk=pk)

        if request.method == "POST":
            assembly_name = assembly.name
            assembly.delete()
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Assembly {assembly_name} deleted successfully!",
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# Public Views
def public_registration(request):
    """Public registration form for new members"""
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            # Set default values for public registrations
            member.membership_status = "NEW_MEMBER"
            member.save()

            messages.success(
                request,
                "Thank you for registering! Your information has been submitted for review.",
            )
            return redirect("registration_success")
    else:
        form = MemberForm()

    context = {"form": form, "title": "Member Registration"}
    return render(request, "public/registration.html", context)


def registration_success(request):
    """Registration success page"""
    return render(request, "public/registration_success.html")


def login_view(request):
    """Custom login view for the church management system"""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        admin_profile = request.user.admin_account
        if admin_profile.is_superadmin:
            return redirect("dashboard")
        if admin_profile.is_cell_admin:
            return redirect("member_list")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")

                # Redirect to next page if it exists, otherwise to dashboard
                next_page = request.GET.get("next")
                if next_page:
                    return redirect(next_page)
                admin_profile = request.user.admin_account
                if admin_profile.is_superadmin:
                    return redirect("home")
                if admin_profile.is_inventory_admin:
                    return redirect("inventory_dashboard")
                if admin_profile.is_cell_admin:
                    return redirect("member_list")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    context = {"form": form, "title": "Login - Church Management System"}
    return render(request, "auth/login.html", context)


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("login")


def member_list(request):
    """List all members with filtering and pagination"""

    MONTH_MAP = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    admin_profile = request.user.admin_account
    if admin_profile.is_superadmin:
        members = (
            Member.objects.all()
            .select_related("assembly", "unit", "cell")
            .order_by("first_name", "last_name")
        )
    if admin_profile.is_cell_admin:
        members = Member.objects.filter(cell=admin_profile.cell).order_by(
            "first_name", "last_name"
        )

    # Filtering
    assembly_id = request.GET.get("assembly")
    unit_id = request.GET.get("unit")
    gender = request.GET.get("gender")
    cell_id = request.GET.get("cell")
    status = request.GET.get("status")
    search = request.GET.get("search")
    month = request.GET.get("month")

    if assembly_id:
        members = members.filter(assembly_id=assembly_id)
    if unit_id:
        if unit_id == "None":
            members = members.filter(unit__isnull=True)
        else:
            members = members.filter(unit_id=unit_id)

    if gender:
        if gender == "all":
            pass
        else:
            members = members.filter(gender=gender)

    if cell_id and admin_profile.is_superadmin:
        if cell_id == "None":
            members = members.filter(cell__isnull=True)
            print(cell_id)
        else:
            members = members.filter(cell_id=cell_id)
    if status:
        members = members.filter(membership_status=status)
    if search:
        members = members.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )
    if month:
        members = members.filter(date_of_birth__month=month).order_by(
            "date_of_birth__day"
        )

    # Pagination
    page_size = int(request.GET.get("page_size", 25))
    paginator = Paginator(members, page_size)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "members": page_obj,
        "assemblies": Assembly.objects.all(),
        "month_map": MONTH_MAP,
        "units": Unit.objects.all(),
        "cells": Cell.objects.all(),
    }
    return render(request, "members/member_list.html", context)


# def family_list(request):
#     """List all families with statistics"""
#     families = Family.objects.annotate(
#         member_count=Count('member'),
#         active_members=Count('member', filter=Q(member__membership_status='ACTIVE')),
#         male_count=Count('member', filter=Q(member__gender='M')),
#         female_count=Count('member', filter=Q(member__gender='F'))
#     ).select_related('assembly')

#     # Filtering
#     assembly_id = request.GET.get('assembly')
#     search = request.GET.get('search')
#     sort = request.GET.get('sort', 'family_name')

#     if assembly_id:
#         families = families.filter(assembly_id=assembly_id)
#     if search:
#         families = families.filter(family_name__icontains=search)

#     families = families.order_by(sort)

#     # Statistics
#     total_families = families.count()
#     total_members = sum(family.member_count for family in families)
#     average_members = total_members / total_families if total_families > 0 else 0
#     families_without_members = families.filter(member_count=0).count()

#     # Pagination
#     paginator = Paginator(families, 12)  # 12 per page for grid view
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'families': page_obj,
#         'assemblies': Assembly.objects.all(),
#         'total_families': total_families,
#         'total_members': total_members,
#         'average_members': average_members,
#         'families_without_members': families_without_members,
#     }
#     return render(request, 'families/family_list.html', context)


def unit_list(request):
    """List all units"""
    units = Unit.objects.annotate(member_count=Count("members")).select_related(
        "leader"
    )
    context = {"units": units}
    return render(request, "units/unit_list.html", context)


def cell_list(request):
    """List all cells"""
    cells = Cell.objects.annotate(member_count=Count("member")).order_by("name")
    context = {"cells": cells}
    return render(request, "cells/cell_list.html", context)


def assembly_list(request):
    """List all assemblies"""
    assemblies = Assembly.objects.annotate(member_count=Count("members"))

    # Filter active assemblies
    active_only = request.GET.get("active")
    if active_only:
        assemblies = assemblies.filter(is_active=True)

    # Statistics
    total_assemblies = assemblies.count()
    active_assemblies = assemblies.filter(is_active=True).count()
    total_members = Member.objects.all().count()
    total_cell = Cell.objects.all().count()
    # total_families = sum(assembly.family_count for assembly in assemblies)

    context = {
        "assemblies": assemblies,
        "total_assemblies": total_assemblies,
        "active_assemblies": active_assemblies,
        "total_members": total_members,
        "total_cell": total_cell,
        # 'total_families': total_families,
    }
    return render(request, "assemblies/assembly_list.html", context)


def member_detail(request, pk):
    """Member detail page"""
    member = get_object_or_404(
        Member.objects.select_related("assembly", "unit", "cell"), pk=pk
    )
    context = {"member": member}
    return render(request, "members/member_detail.html", context)


# def family_detail(request, pk):
#     """Family detail page"""
#     family = get_object_or_404(Family.objects.select_related('assembly'), pk=pk)
#     family_members = Member.objects.filter(family=family).select_related('unit', 'cell')
#     context = {
#         'family': family,
#         'family_members': family_members
#     }
#     return render(request, 'families/family_detail.html', context)


def unit_detail(request, pk):
    """Unit detail page"""
    unit = get_object_or_404(Unit.objects.select_related("leader"), pk=pk)
    unit_members = Member.objects.filter(unit=unit).select_related("assembly", "cell")
    context = {"unit": unit, "unit_members": unit_members}
    return render(request, "units/unit_detail.html", context)


def cell_detail(request, pk):
    """Cell detail page"""
    cell = get_object_or_404(Cell, pk=pk)
    cell_members = Member.objects.filter(cell=cell).select_related("assembly", "unit")
    context = {"cell": cell, "cell_members": cell_members}
    return render(request, "cells/cell_detail.html", context)


def assembly_detail(request, pk):
    """Assembly detail page"""
    assembly = get_object_or_404(Assembly, pk=pk)
    assembly_members = Member.objects.filter(assembly=assembly).select_related(
        "unit", "cell"
    )
    # assembly_families = Family.objects.filter(assembly=assembly)
    context = {
        "assembly": assembly,
        "assembly_members": assembly_members,
        # 'assembly_families': assembly_families
    }
    return render(request, "assemblies/assembly_detail.html", context)


# Unit AJAX Views
def get_unit_form(request, pk=None):
    """Return unit form for modal"""
    try:
        if pk:
            unit = get_object_or_404(Unit, pk=pk)
            form = UnitForm(instance=unit)
            title = f"Edit Unit: {unit.name}"
        else:
            form = UnitForm()
            title = "Add New Unit"

        html = render_to_string(
            "dashboard/partials/unit_form_modal.html",
            {"form": form, "title": title, "unit_id": pk},
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def create_unit(request):
    """Create new unit"""
    try:
        if request.method == "POST":
            form = UnitForm(request.POST)
            if form.is_valid():
                unit = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Unit {unit.name} created successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def update_unit(request, pk):
    """Update unit"""
    try:
        unit = get_object_or_404(Unit, pk=pk)
        if request.method == "POST":
            form = UnitForm(request.POST, instance=unit)
            if form.is_valid():
                unit = form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Unit {unit.name} updated successfully!",
                    }
                )
            else:
                return JsonResponse(
                    {"success": False, "errors": form.errors.as_json()}, status=400
                )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def delete_unit(request, pk):
    """Delete unit"""
    try:
        unit = get_object_or_404(Unit, pk=pk)
        if request.method == "POST":
            unit_name = unit.name
            unit.delete()
            return JsonResponse(
                {"success": True, "message": f"Unit {unit_name} deleted successfully!"}
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Only POST method allowed"}, status=405
            )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def unit_detail_modal(request, pk):
    """Return unit details for modal"""
    try:
        unit = get_object_or_404(Unit.objects.select_related("leader"), pk=pk)
        unit_members = Member.objects.filter(unit=unit).select_related(
            "assembly", "cell"
        )

        html = render_to_string(
            "dashboard/partials/unit_detail_modal.html",
            {
                "unit": unit,
                "unit_members": unit_members,
            },
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def cell_detail_modal(request, pk):
    """Return cell details for modal"""
    try:
        cell = get_object_or_404(Cell, pk=pk)
        cell_members = Member.objects.filter(cell=cell).select_related(
            "assembly", "unit"
        )

        html = render_to_string(
            "dashboard/partials/cell_detail_modal.html",
            {
                "cell": cell,
                "cell_members": cell_members,
            },
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def assembly_detail_modal(request, pk):
    """Return assembly details for modal"""
    try:
        assembly = get_object_or_404(Assembly, pk=pk)
        assembly_members = (
            Member.objects.filter(assembly=assembly)
            .select_related("unit", "cell")
            .order_by("last_name")
        )
        # assembly_families = Family.objects.filter(assembly=assembly)

        html = render_to_string(
            "dashboard/partials/assembly_detail_modal.html",
            {
                "assembly": assembly,
                "assembly_members": assembly_members,
                # 'assembly_families': assembly_families,
            },
        )
        return JsonResponse({"html": html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
