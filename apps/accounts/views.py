from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from .forms import StudentSignUpForm, CompanySignUpForm, UserLoginForm

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    role = request.GET.get('role', 'student')
    if role == 'company':
        if request.method == 'POST':
            form = CompanySignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Recruiter account registered successfully!")
                return redirect('dashboard:home')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = CompanySignUpForm()
    else:
        role = 'student'
        if request.method == 'POST':
            form = StudentSignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Student account registered successfully!")
                return redirect('dashboard:home')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = StudentSignUpForm()
            
    return render(request, 'accounts/register.html', {'form': form, 'role': role})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    if user.is_student():
        context['profile'] = getattr(user, 'student_profile', None)
    elif user.is_company():
        context['profile'] = getattr(user, 'company_profile', None)
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    user = request.user
    if user.is_student():
        from apps.students.forms import StudentProfileForm
        profile = getattr(user, 'student_profile', None)
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('accounts:profile')
        else:
            form = StudentProfileForm(instance=profile)
    elif user.is_company():
        from apps.companies.forms import CompanyProfileForm
        profile = getattr(user, 'company_profile', None)
        if request.method == 'POST':
            form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Company profile updated successfully.")
                return redirect('accounts:profile')
        else:
            form = CompanyProfileForm(instance=profile)
    else:
        # Officer/Admin
        form = None
        
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

def forgot_password_view(request):
    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request):
    return render(request, 'accounts/reset_password.html')

def verify_email_view(request):
    return render(request, 'accounts/verify_email.html')
