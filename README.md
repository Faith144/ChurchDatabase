# SEPCAM Church Management System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2%2B-success?logo=django)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Database](https://img.shields.io/badge/Database-PostgreSQL%2FSQLite-blue)

---

## 📚 Table of Contents
- [📖 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🏗️ System Architecture](#️-system-architecture)
- [🔐 Authentication & Authorization](#-authentication--authorization)
- [📊 Core Features](#-core-features)
- [🎯 User Guide](#-user-guide)
- [🔧 Technical Implementation](#-technical-implementation)
- [📱 Mobile Responsiveness](#-mobile-responsiveness)
- [🔒 Security Features](#-security-features)
- [🛠️ Development](#️-development)
- [📈 Deployment](#-deployment)
- [🆘 Support & Troubleshooting](#-support--troubleshooting)
- [🔄 Version Information](#-version-information)
- [📄 License](#-license)

---

## 📖 Overview

The **SEPCAM Church Management System** is a comprehensive Django web application designed to help churches efficiently manage their members, administrative structure, and operations. Built with Django and featuring a responsive Bootstrap interface, the system provides role-based access control, member management, organizational hierarchy management, and inventory tracking.

### 🎯 Purpose
- Streamline church administration and member management
- Provide role-based access for different staff levels
- Maintain comprehensive member and organizational records
- Enable efficient inventory and asset management

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Django 4.2+**
- **PostgreSQL** (recommended) or **SQLite**
- Modern web browser with JavaScript enabled

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Faith144/ChurchDatabase.git
   cd ChurchDatabase
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database Settings**
   ```python
   # In settings.py, configure your database
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'sepcam_church',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Super Admin Account**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to create your first super admin account.

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

---

## 🏗️ System Architecture

### Core Data Models

#### 👥 Member Management
```python
class Member(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Church Information
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True)
    membership_status = models.CharField(max_length=15, choices=MEMBERSHIP_STATUS_CHOICES)
```

#### 🏛️ Organizational Structure
```python
class Assembly(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class Unit(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)

class Cell(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateField()
```

#### 👨‍💼 Admin System
```python
class Admin(models.Model):
    ADMIN_TYPE_CHOICES = [
        ("SUPERADMIN", "Super Admin"),
        ("Cell", "Cell"),
        ("MODERATOR", "Moderator"),
        ("Inventory", "Inventory"),
    ]
    
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    level = models.CharField(max_length=100, choices=ADMIN_TYPE_CHOICES)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, null=True, blank=True)
    user_account = models.OneToOneField(User, on_delete=models.CASCADE)
```

#### 📦 Inventory Management
```python
class Inventory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=200)
```

---

## 🔐 Authentication & Authorization

### User Roles and Permissions

| Role | Description | Permissions | Access Level |
|------|-------------|-------------|--------------|
| **Super Admin** | Full system administrator | • Manage all admins<br>• Access all data<br>• System configuration<br>• Create/delete assemblies | Global |
| **Cell Admin** | Manages specific cell | • Manage cell members only<br>• View cell statistics<br>• Add members to cell | Cell-specific |
| **Moderator** | Assembly-wide manager | • Manage all assembly members<br>• Content management<br>• Member operations | Assembly-wide |
| **Inventory Admin** | Asset manager | • Manage inventory only<br>• Track equipment<br>• Update asset status | Inventory only |

### Login System Features
- **Automatic Redirection**: Users are redirected to appropriate dashboards based on their role
- **Session Management**: Secure session-based authentication
- **Auto-generated Credentials**: New admin accounts automatically get user credentials
- **Role-based Access Control**: Each role has specific permissions and data access

### Access Flow
```python
def login_view(request):
    if admin_profile.is_superadmin:
        return redirect("dashboard")
    elif admin_profile.is_cell_admin:
        return redirect("member_list")
    elif admin_profile.is_inventory_admin:
        return redirect("inventory_dashboard")
```

---

## 📊 Core Features

### 1. 📈 Dashboard & Analytics
**Real-time Church Statistics**
- Total members count with growth metrics
- Active vs inactive member breakdown
- New members registered today
- Assembly, unit, and cell statistics
- Recent member activity feed

**Advanced Filtering**
- Filter by assembly, unit, cell
- Membership status filtering
- Date range selection
- Birth month categorization

### 2. 👥 Member Management
**Complete Member Profiles**
- Personal information (name, DOB, gender)
- Contact details (email, phone, address)
- Emergency contact information
- Church assignment (assembly, unit, cell)
- Membership status tracking
- Photo upload capability

**Member Operations**
- Add new members with validation
- Edit existing member information
- Bulk member operations
- Advanced search and filtering
- Public registration form for new members

### 3. 🏢 Organizational Management
**Assembly Management**
- Create and manage church locations
- Contact information and addresses
- Social media integration
- Status tracking (active/inactive)

**Unit Management**
- Department and ministry organization
- Leader assignment
- Member grouping and management

**Cell Management**
- Small group organization
- Geographical division management
- Cell-specific admin assignments

### 4. 👨‍💼 Admin Management
**Admin Account Creation**
- Select existing members to make admins
- Choose from four admin levels
- Automatic user account generation
- Assembly and cell assignment

**Admin Operations**
- View all admin accounts
- Change admin levels and permissions
- Monitor admin activity
- Delete admin accounts when needed

### 5. 📦 Inventory Management
**Asset Tracking**
- Item name, description, and specifications
- Quantity and pricing information
- Condition and status monitoring
- Location tracking within church premises

**Inventory Operations**
- Add new inventory items
- Update item status and condition
- Track maintenance and repairs
- Image upload for items

---

## 🎯 User Guide

### 👑 For Super Admins

#### System Access
1. **Login**: Use your super admin credentials
2. **Dashboard**: View system-wide statistics and recent activity
3. **Navigation**: Use sidebar to access all system modules

#### Admin Management
1. **View All Admins**: Click "Admin Management" in sidebar
2. **Create New Admin**:
   - Click "Create New Admin" button
   - Select existing member from dropdown
   - Choose admin level (Super Admin, Cell Admin, Moderator, Inventory Admin)
   - Select assembly and cell (if applicable)
   - Save - system auto-generates username and password

3. **Manage Admin Permissions**:
   - Go to admin list
   - Click "Change Level" for specific admin
   - Modify admin level and permissions
   - Save changes

#### Member Management
- Access all members across all assemblies
- Create, edit, and delete member records
- Use advanced filters for specific member groups
- Export member data as needed

#### Organizational Management
- Create and manage assemblies
- Set up units and assign leaders
- Organize cells and assign cell admins

### 👤 For Cell Admins

#### Access Limitations
- Can only view and manage members in assigned cell
- Cannot access other cells or system-wide data
- Limited to cell-specific operations

#### Member Management
1. **View Cell Members**: Member list shows only your cell members
2. **Add New Member**:
   - Cell is automatically assigned to your cell
   - Fill in member details
   - System restricts access to your cell only

3. **Edit Member Information**:
   - Modify details for cell members only
   - Cannot change cell assignment (automatically set)

#### Dashboard Features
- Cell-specific statistics
- Recent activity for your cell only
- Filters limited to your cell data

### 📊 For All Users

#### Using the Dashboard
1. **Quick Statistics**: View key metrics at top of dashboard
2. **Global Search**: Use search bar for quick member/organization lookup
3. **Recent Activity**: Monitor recently added members and changes
4. **Member List**: View and filter members based on your permissions

#### Member Operations
1. **Adding Members**:
   - Click "Add Member" button from any member view
   - Fill required fields (name, contact information)
   - System auto-assigns based on your role
   - Upload member photo if available
   - Set membership status appropriately

2. **Searching Members**:
   - Use global search bar for quick text search
   - Apply filters for specific criteria (assembly, unit, status, etc.)
   - Combine multiple filters for precise results
   - Search by name, email, phone, or other attributes

3. **Editing Members**:
   - Click edit icon (pencil) next to any member
   - Update information in the form
   - Changes save immediately upon submission
   - Photo can be updated if needed

#### Using Filters
- **Assembly Filter**: Filter by specific church location
- **Unit Filter**: Filter by department or ministry
- **Cell Filter**: Filter by small group (Super Admins only)
- **Status Filter**: Filter by membership status
- **Gender Filter**: Filter by gender
- **Birth Month**: Filter members by birth month

---

## 🔧 Technical Implementation

### Key Views and Functions

#### Dashboard View
```python
@login_required
def dashboard(request):
    """Main dashboard with overview and all functionality"""
    try:
        admin_profile = request.user.admin_account
        
        # Role-based data filtering
        if admin_profile.is_superadmin:
            members = Member.objects.all().select_related("assembly", "unit", "cell")
        elif admin_profile.is_cell_admin:
            members = Member.objects.filter(cell=admin_profile.cell)
        
        # Statistics calculation
        total_members = Member.objects.count()
        active_members = Member.objects.filter(membership_status="ACTIVE").count()
        new_members_today = Member.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        
        # Context preparation
        context = {
            "total_members": total_members,
            "active_members": active_members,
            "new_members_today": new_members_today,
            "members": members,
        }
        
        return render(request, "dashboard/dashboard.html", context)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

#### Admin Management Views
```python
class AdminListView(SuperAdminRequiredMixin, ListView):
    """List all admins in the system - Super Admin only"""
    model = Admin
    template_name = "admins/admin_list.html"
    context_object_name = "admins"
    paginate_by = 20

    def get_queryset(self):
        queryset = Admin.objects.all()
        # Apply filters for level, search, cell
        return queryset.order_by("member__first_name", "member__last_name")

@login_required
def admin_create(request):
    """Create a new admin account - Super Admin only"""
    if request.method == "POST":
        form = AdminForm(request.POST, current_user=request.user)
        if form.is_valid():
            admin = form.save()
            # Auto-generate user account
            admin.create_user_account()
            messages.success(request, f"Admin account created for {admin.get_full_name()}")
            return redirect("admin_list")
```

#### Member Management Views
```python
def member_list(request):
    """List all members with filtering and pagination"""
    admin_profile = request.user.admin_account
    
    # Role-based filtering
    if admin_profile.is_superadmin:
        members = Member.objects.all().select_related("assembly", "unit", "cell")
    elif admin_profile.is_cell_admin:
        members = Member.objects.filter(cell=admin_profile.cell)
    
    # Apply filters from request
    assembly_id = request.GET.get("assembly")
    unit_id = request.GET.get("unit")
    status = request.GET.get("status")
    search = request.GET.get("search")
    
    if assembly_id:
        members = members.filter(assembly_id=assembly_id)
    if unit_id:
        members = members.filter(unit_id=unit_id)
    if status:
        members = members.filter(membership_status=status)
    if search:
        members = members.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(members, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "members/member_list.html", {"members": page_obj})
```

### URL Structure

#### Main Application URLs
```python
urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # AJAX endpoints
    path("ajax/search/", views.ajax_search, name="ajax_search"),
    path("ajax/quick-stats/", views.quick_stats, name="quick_stats"),
    
    # Member management
    path("members/", views.member_list, name="member_list"),
    path("members/<int:pk>/", views.member_detail, name="member_detail"),
    
    # Organizational management
    path("units/", views.unit_list, name="unit_list"),
    path("cells/", views.cell_list, name="cell_list"),
    path("assemblies/", views.assembly_list, name="assembly_list"),
    
    # Admin management (Super Admins only)
    path("admins/", adminviews.AdminListView.as_view(), name="admin_list"),
    path("admins/create/", adminviews.admin_create, name="admin_create"),
    path("admins/<int:pk>/", adminviews.admin_detail, name="admin_detail"),
    path("admins/<int:pk>/update/", adminviews.admin_update, name="admin_update"),
    path("admins/<int:pk>/change-level/", adminviews.admin_change_level, name="admin_change_level"),
    path("admins/<int:pk>/delete/", adminviews.admin_delete, name="admin_delete"),
]
```

#### AJAX Endpoints
```python
# Member AJAX endpoints
path("ajax/members/form/", views.get_member_form, name="get_member_form"),
path("ajax/members/form/<int:pk>/", views.get_member_form, name="get_member_form_update"),
path("ajax/members/create/", views.create_member, name="create_member"),
path("ajax/members/update/<int:pk>/", views.update_member, name="update_member"),
path("ajax/members/delete/<int:pk>/", views.delete_member, name="delete_member"),

# Organizational AJAX endpoints
path("ajax/units/form/", views.get_unit_form, name="get_unit_form"),
path("ajax/cells/form/", views.get_cell_form, name="get_cell_form"),
path("ajax/assemblies/form/", views.get_assembly_form, name="get_assembly_form"),
```

### Database Schema

#### Key Relationships
- **Member** → Assembly, Unit, Cell (Foreign Keys)
- **Admin** → Member, Assembly, Cell (Foreign Keys + User)
- **Inventory** → Assembly, Admin (Foreign Keys)
- **Unit** → Member (Leader Foreign Key)

#### Important Fields
- **Members**: membership_status, date_of_birth, baptism_date
- **Admins**: level (SUPERADMIN, Cell, MODERATOR, Inventory)
- **Inventory**: status, condition, location

---

## 📱 Mobile Responsiveness

### Design Philosophy
The system is built with **mobile-first** approach, ensuring seamless experience across all devices.

### Responsive Features

#### 📱 Mobile Optimization
- **Collapsible sidebar** that becomes hamburger menu on small screens
- **Responsive tables** with horizontal scrolling for data tables
- **Touch-friendly buttons** with appropriate sizing and spacing
- **Optimized forms** that stack vertically on mobile devices
- **Fast-loading** components for slower mobile networks

#### 💻 Desktop Enhancement
- **Full sidebar** with expanded navigation
- **Multi-column layouts** for better data presentation
- **Hover effects** and advanced interactions
- **Larger data tables** with more visible columns

#### 📟 Tablet Adaptation
- **Hybrid layouts** that balance mobile and desktop features
- **Adaptive images** that scale appropriately
- **Touch-optimized** navigation elements

### Technical Implementation
```html
<!-- Base template with responsive design -->
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar - collapses on mobile -->
        <nav class="sidebar col-lg-2 col-md-3" id="sidebar">
            <!-- Navigation items -->
        </nav>
        
        <!-- Main content - expands on mobile -->
        <main class="main-content col-lg-10 col-md-9" id="mainContent">
            <!-- Responsive content -->
            <div class="table-responsive">
                <table class="table table-hover">
                    <!-- Table content -->
                </table>
            </div>
        </main>
    </div>
</div>
```

---

## 🔒 Security Features

### Authentication Security
- **Session-based authentication** with secure cookie handling
- **CSRF protection** on all forms and AJAX requests
- **Password hashing** using Django's built-in PBKDF2 hasher
- **Automatic session expiry** and cleanup

### Authorization Security
- **Role-based access control** (RBAC) at view level
- **Permission decorators** on all sensitive views
- **Query-level filtering** to ensure users only see authorized data
- **Admin-level validation** in forms and business logic

### Data Security
- **Input validation** and sanitization on all forms
- **SQL injection prevention** through Django ORM
- **XSS protection** through template auto-escaping
- **File upload validation** for member photos and inventory images

### Security Implementation Examples

#### View Protection
```python
class SuperAdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only super admins can access the view"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if (not hasattr(request.user, "admin_account") or 
            not request.user.admin_account.is_superadmin):
            messages.error(request, "Only super administrators can access this page.")
            return redirect("dashboard")
            
        return super().dispatch(request, *args, **kwargs)
```

#### Data Filtering
```python
@login_required
def get_member_form(request, pk=None):
    """Return member form with cell filtering for cell admins"""
    # Filter cell field for cell admins
    if hasattr(request.user, "admin_account"):
        admin_account = request.user.admin_account
        if (admin_account.is_cell_admin and admin_account.cell):
            form.fields["cell"].queryset = Cell.objects.filter(id=admin_account.cell.id)
            form.fields["cell"].empty_label = None
```

---

## 🛠️ Development

### Project Structure
```
sepcam_church_system/
├── 📁 models.py              # Database models and relationships
├── 📁 views.py               # Main application views and logic
├── 📁 adminviews.py          # Admin management specific views
├── 📁 adminforms.py          # Forms for admin management
├── 📁 urls.py                # URL routing configuration
├── 📁 templates/             # HTML templates
│   ├── 📁 base.html          # Base template with navigation
│   ├── 📁 dashboard/         # Dashboard templates
│   │   ├── dashboard.html    # Main dashboard
│   │   └── 📁 partials/      # AJAX partial templates
│   ├── 📁 admins/            # Admin management templates
│   │   ├── admin_list.html   # Admin listing
│   │   ├── admin_form.html   # Admin creation/editing
│   │   ├── admin_detail.html # Admin details
│   │   └── admin_confirm_delete.html # Delete confirmation
│   ├── 📁 members/           # Member management templates
│   │   ├── member_list.html  # Member listing with filters
│   │   └── member_detail.html # Member profile view
│   └── 📁 auth/              # Authentication templates
│       └── login.html        # Login page
├── 📁 static/                # Static assets
│   ├── 📁 css/               # Stylesheets
│   ├── 📁 js/                # JavaScript files
│   └── 📁 images/            # Images and icons
└── 📁 media/                 # User uploaded files
    ├── 📁 member_photos/     # Member profile pictures
    └── 📁 inventory_images/  # Inventory item photos
```

### Key Dependencies

#### Backend Dependencies
- **Django 4.2+**: Web framework
- **Pillow**: Image processing for photo uploads
- **Python-decouple**: Environment configuration
- **Whitenoise**: Static file serving

#### Frontend Dependencies
- **Bootstrap 5.3+**: CSS framework and components
- **jQuery 3.6+**: JavaScript utilities and AJAX
- **Font Awesome 6.4+**: Icons and UI elements
- **DataTables** (optional): Enhanced table functionality

### Development Workflow

#### Setting Up Development Environment
1. **Clone and setup virtual environment**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure development database**
4. **Run migrations**: `python manage.py migrate`
5. **Create test data**: `python manage.py create_test_data` (if available)
6. **Start development server**: `python manage.py runserver`

#### Adding New Features
1. **Define Model** in `models.py`
2. **Create Forms** in appropriate forms file
3. **Implement Views** with proper permission checks
4. **Build Templates** following existing patterns
5. **Configure URLs** in `urls.py`
6. **Test Thoroughly** with different user roles

#### Code Standards
- **Follow Django best practices** for project structure
- **Use class-based views** where appropriate
- **Implement proper error handling** in all views
- **Write docstrings** for all functions and classes
- **Maintain consistent naming conventions**

---

## 📈 Deployment

### Production Checklist

#### 🔧 Configuration
- [ ] Set `DEBUG = False` in production
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set `ALLOWED_HOSTS` with your domain
- [ ] Configure `SECRET_KEY` properly
- [ ] Set up proper `MEDIA_ROOT` and `STATIC_ROOT`

#### 🌐 Web Server
- [ ] Configure web server (Nginx/Apache)
- [ ] Set up WSGI application server (Gunicorn/uWSGI)
- [ ] Configure static and media file serving
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up proper caching headers

#### 📧 Email & Notifications
- [ ] Configure email backend for notifications
- [ ] Set up error reporting (Sentry/email)
- [ ] Configure backup notifications

#### 💾 Database & Storage
- [ ] Set up database backups
- [ ] Configure media file storage (local or cloud)
- [ ] Set up regular database maintenance

### Environment Variables
```bash
# Required environment variables
DEBUG=False
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=postgres://user:password@host:port/database
ALLOWED_HOSTS=.yourdomain.com,localhost
```

### Deployment Steps

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade

# Install Python and dependencies
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx

# Create database and user
sudo -u postgres createdb sepcam_church
sudo -u postgres createuser --pwprompt church_user
```

#### 2. Application Setup
```bash
# Clone application
git clone https://github.com/Faith144/ChurchDatabase.git
cd sepcam-church-system

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

#### 3. Web Server Configuration
```nginx
# Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/static/files;
    }
    
    location /media/ {
        alias /path/to/your/media/files;
    }
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. Process Management
```bash
# Using systemd for Gunicorn
sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon for SEPCAM Church System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/your/app/app.sock your_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

---

## 🆘 Support & Troubleshooting

### Common Issues and Solutions

#### 🔐 Authentication Issues
| Problem | Cause | Solution |
|---------|-------|----------|
| **Cannot login** | Invalid credentials or inactive account | Verify username/password, check admin account status |
| **Wrong redirect after login** | Admin level not properly set | Contact Super Admin to verify admin level |
| **Session expires too quickly** | Session configuration | Check Django session settings |

#### 👥 Member Management Issues
| Problem | Cause | Solution |
|---------|-------|----------|
| **Cannot see all members** | Cell admin restrictions | Cell admins only see their cell members |
| **Member not appearing in lists** | Filter applied | Clear filters or check membership status |
| **Cannot edit member** | Permission restrictions | Verify you have appropriate admin level |

#### 👨‍💼 Admin Management Issues
| Problem | Cause | Solution |
|---------|-------|----------|
| **Cannot create admin** | Member doesn't exist | Create member record first |
| **Admin level change not working** | Permission issues | Only Super Admins can change admin levels |
| **Duplicate admin accounts** | Member already has admin profile | Check existing admin assignments |

### Performance Optimization

#### Database Optimization
- Use `select_related()` and `prefetch_related()` for foreign key relationships
- Implement database indexing on frequently queried fields
- Use pagination for large datasets

#### Caching Strategies
```python
# Implement view caching for frequently accessed pages
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def member_list(request):
    # View logic
```

### Backup and Recovery

#### Automated Backups
```bash
#!/bin/bash
# backup_script.sh
DATE=$(date +%Y-%m-%d_%H-%M-%S)
pg_dump sepcam_church > /backups/church_db_$DATE.sql
tar -czf /backups/church_media_$DATE.tar.gz /path/to/media/files
```

#### Recovery Procedures
1. **Database Recovery**: `psql sepcam_church < backup_file.sql`
2. **Media Files**: Extract backup tar.gz to media directory
3. **Verify Integrity**: Check key data and relationships

---

## 🔄 Version Information

### Current Version: 1.0

### Technology Stack
| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8+ | Backend programming language |
| **Django** | 4.2+ | Web framework |
| **PostgreSQL** | 12+ | Primary database (recommended) |
| **SQLite** | 3.35+ | Development database |
| **Bootstrap** | 5.3+ | Frontend framework |
| **jQuery** | 3.6+ | JavaScript utilities |

### Version History
- **v1.0** (Current): Initial production release with core features
  - Member management
  - Admin system with role-based access
  - Organizational structure
  - Inventory management
  - Responsive design

### Upgrade Instructions
When upgrading between versions:
1. **Backup** database and media files
2. **Update code** to new version
3. **Run migrations**: `python manage.py migrate`
4. **Update static files**: `python manage.py collectstatic`
5. **Test thoroughly** before going live

---

## 📄 License

### Proprietary Software
This **SEPCAM Church Management System** is proprietary software developed specifically for church administration and management.

### Usage Rights
- ✅ **Authorized Use**: Licensed for use by authorized churches and organizations
- ✅ **Internal Use**: Can be used for internal church management
- ✅ **Customization**: Can be customized for specific church needs

### Restrictions
- ❌ **Redistribution**: Cannot be redistributed or resold
- ❌ **Commercial Use**: Cannot be used for commercial purposes without authorization
- ❌ **Source Modification**: Source code modifications require authorization

### Support and Maintenance
For support, customization, or feature requests, please contact:
- **System Administration Team**
- **Technical Support**: [Contact Information]
- **Feature Requests**: [Process for submitting requests]

### Copyright
© 2024 SEPCAM Church Management System. All rights reserved.

---

*This documentation is maintained by the SEPCAM development team. For updates or corrections, please contact the system administrators.*