from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from apps.students.models import StudentProfile
from apps.companies.models import CompanyProfile

User = get_user_model()

class StudentSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    roll_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    course = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    batch_year = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                department=self.cleaned_data['department'],
                course=self.cleaned_data['course'],
                batch_year=self.cleaned_data['batch_year'],
                cgpa=self.cleaned_data['cgpa'],
                phone=self.cleaned_data['phone']
            )
        return user

class CompanySignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    company_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    industry = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'company'
        if commit:
            user.save()
            CompanyProfile.objects.create(
                user=user,
                name=self.cleaned_data['company_name'],
                website=self.cleaned_data['website'],
                industry=self.cleaned_data['industry'],
                contact_phone=self.cleaned_data['contact_phone'],
                contact_email=self.cleaned_data['contact_email'],
                address=self.cleaned_data['address']
            )
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
