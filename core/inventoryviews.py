from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db import models
from .models import Inventory, Assembly
from .forms import InventoryForm


@login_required
def inventory_list(request):
    """
    Display all inventory items with search and filtering capabilities
    """
    inventory_items = Inventory.objects.select_related("assembly", "added_by").all()

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        inventory_items = inventory_items.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(Brand__icontains=search_query)
            | Q(Model__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(assembly__name__icontains=search_query)
            | Q(acquired_from__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get("status", "")
    if status_filter:
        inventory_items = inventory_items.filter(status=status_filter)

    # Filter by condition
    condition_filter = request.GET.get("condition", "")
    if condition_filter:
        inventory_items = inventory_items.filter(condition=condition_filter)

    # Filter by assembly
    assembly_filter = request.GET.get("assembly", "")
    if assembly_filter:
        inventory_items = inventory_items.filter(assembly_id=assembly_filter)

    # Ordering
    order_by = request.GET.get("order_by", "name")
    if order_by in [
        "name",
        "quantity",
        "total_price",
        "-total_price",
        "created_at",
        "-created_at",
    ]:
        inventory_items = inventory_items.order_by(order_by)
    else:
        inventory_items = inventory_items.order_by("name")

    # Statistics for the current filtered view
    total_items = inventory_items.count()
    total_value = inventory_items.aggregate(total=Sum("total_price"))["total"] or 0
    low_stock_count = inventory_items.filter(quantity__lt=0).count()

    # Pagination
    paginator = Paginator(inventory_items, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get available assemblies for filter
    assemblies = Assembly.objects.all()

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "status_filter": status_filter,
        "condition_filter": condition_filter,
        "assembly_filter": assembly_filter,
        "assemblies": assemblies,
        "status_choices": Inventory.STATUS_CHOICES,
        "condition_choices": Inventory.CONDITION_CHOICES,
        "order_by": order_by,
        "total_items": total_items,
        "total_value": total_value,
        "low_stock_count": low_stock_count,
    }

    return render(request, "inventory/inventory_list.html", context)


@login_required
def inventory_detail(request, pk):
    """
    Display detailed information about a specific inventory item
    """
    inventory_item = get_object_or_404(
        Inventory.objects.select_related("assembly", "added_by"), pk=pk
    )

    # Get related items from the same assembly
    related_items = Inventory.objects.filter(assembly=inventory_item.assembly).exclude(
        pk=pk
    )[:5]

    context = {
        "item": inventory_item,
        "related_items": related_items,
    }

    return render(request, "inventory/inventory_detail.html", context)


@login_required
def inventory_create(request):
    """
    Create a new inventory item
    """
    if request.method == "POST":
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            inventory_item = form.save(commit=False)
            inventory_item.added_by = request.user.admin_account
            inventory_item.save()

            messages.success(
                request, f'Inventory item "{inventory_item.name}" created successfully!'
            )
            return redirect("inventory_detail", pk=inventory_item.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill assembly if provided in GET parameters
        initial = {}
        assembly_id = request.GET.get("assembly")
        if assembly_id:
            try:
                initial["assembly"] = Assembly.objects.get(pk=assembly_id)
            except Assembly.DoesNotExist:
                pass
        form = InventoryForm(initial=initial)

    context = {
        "form": form,
        "title": "Add New Inventory Item",
    }

    return render(request, "inventory/inventory_form.html", context)


@login_required
def inventory_edit(request, pk):
    """
    Edit an existing inventory item
    """
    inventory_item = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        form = InventoryForm(request.POST, request.FILES, instance=inventory_item)
        if form.is_valid():
            inventory_item = form.save()

            messages.success(
                request, f'Inventory item "{inventory_item.name}" updated successfully!'
            )
            return redirect("inventory_detail", pk=inventory_item.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InventoryForm(instance=inventory_item)

    context = {
        "form": form,
        "title": f"Edit {inventory_item.name}",
        "item": inventory_item,
    }

    return render(request, "inventory/inventory_form.html", context)


@login_required
def inventory_delete(request, pk):
    """
    Delete an inventory item
    """
    inventory_item = get_object_or_404(Inventory, pk=pk)

    if request.method == "POST":
        item_name = inventory_item.name
        inventory_item.delete()

        messages.success(request, f'Inventory item "{item_name}" deleted successfully!')
        return redirect("inventory_list")

    context = {
        "item": inventory_item,
    }

    return render(request, "inventory/inventory_confirm_delete.html", context)


@login_required
def inventory_dashboard(request):
    """
    Dashboard view showing inventory statistics and overview
    """
    # Basic statistics
    total_items = Inventory.objects.count()
    total_value = Inventory.objects.aggregate(total=Sum("total_price"))["total"] or 0

    # Status counts
    status_counts = {}
    for status_code, status_name in Inventory.STATUS_CHOICES:
        count = Inventory.objects.filter(status=status_code).count()
        status_counts[status_name] = {
            "count": count,
            "percentage": (count / total_items * 100) if total_items > 0 else 0,
        }

    # Condition counts
    condition_counts = {}
    for condition_code, condition_name in Inventory.CONDITION_CHOICES:
        count = Inventory.objects.filter(condition=condition_code).count()
        condition_counts[condition_name] = {
            "count": count,
            "percentage": (count / total_items * 100) if total_items > 0 else 0,
        }

    # Assembly-wise distribution
    assembly_stats = Assembly.objects.annotate(
        item_count=Count("inventories"), total_value=Sum("inventories__total_price")
    ).order_by("-item_count")[:10]

    # Low stock items (quantity less than 5)
    low_stock_items = Inventory.objects.filter(quantity__lt=0).select_related(
        "assembly"
    )[:10]

    # Recent additions
    recent_items = Inventory.objects.select_related("assembly", "added_by").order_by(
        "-created_at"
    )[:1]

    # Items needing attention
    attention_items = Inventory.objects.filter(
        Q(condition__in=["fair", "poor", "broken"])
        | Q(status__in=["maintenance", "lost"])
    ).select_related("assembly")[:10]

    # Most valuable items
    valuable_items = (
        Inventory.objects.filter(total_price__isnull=False)
        .select_related("assembly")
        .order_by("-total_price")[:1]
    )

    context = {
        "total_items": total_items,
        "total_value": total_value,
        "status_counts": status_counts,
        "condition_counts": condition_counts,
        "assembly_stats": assembly_stats,
        "low_stock_items": low_stock_items,
        "recent_items": recent_items,
        "attention_items": attention_items,
        "valuable_items": valuable_items,
    }

    return render(request, "inventory/inventory_dashboard.html", context)


@login_required
def inventory_search(request):
    """
    AJAX search for inventory items - returns JSON response
    """
    query = request.GET.get("q", "")

    if query:
        inventory_items = Inventory.objects.select_related("assembly").filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(Brand__icontains=query)
            | Q(Model__icontains=query)
            | Q(location__icontains=query)
        )[:10]

        results = []
        for item in inventory_items:
            results.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "brand": item.Brand,
                    "model": item.Model,
                    "quantity": item.quantity,
                    "location": item.location,
                    "assembly": item.assembly.name,
                    "status": item.get_status_display(),
                    "condition": item.get_condition_display(),
                    "url": f"/inventory/{item.id}/",
                }
            )
    else:
        results = []

    return JsonResponse({"results": results})


@login_required
def inventory_quick_update(request, pk):
    """
    Quick update for inventory quantity (AJAX)
    """
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        inventory_item = get_object_or_404(Inventory, pk=pk)
        new_quantity = request.POST.get("quantity")

        try:
            inventory_item.quantity = int(new_quantity)
            inventory_item.save()

            return JsonResponse(
                {
                    "success": True,
                    "quantity": inventory_item.quantity,
                    "total_price": (
                        float(inventory_item.total_price)
                        if inventory_item.total_price
                        else 0
                    ),
                }
            )
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "Invalid quantity"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# AJAX Modal Views (following your existing pattern)
@login_required
def get_inventory_form(request, pk=None):
    """
    AJAX endpoint to get inventory form (create or edit)
    """
    if pk:
        inventory_item = get_object_or_404(Inventory, pk=pk)
        form = InventoryForm(instance=inventory_item)
        title = f"Edit {inventory_item.name}"
    else:
        form = InventoryForm()
        title = "Add New Inventory Item"

    html = render_to_string(
        "inventory/partials/inventory_form_modal.html",
        {
            "form": form,
            "title": title,
        },
        request=request,
    )

    return JsonResponse({"html": html})


@login_required
def create_inventory(request):
    """
    AJAX endpoint to create inventory item
    """
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            inventory_item = form.save(commit=False)
            inventory_item.added_by = request.user
            inventory_item.save()

            # Return the new row HTML for table update
            row_html = render_to_string(
                "inventory/partials/inventory_table_row.html",
                {"item": inventory_item},
                request=request,
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": f'Inventory item "{inventory_item.name}" created successfully!',
                    "item_id": inventory_item.id,
                    "row_html": row_html,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def update_inventory(request, pk):
    """
    AJAX endpoint to update inventory item
    """
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        inventory_item = get_object_or_404(Inventory, pk=pk)
        form = InventoryForm(request.POST, request.FILES, instance=inventory_item)
        if form.is_valid():
            inventory_item = form.save()

            # Return updated row HTML
            row_html = render_to_string(
                "inventory/partials/inventory_table_row.html",
                {"item": inventory_item},
                request=request,
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": f'Inventory item "{inventory_item.name}" updated successfully!',
                    "item_id": inventory_item.id,
                    "row_html": row_html,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def delete_inventory(request, pk):
    """
    AJAX endpoint to delete inventory item
    """
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        inventory_item = get_object_or_404(Inventory, pk=pk)
        item_name = inventory_item.name
        inventory_item.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f'Inventory item "{item_name}" deleted successfully!',
            }
        )

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def inventory_detail_modal(request, pk):
    """
    AJAX endpoint to get inventory detail modal
    """
    inventory_item = get_object_or_404(
        Inventory.objects.select_related("assembly", "added_by"), pk=pk
    )

    html = render_to_string(
        "inventory/partials/inventory_detail_modal.html",
        {
            "item": inventory_item,
        },
        request=request,
    )

    return JsonResponse({"html": html})
