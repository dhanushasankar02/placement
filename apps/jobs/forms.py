from django import forms
from apps.jobs.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'skills_required', 'location', 'job_type', 'salary_package', 'eligibility_criteria', 'application_deadline', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, SQL, Git'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'salary_package': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10 LPA'}),
            'eligibility_criteria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 7.5'}),
            'application_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
