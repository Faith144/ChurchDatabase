from django import forms
from .models import Admin, Member, Assembly, Cell


class AdminForm(forms.ModelForm):
    """Form for creating and updating Admin instances"""

    class Meta:
        model = Admin
        fields = ["member", "assembly", "level", "cell"]
        widgets = {
            "level": forms.Select(choices=Admin.ADMIN_TYPE_CHOICES),
            "assembly": forms.Select(attrs={"class": "form-control"}),
            "cell": forms.Select(attrs={"class": "form-control"}),
            "member": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # Set up querysets - remove invalid select_related
        self.fields["member"].queryset = Member.objects.all()
        self.fields["assembly"].queryset = Assembly.objects.all()
        self.fields["cell"].queryset = Cell.objects.all()

        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name != "level":  # level already has choices
                field.widget.attrs["class"] = "form-control"

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

        # Check if member already has an admin profile (only for new admins)
        if member and not self.instance.pk:
            if Admin.objects.filter(member=member).exists():
                raise forms.ValidationError(
                    {"member": "This member already has an admin profile."}
                )

        return cleaned_data


class AdminLevelChangeForm(forms.ModelForm):
    """Form for changing admin level only"""

    class Meta:
        model = Admin
        fields = ["level", "cell"]
        widgets = {
            "level": forms.Select(choices=Admin.ADMIN_TYPE_CHOICES),
            "cell": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name != "level":
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        cell = cleaned_data.get("cell")

        # Validate that cell admins have a cell assigned
        if level == "Cell" and not cell:
            raise forms.ValidationError(
                {"cell": "Cell is required for Cell level administrators."}
            )

        return cleaned_data


class AdminFilterForm(forms.Form):
    """Form for filtering admin lists"""

    LEVEL_CHOICES = [("", "All Levels")] + Admin.ADMIN_TYPE_CHOICES

    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
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
