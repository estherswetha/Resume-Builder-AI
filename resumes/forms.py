
from django import forms
from .models import Resume, BuilderResume


# ==========================================================
# 1. EXISTING AI RESUME GENERATOR FORM
# ==========================================================

class ResumeForm(forms.ModelForm):

    class Meta:
        model = Resume

        fields = [
            "full_name",
            "email",
            "phone",
            "location",
            "target_role",
            "education",
            "skills",
            "experience",
            "projects",
            "certifications",
            "professional_summary",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Enter your email address",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "+91 9876543210",
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "City, Country",
            }),
            "target_role": forms.Select(),
            "education": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Degree, college, graduation year, marks...",
            }),
            "skills": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Python, Django, SQL, HTML, CSS...",
            }),
            "experience": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Company, role, duration, responsibilities...",
            }),
            "projects": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Project name, technologies and description...",
            }),
            "certifications": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Certification name and organization...",
            }),
            "professional_summary": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Enter your professional summary...",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


# ==========================================================
# 2. SMART RESUME BUILDER FORM
# ==========================================================

class BuilderResumeForm(forms.ModelForm):

    class Meta:
        model = BuilderResume

        fields = [
            "title",
            "career_level",
            "full_name",
            "email",
            "phone",
            "location",
            "linkedin",
            "portfolio",
            "github",
            "target_role",
            "professional_summary",
            "education",
            "experience",
            "skills",
            "projects",
            "certifications",
            "job_description",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "My Professional Resume",
            }),
            "career_level": forms.Select(),
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Enter your email address",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "+91 9876543210",
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "Chennai, India",
            }),
            "linkedin": forms.URLInput(attrs={
                "placeholder": "https://linkedin.com/in/your-profile",
            }),
            "portfolio": forms.URLInput(attrs={
                "placeholder": "https://yourportfolio.com",
            }),
            "github": forms.URLInput(attrs={
                "placeholder": "https://github.com/yourusername",
            }),
            "target_role": forms.TextInput(attrs={
                "placeholder": "Python Developer",
            }),
            "professional_summary": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write your professional summary...",
            }),
            "education": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Degree | College | Year | CGPA",
            }),
            "experience": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Company | Job title | Dates | Responsibilities",
            }),
            "skills": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Python, Django, HTML, CSS, SQL...",
            }),
            "projects": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Project name | Technologies | Your contribution",
            }),
            "certifications": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Certification name | Issuing organization",
            }),
            "job_description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Paste the target job description for ATS analysis...",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

        required_fields = [
            "full_name",
            "email",
            "target_role",
            "education",
            "skills",
        ]

        for field_name in required_fields:
            self.fields[field_name].required = True

        optional_fields = [
            "title",
            "career_level",
            "phone",
            "location",
            "linkedin",
            "portfolio",
            "github",
            "professional_summary",
            "experience",
            "projects",
            "certifications",
            "job_description",
        ]

        for field_name in optional_fields:
            self.fields[field_name].required = False

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        return email.lower()

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "").strip()

        if not full_name:
            raise forms.ValidationError(
                "Please enter your full name."
            )

        return full_name
