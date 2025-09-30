# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Assembly(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    founded_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address Information
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Location coordinates (optional)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Church Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Assemblies"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Unit(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(
        'Member', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='led_units'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Units"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}"

class Cell(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateField()
    
    def __str__(self):
        return self.name

class Family(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='families')
    family_name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Families"
        ordering = ['family_name']
    
    def __str__(self):
        return self.family_name

class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
        ('SEPARATED', 'Separated'),
    ]
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('VISITOR', 'Visitor'),
        ('NEW_MEMBER', 'New Member'),
        ('TRANSFERRED', 'Transferred'),
    ]

    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='members')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Church Information
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    membership_status = models.CharField(max_length=15, choices=MEMBERSHIP_STATUS_CHOICES, default='ACTIVE')
    membership_date = models.DateField(null=True, blank=True)
    cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True, blank=True)
    baptism_date = models.DateField(null=True, blank=True)
    confirmation_date = models.DateField(null=True, blank=True)
    
    # Additional Information
    photo = models.ImageField(upload_to='member_photos/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

class Event(models.Model):
    EVENT_TYPES = [
        ('SERVICE', 'Church Service'),
        ('MEETING', 'Meeting'),
        ('FELLOWSHIP', 'Fellowship'),
        ('OUTREACH', 'Outreach'),
        ('CONFERENCE', 'Conference'),
        ('OTHER', 'Other'),
    ]
    
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    attended = models.BooleanField(default=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['event', 'member']
        verbose_name_plural = "Attendance Records"
    
    def __str__(self):
        status = "Attended" if self.attended else "Absent"
        return f"{self.member} - {self.event} - {status}"

class Donation(models.Model):
    DONATION_TYPES = [
        ('TITHE', 'Tithe'),
        ('OFFERING', 'Offering'),
        ('BUILDING_FUND', 'Building Fund'),
        ('MISSIONS', 'Missions'),
        ('OTHER', 'Other'),
    ]
    
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('CARD', 'Credit/Debit Card'),
        ('ONLINE', 'Online'),
        ('OTHER', 'Other'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='donations')
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    donation_date = models.DateField(default=timezone.now)
    check_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.member} - ${self.amount} - {self.donation_date}"

class Sermon(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='sermons')
    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=200)
    bible_passage = models.CharField(max_length=100, blank=True)
    sermon_date = models.DateField()
    audio_file = models.FileField(upload_to='sermons/audio/', null=True, blank=True)
    video_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sermon_date']
    
    def __str__(self):
        return f"{self.title} - {self.sermon_date}"

class PrayerRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('ANSWERED', 'Answered'),
        ('CLOSED', 'Closed'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='prayer_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.member}"
    

# core/models.py
class Admin(models.Model):
    ADMIN_TYPE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('Cell', 'Cell'),
        ('MODERATOR', 'Moderator'),
    ]

    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='admin_profile')
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='admins')
    level = models.CharField(max_length=100, choices=ADMIN_TYPE_CHOICES, default='Cell')
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='cell_admins', null=True, blank=True)
    
    # Add user account specifically for admin access
    user_account = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='admin_account',
        null=True, 
        blank=True
    )
    
    def create_user_account(self, username=None, password=None):
        """Create user account for this admin"""
        if self.user_account:
            return self.user_account
        
        if not username:
            # Generate username from member name
            username = f"{self.member.first_name.lower()}.{self.member.last_name.lower()}"
            # Ensure uniqueness
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=self.member.email,
            password=password or self.member.first_name + "sepcam", 
            first_name=self.member.first_name,
            last_name=self.member.last_name
        )
        
        self.user_account = user
        self.save()
        return user
    

    def confirm_cell_membership(self):
        """Ensure the admin's member is part of the assigned cell"""
        if self.member.cell != self.cell:
            self.member.cell = self.cell
            self.member.save()
        return self.member.cell
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_user_account()
        self.confirm_cell_membership()

    @property
    def is_superadmin(self):
        return self.level == 'SUPERADMIN'
    
    @property
    def is_cell_admin(self):
        return self.level == 'Cell'
    
    @property
    def is_moderator(self):
        return self.level == 'MODERATOR'
    
    def can_access_member(self, member):
        """Check if admin can access a specific member based on cell assignment"""
        if self.is_superadmin:
            # Super admins can access all members in their assembly
            return member.assembly == self.assembly
        elif self.is_cell_admin and self.cell:
            # Cell admins can only access members in their specific cell
            return member.assembly == self.assembly and member.cell == self.cell
        elif self.is_moderator:
            # Moderators can access all members in their assembly
            return member.assembly == self.assembly
        return False
    
    def has_permission(self, permission_type):
        """Check if admin has specific permission based on level"""
        permission_map = {
            'manage_members': self.can_manage_members,
            'manage_finances': self.can_manage_finances and (self.is_superadmin or self.is_moderator),
            'manage_events': self.can_manage_events,
            'manage_content': self.can_manage_content and (self.is_superadmin or self.is_moderator),
            'access_all_cells': self.is_superadmin or self.is_moderator,
            'manage_users': self.is_superadmin,
            'system_config': self.is_superadmin,
        }
        
        if permission_type in permission_map:
            # If it's a callable, call it, otherwise return the value
            if callable(permission_map[permission_type]):
                return permission_map[permission_type]()
            return permission_map[permission_type]
        return False
    
    def get_managed_members(self):
        """Get members that this admin can manage"""
        if self.is_superadmin:
            return Member.objects.filter(assembly=self.assembly)
        elif self.is_cell_admin and self.cell:
            return Member.objects.filter(assembly=self.assembly, cell=self.cell)
        elif self.is_moderator:
            return Member.objects.filter(assembly=self.assembly)
        else:
            return Member.objects.none()
    
    def get_full_name(self):
        return self.member.get_full_name()
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.level} - {self.assembly.name}"