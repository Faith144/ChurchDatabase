from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Assembly, Unit, Member, Cell, Admin

class UnitMemberInline(admin.TabularInline):
    """Inline members for Unit admin"""
    model = Member
    fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['first_name', 'last_name', 'email', 'phone']
    extra = 0
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj):
        return False

class CellMemberInline(admin.TabularInline):
    """Inline members for Cell admin"""
    model = Member
    fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['first_name', 'last_name', 'email', 'phone']
    extra = 0
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj):
        return False

class AssemblyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'city', 
        'state', 
        'member_count', 
        'is_active', 
        'created_at'
    ]
    list_filter = [
        'is_active', 
        'city', 
        'state', 
        'country', 
        'created_at'
    ]
    search_fields = [
        'name', 
        'city', 
        'state', 
        'email', 
        'phone'
    ]
    readonly_fields = ['created_at', 'updated_at', 'member_count_display']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 
                'description', 
                'founded_date', 
                'is_active'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 
                'phone', 
                'website'
            )
        }),
        ('Address Information', {
            'fields': (
                'street_address',
                'city',
                'state', 
                'country', 
                'zip_code'
            )
        }),
        ('Location Coordinates', {
            'fields': (
                'latitude', 
                'longitude'
            ),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': (
                'facebook_url',
                'twitter_url',
                'instagram_url',
                'youtube_url'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'member_count_display',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    member_count.admin_order_field = 'member_count'
    
    def member_count_display(self, obj):
        count = obj.members.count()
        url = reverse('admin:core_member_changelist') + f'?assembly__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    member_count_display.short_description = 'Total Members'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(member_count=Count('members'))
        return queryset

class UnitAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'leader_link', 
        'member_count', 
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'leader__first_name', 'leader__last_name']
    readonly_fields = ['created_at', 'updated_at', 'member_count_display']
    autocomplete_fields = ['leader']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 
                'description'
            )
        }),
        ('Leadership', {
            'fields': (
                'leader',
            )
        }),
        ('Statistics', {
            'fields': (
                'member_count_display',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [UnitMemberInline]
    
    def leader_link(self, obj):
        if obj.leader:
            url = reverse('admin:core_member_change', args=[obj.leader.id])
            return format_html('<a href="{}">{}</a>', url, f"{obj.leader.first_name} {obj.leader.last_name}")
        return "-"
    leader_link.short_description = 'Leader'
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    member_count.admin_order_field = 'member_count'
    
    def member_count_display(self, obj):
        count = obj.members.count()
        url = reverse('admin:core_member_changelist') + f'?unit__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    member_count_display.short_description = 'Total Members'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(member_count=Count('members'))
        return queryset

class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'assembly_link',
        'unit_link',
        'cell_link',
        'membership_status_badge',
        'email',
        'phone',
        'age',
        'created_at'
    ]
    list_filter = [
        'assembly',
        'unit',
        'cell',
        'membership_status',
        'gender',
        'marital_status',
        'created_at'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'middle_name',
        'email',
        'phone',
        'address'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'age_display',
        'photo_preview'
    ]
    autocomplete_fields = ['assembly', 'unit', 'cell']
    list_select_related = ['assembly', 'unit', 'cell']
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'photo',
                'photo_preview',
                ('first_name', 'last_name', 'middle_name'),
                ('date_of_birth', 'age_display'),
                ('gender', 'marital_status'),
                'month_of_birth',
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'phone',
                'address',
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
            ),
            'classes': ('collapse',)
        }),
        ('Church Information', {
            'fields': (
                'assembly',
                'unit',
                'cell',
                'membership_status',
                'membership_date',
            )
        }),
        ('Sacraments & Important Dates', {
            'fields': (
                'baptism_date',
                'confirmation_date',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    full_name.admin_order_field = 'last_name'
    
    def assembly_link(self, obj):
        if obj.assembly:
            url = reverse('admin:core_assembly_change', args=[obj.assembly.id])
            return format_html('<a href="{}">{}</a>', url, obj.assembly.name)
        return "-"
    assembly_link.short_description = 'Assembly'
    
    def unit_link(self, obj):
        if obj.unit:
            url = reverse('admin:core_unit_change', args=[obj.unit.id])
            return format_html('<a href="{}">{}</a>', url, obj.unit.name)
        return "-"
    unit_link.short_description = 'Unit'
    
    def cell_link(self, obj):
        if obj.cell:
            url = reverse('admin:core_cell_change', args=[obj.cell.id])
            return format_html('<a href="{}">{}</a>', url, obj.cell.name)
        return "-"
    cell_link.short_description = 'Cell'
    
    def membership_status_badge(self, obj):
        status_colors = {
            'ACTIVE': 'success',
            'INACTIVE': 'warning',
            'VISITOR': 'info',
            'NEW_MEMBER': 'primary',
            'TRANSFERRED': 'secondary'
        }
        color = status_colors.get(obj.membership_status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.membership_status
        )
    membership_status_badge.short_description = 'Status'
    membership_status_badge.admin_order_field = 'membership_status'
    
    def age_display(self, obj):
        return obj.age or "N/A"
    age_display.short_description = 'Age'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.photo.url
            )
        return "No photo"
    photo_preview.short_description = 'Photo Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assembly', 'unit', 'cell')

class CellAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_at',
        'member_count',
        'created_at_formatted'
    ]
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['member_count_display', 'created_at_formatted']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'created_at',
            )
        }),
        ('Statistics', {
            'fields': (
                'member_count_display',
            )
        }),
    )
    inlines = [CellMemberInline]
    
    def member_count(self, obj):
        return obj.member_set.count()
    member_count.short_description = 'Members'
    member_count.admin_order_field = 'member_count'
    
    def member_count_display(self, obj):
        count = obj.member_set.count()
        url = reverse('admin:core_member_changelist') + f'?cell__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    member_count_display.short_description = 'Total Members'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
    created_at_formatted.short_description = 'Created Date'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(member_count=Count('member'))
        return queryset

# Register your models here
admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Cell, CellAdmin)
admin.site.register(Admin)

# Admin site customization
admin.site.site_header = 'Church Management System Administration'
admin.site.site_title = 'Church Management System'
admin.site.index_title = 'Church Management Administration'

# Custom actions
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_active.short_description = "Mark selected as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_inactive.short_description = "Mark selected as inactive"

def mark_as_active_members(modeladmin, request, queryset):
    queryset.update(membership_status='ACTIVE')
mark_as_active_members.short_description = "Mark selected members as ACTIVE"

def mark_as_inactive_members(modeladmin, request, queryset):
    queryset.update(membership_status='INACTIVE')
mark_as_inactive_members.short_description = "Mark selected members as INACTIVE"

# Add custom actions to models
AssemblyAdmin.actions = [make_active, make_inactive]
MemberAdmin.actions = [mark_as_active_members, mark_as_inactive_members]