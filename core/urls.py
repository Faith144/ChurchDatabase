from django.urls import path
from . import views
from . import commiteeview as com_views
from . import inventoryviews as inv_views  # Import inventory views
from . import adminviews

urlpatterns = [
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # AJAX endpoints
    path("ajax/search/", views.ajax_search, name="ajax_search"),
    path("ajax/quick-stats/", views.quick_stats, name="quick_stats"),
    # Member AJAX endpoints
    path(
        "ajax/members/<int:pk>/", views.member_detail_modal, name="member_detail_modal"
    ),
    path("ajax/members/form/", views.get_member_form, name="get_member_form"),
    path(
        "ajax/members/form/<int:pk>/",
        views.get_member_form,
        name="get_member_form_update",
    ),
    path("ajax/members/create/", views.create_member, name="create_member"),
    path("ajax/members/update/<int:pk>/", views.update_member, name="update_member"),
    path("ajax/members/delete/<int:pk>/", views.delete_member, name="delete_member"),
    # Family AJAX endpoints
    # # path('ajax/families/<int:pk>/', views.family_detail_modal, name='family_detail_modal'),
    # # path('ajax/families/form/', views.get_family_form, name='get_family_form'),
    # # path('ajax/families/form/<int:pk>/', views.get_family_form, name='get_family_form_update'),
    # # path('ajax/families/create/', views.create_family, name='create_family'),
    # # path('ajax/families/update/<int:pk>/', views.update_family, name='update_family'),
    # # path('ajax/families/delete/<int:pk>/', views.delete_family, name='delete_family'),
    # Public routes
    path("register/", views.public_registration, name="public_registration"),
    path(
        "registration/success/", views.registration_success, name="registration_success"
    ),
    # Cell AJAX endpoints
    path("ajax/cells/form/", views.get_cell_form, name="get_cell_form"),
    path("ajax/cells/form/<int:pk>/", views.get_cell_form, name="get_cell_form_update"),
    path("ajax/cells/create/", views.create_cell, name="create_cell"),
    path("ajax/cells/update/<int:pk>/", views.update_cell, name="update_cell"),
    path("ajax/cells/delete/<int:pk>/", views.delete_cell, name="delete_cell"),
    # Assembly AJAX endpoints
    path("ajax/assemblies/form/", views.get_assembly_form, name="get_assembly_form"),
    path(
        "ajax/assemblies/form/<int:pk>/",
        views.get_assembly_form,
        name="get_assembly_form_update",
    ),
    path("ajax/assemblies/create/", views.create_assembly, name="create_assembly"),
    path(
        "ajax/assemblies/update/<int:pk>/",
        views.update_assembly,
        name="update_assembly",
    ),
    path(
        "ajax/assemblies/delete/<int:pk>/",
        views.delete_assembly,
        name="delete_assembly",
    ),
    # List pages
    path("members/", views.member_list, name="member_list"),
    # # path('families/', views.family_list, name='family_list'),
    path("units/", views.unit_list, name="unit_list"),
    path("cells/", views.cell_list, name="cell_list"),
    path("assemblies/", views.assembly_list, name="assembly_list"),
    # Detail pages
    path("members/<int:pk>/", views.member_detail, name="member_detail"),
    # # path('families/<int:pk>/', views.family_detail, name='family_detail'),
    path("units/<int:pk>/", views.unit_detail, name="unit_detail"),
    path("cells/<int:pk>/", views.cell_detail, name="cell_detail"),
    path("assemblies/<int:pk>/", views.assembly_detail, name="assembly_detail"),
    # Unit AJAX endpoints
    path("ajax/units/form/", views.get_unit_form, name="get_unit_form"),
    path("ajax/units/form/<int:pk>/", views.get_unit_form, name="get_unit_form_update"),
    path("ajax/units/create/", views.create_unit, name="create_unit"),
    path("ajax/units/update/<int:pk>/", views.update_unit, name="update_unit"),
    path("ajax/units/delete/<int:pk>/", views.delete_unit, name="delete_unit"),
    path("ajax/units/<int:pk>/", views.unit_detail_modal, name="unit_detail_modal"),
    # Cell detail modal
    path("ajax/cells/<int:pk>/", views.cell_detail_modal, name="cell_detail_modal"),
    # Assembly detail modal
    path(
        "ajax/assemblies/<int:pk>/",
        views.assembly_detail_modal,
        name="assembly_detail_modal",
    ),
    # Committee URLs
    path("committee/", com_views.committee_list, name="committee-list"),
    path("committee/<int:pk>/", com_views.committee_detail, name="committee-detail"),
    path("committee/create/", com_views.committee_create, name="committee-create"),
    path(
        "committee/<int:pk>/update/",
        com_views.committee_update,
        name="committee-update",
    ),
    path(
        "committee/<int:pk>/delete/",
        com_views.committee_delete,
        name="committee-delete",
    ),
    # Committee Membership AJAX endpoints
    path(
        "committee/<int:committee_id>/members/add/",
        com_views.add_committee_member,
        name="add-committee-member",
    ),
    path(
        "committee/<int:committee_id>/members/remove/<int:membership_id>/",
        com_views.remove_committee_member,
        name="remove-committee-member",
    ),
    path(
        "committee/<int:committee_id>/members/role/<int:membership_id>/",
        com_views.update_member_role,
        name="update-member-role",
    ),
    path(
        "committee/<int:committee_id>/leader/set/",
        com_views.set_committee_leader,
        name="set-committee-leader",
    ),
    # ==================== INVENTORY URLS ====================
    # Inventory List and Dashboard
    path("inventory/", inv_views.inventory_list, name="inventory_list"),
    path(
        "inventory/dashboard/",
        inv_views.inventory_dashboard,
        name="inventory_dashboard",
    ),
    # Inventory CRUD operations
    path("inventory/create/", inv_views.inventory_create, name="inventory_create"),
    path("inventory/<int:pk>/", inv_views.inventory_detail, name="inventory_detail"),
    path("inventory/<int:pk>/edit/", inv_views.inventory_edit, name="inventory_edit"),
    path(
        "inventory/<int:pk>/delete/",
        inv_views.inventory_delete,
        name="inventory_delete",
    ),
    # Inventory AJAX endpoints
    path("ajax/inventory/search/", inv_views.inventory_search, name="inventory_search"),
    path(
        "ajax/inventory/quick-update/<int:pk>/",
        inv_views.inventory_quick_update,
        name="inventory_quick_update",
    ),
    path(
        "ajax/inventory/form/", inv_views.get_inventory_form, name="get_inventory_form"
    ),
    path(
        "ajax/inventory/form/<int:pk>/",
        inv_views.get_inventory_form,
        name="get_inventory_form_update",
    ),
    path("ajax/inventory/create/", inv_views.create_inventory, name="create_inventory"),
    path(
        "ajax/inventory/update/<int:pk>/",
        inv_views.update_inventory,
        name="update_inventory",
    ),
    path(
        "ajax/inventory/delete/<int:pk>/",
        inv_views.delete_inventory,
        name="delete_inventory",
    ),
    path(
        "ajax/inventory/<int:pk>/",
        inv_views.inventory_detail_modal,
        name="inventory_detail_modal",
    ),
    # ==================== ADMIN URLS ====================
    # path("dashboard/", adminviews.admin_dashboard, name="dashboard"),
    # Admin Management
    path("", adminviews.AdminListView.as_view(), name="admin_list"),
    path("create/", adminviews.admin_create, name="admin_create"),
    path("<int:pk>/", adminviews.admin_detail, name="admin_detail"),
    path("<int:pk>/update/", adminviews.admin_update, name="admin_update"),
    path(
        "<int:pk>/change-level/",
        adminviews.admin_change_level,
        name="admin_change_level",
    ),
    path("<int:pk>/delete/", adminviews.admin_delete, name="admin_delete"),
]
