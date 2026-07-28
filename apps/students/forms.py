from django import forms
from apps.students.models import StudentProfile, Education, Certificate

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['phone', 'department', 'course', 'batch_year', 'cgpa']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SkillsForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['skills']
        widgets = {
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, SQL, React'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'passing_year', 'percentage_cgpa']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'passing_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_cgpa': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'issuing_organization', 'issue_date', 'credential_url', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
