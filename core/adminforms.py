from django import forms
from django.contrib.auth.models import User
from .models import Admin, Member, Assembly, Cell


class AdminForm(forms.ModelForm):
    """Form for creating and updating Admin instances - username/password auto-generated"""

    class Meta:
        model = Admin
        fields = ["member", "assembly", "level", "cell"]
        widgets = {
            "level": forms.Select(choices=Admin.ADMIN_TYPE_CHOICES),
            "cell": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        # Get the current user (super admin) from kwargs
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # Set up querysets with related data
        self.fields["member"].queryset = Member.objects.select_related(
            "assembly", "cell"
        )
        self.fields["assembly"].queryset = Assembly.objects.all()
        self.fields["cell"].queryset = Cell.objects.select_related("assembly")

        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        # Make cell field required only for cell admins in the form validation
        self.fields["cell"].required = False

        # Remove username and password fields since they're auto-generated
        # These fields are handled in the model's save() method

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        cell = cleaned_data.get("cell")
        member = cleaned_data.get("member")
        assembly = cleaned_data.get("assembly")

        # Validate that cell admins have a cell assigned
        if level == "Cell" and not cell:
            raise forms.ValidationError(
                {"cell": "Cell is required for Cell level administrators."}
            )

        # Validate that non-cell admins don't have cell assigned
        if level != "Cell" and cell:
            cleaned_data["cell"] = None

        # Validate member belongs to the selected assembly
        if member and assembly and member.assembly != assembly:
            raise forms.ValidationError(
                {
                    "member": f"Selected member belongs to {member.assembly.name}, not {assembly.name}."
                }
            )

        # Validate cell belongs to the selected assembly
        if cell and assembly and cell.assembly != assembly:
            raise forms.ValidationError(
                {
                    "cell": f"Selected cell belongs to {cell.assembly.name}, not {assembly.name}."
                }
            )

        # Check if member already has an admin profile
        if member and Admin.objects.filter(member=member).exists():
            # If we're updating an existing admin, allow it
            if not self.instance or not self.instance.pk:
                raise forms.ValidationError(
                    {"member": "This member already has an admin profile."}
                )

        return cleaned_data


class AdminCreationForm(AdminForm):
    """Form specifically for creating new Admin instances"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Additional validation for creation
        if (
            not self.current_user
            or not hasattr(self.current_user, "admin_account")
            or not self.current_user.admin_account.is_superadmin
        ):
            raise forms.ValidationError(
                "Only super admins can create new admin accounts."
            )


class AdminUpdateForm(AdminForm):
    """Form specifically for updating existing Admin instances"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For updates, member and assembly might be read-only depending on the current user's level
        if (
            self.current_user
            and hasattr(self.current_user, "admin_account")
            and not self.current_user.admin_account.is_superadmin
        ):
            # Non-super admins can only update certain fields
            self.fields["member"].disabled = True
            self.fields["assembly"].disabled = True
            self.fields["level"].disabled = True


class AdminLevelChangeForm(forms.ModelForm):
    """Simplified form for changing admin level only"""

    class Meta:
        model = Admin
        fields = ["level", "cell"]
        widgets = {
            "level": forms.Select(choices=Admin.ADMIN_TYPE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # Set cell queryset based on the admin's assembly
        if self.instance and self.instance.assembly:
            self.fields["cell"].queryset = Cell.objects.filter(
                assembly=self.instance.assembly
            )

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        # Only super admins can change admin levels
        if (
            not self.current_user
            or not hasattr(self.current_user, "admin_account")
            or not self.current_user.admin_account.is_superadmin
        ):
            raise forms.ValidationError("Only super admins can change admin levels.")

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        cell = cleaned_data.get("cell")

        # Validate that cell admins have a cell assigned
        if level == "Cell" and not cell:
            raise forms.ValidationError(
                {"cell": "Cell is required for Cell level administrators."}
            )

        # Validate that non-cell admins don't have cell assigned
        if level != "Cell" and cell:
            cleaned_data["cell"] = None

        return cleaned_data


class SuperAdminOnlyMixin:
    """Mixin to ensure only super admins can access the form"""

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # Check if current user is a super admin
        if (
            not self.current_user
            or not hasattr(self.current_user, "admin_account")
            or not self.current_user.admin_account.is_superadmin
        ):
            raise PermissionError("Only super administrators can perform this action.")


class SuperAdminCreationForm(SuperAdminOnlyMixin, AdminCreationForm):
    """Admin creation form that requires super admin privileges"""

    pass


class SuperAdminUpdateForm(SuperAdminOnlyMixin, AdminUpdateForm):
    """Admin update form that requires super admin privileges"""

    pass


class AdminFilterForm(forms.Form):
    """Form for filtering admin lists"""

    LEVEL_CHOICES = [("", "All Levels")] + Admin.ADMIN_TYPE_CHOICES

    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    assembly = forms.ModelChoiceField(
        queryset=Assembly.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    cell = forms.ModelChoiceField(
        queryset=Cell.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search by name..."}
        ),
    )
