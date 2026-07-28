from django import forms
from apps.applications.models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Introduce yourself and state why you are a good fit for this role...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
