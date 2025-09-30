from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Assembly, Unit, Family, Member, Cell

class AssemblyForm(forms.ModelForm):
    class Meta:
        model = Assembly
        fields = [
            'name', 'description', 'founded_date', 'website', 'email', 'phone',
            'street_address', 'city', 'state', 'country', 'zip_code',
            'latitude', 'longitude', 'facebook_url', 'twitter_url',
            'instagram_url', 'youtube_url', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assembly name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter assembly description'
            }),
            'founded_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'assembly@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter country'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ZIP code'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'e.g., 40.7128'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'e.g., -74.0060'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/your-assembly'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/your-assembly'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/your-assembly'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/your-assembly'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'is_active': 'Is this assembly active?'
        }

    def clean_founded_date(self):
        founded_date = self.cleaned_data.get('founded_date')
        if founded_date and founded_date > timezone.now().date():
            raise ValidationError("Founded date cannot be in the future.")
        return founded_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValidationError("Phone number can only contain numbers, spaces, hyphens, and plus sign.")
        return phone


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'description', 'leader']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unit name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter unit description'
            }),
            'leader': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active members as potential leaders
        self.fields['leader'].queryset = Member.objects.filter(membership_status='ACTIVE')
        self.fields['leader'].required = False


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['assembly', 'family_name', 'address', 'phone', 'email']
        widgets = {
            'assembly': forms.Select(attrs={
                'class': 'form-control'
            }),
            'family_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter family name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter family address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'family@example.com'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValidationError("Phone number can only contain numbers, spaces, hyphens, and plus sign.")
        return phone


class CellForm(forms.ModelForm):
    class Meta:
        model = Cell
        fields = ['name', 'created_at']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter cell name'
            }),
            'created_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_created_at(self):
        created_at = self.cleaned_data.get('created_at')
        if created_at and created_at > timezone.now().date():
            raise ValidationError("Creation date cannot be in the future.")
        return created_at


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'assembly', 'first_name', 'last_name', 'middle_name', 
            'date_of_birth', 'gender', 'marital_status', 'family',
            'email', 'phone', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'unit', 'membership_status',
            'membership_date', 'cell', 'baptism_date', 'confirmation_date',
            'photo'
        ]
        widgets = {
            'assembly': forms.Select(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter middle name (optional)'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'family': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'member@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control'
            }),
            'membership_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'membership_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cell': forms.Select(attrs={
                'class': 'form-control'
            }),
            'baptism_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'confirmation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields not required for public registration
        self.fields['family'].required = False
        self.fields['unit'].required = False
        self.fields['cell'].required = False
        self.fields['membership_date'].required = False
        self.fields['baptism_date'].required = False
        self.fields['confirmation_date'].required = False
        self.fields['photo'].required = False
        self.fields['emergency_contact_name'].required = False
        self.fields['emergency_contact_phone'].required = False

        # Set initial membership status for new members
        if not self.instance.pk:
            self.fields['membership_status'].initial = 'NEW_MEMBER'

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
        return date_of_birth

    def clean_membership_date(self):
        membership_date = self.cleaned_data.get('membership_date')
        if membership_date and membership_date > timezone.now().date():
            raise ValidationError("Membership date cannot be in the future.")
        return membership_date

    def clean_baptism_date(self):
        baptism_date = self.cleaned_data.get('baptism_date')
        if baptism_date and baptism_date > timezone.now().date():
            raise ValidationError("Baptism date cannot be in the future.")
        return baptism_date

    def clean_confirmation_date(self):
        confirmation_date = self.cleaned_data.get('confirmation_date')
        if confirmation_date and confirmation_date > timezone.now().date():
            raise ValidationError("Confirmation date cannot be in the future.")
        return confirmation_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValidationError("Phone number can only contain numbers, spaces, hyphens, and plus sign.")
        return phone

    def clean_emergency_contact_phone(self):
        emergency_contact_phone = self.cleaned_data.get('emergency_contact_phone')
        if emergency_contact_phone and not emergency_contact_phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValidationError("Emergency contact phone number can only contain numbers, spaces, hyphens, and plus sign.")
        return emergency_contact_phone

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')
        membership_date = cleaned_data.get('membership_date')
        baptism_date = cleaned_data.get('baptism_date')
        confirmation_date = cleaned_data.get('confirmation_date')

        # Validate date order
        if date_of_birth and membership_date:
            if membership_date < date_of_birth:
                raise ValidationError({
                    'membership_date': 'Membership date cannot be before date of birth.'
                })

        if baptism_date and date_of_birth:
            if baptism_date < date_of_birth:
                raise ValidationError({
                    'baptism_date': 'Baptism date cannot be before date of birth.'
                })

        if confirmation_date and baptism_date:
            if confirmation_date < baptism_date:
                raise ValidationError({
                    'confirmation_date': 'Confirmation date cannot be before baptism date.'
                })

        return cleaned_data


class MemberPublicRegistrationForm(MemberForm):
    """Simplified form for public registration"""
    class Meta(MemberForm.Meta):
        fields = [
            'assembly', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'email', 'phone', 'address'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove fields not needed for public registration
        for field_name in list(self.fields.keys()):
            if field_name not in self.Meta.fields:
                del self.fields[field_name]

        # Make assembly field more prominent for public registration
        self.fields['assembly'].label = "Which assembly do you attend?"


class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['family']
        widgets = {
            'family': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class MemberFilterForm(forms.Form):
    """Form for filtering members in the dashboard"""
    assembly = forms.ModelChoiceField(
        queryset=Assembly.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'id': 'assemblyFilter'
        }),
        empty_label="All Assemblies"
    )
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'id': 'unitFilter'
        }),
        empty_label="All Units"
    )
    family = forms.ModelChoiceField(
        queryset=Family.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'id': 'familyFilter'
        }),
        empty_label="All Families"
    )
    cell = forms.ModelChoiceField(
        queryset=Cell.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'id': 'cellFilter'
        }),
        empty_label="All Cells"
    )
    membership_status = forms.ChoiceField(
        choices=[('', 'All Status')] + Member.MEMBERSHIP_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'id': 'statusFilter'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search members...',
            'id': 'memberSearch'
        })
    )


class BulkMemberUploadForm(forms.Form):
    """Form for bulk uploading members via CSV"""
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with member data. Required columns: first_name, last_name, email, assembly_id',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    assembly = forms.ModelChoiceField(
        queryset=Assembly.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select the assembly for all members in this upload'
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError("Please upload a CSV file.")
            # Check file size (max 5MB)
            if csv_file.size > 5 * 1024 * 1024:
                raise ValidationError("File size must be less than 5MB.")
        return csv_file


class DateRangeFilterForm(forms.Form):
    """Form for filtering by date range"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='From Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date cannot be after end date.")

        return cleaned_data


class MemberReportForm(DateRangeFilterForm):
    """Form for generating member reports"""
    REPORT_TYPE_CHOICES = [
        ('membership', 'Membership Report'),
        ('demographic', 'Demographic Report'),
        ('geographic', 'Geographic Report'),
        ('activity', 'Activity Report'),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        initial='membership'
    )
    assembly = forms.ModelChoiceField(
        queryset=Assembly.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="All Assemblies"
    )
    include_inactive = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include Inactive Members'
    )


# Custom form for quick member creation (simplified version)
class QuickMemberForm(forms.ModelForm):
    """Simplified form for quick member creation in modals"""
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone', 'assembly']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone'
            }),
            'assembly': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# Form for assigning multiple members to a family
class BulkFamilyAssignmentForm(forms.Form):
    family = forms.ModelChoiceField(
        queryset=Family.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Assign to Family"
    )
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '10'
        }),
        label="Select Members"
    )

    def __init__(self, *args, **kwargs):
        assembly = kwargs.pop('assembly', None)
        super().__init__(*args, **kwargs)
        
        if assembly:
            self.fields['family'].queryset = Family.objects.filter(assembly=assembly)
            self.fields['members'].queryset = Member.objects.filter(assembly=assembly)