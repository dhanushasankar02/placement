from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CompanyProfile
from apps.jobs.models import Job
from apps.applications.models import Application
from .forms import CompanyProfileForm

@login_required
def company_list(request):
    companies = CompanyProfile.objects.all()
    query = request.GET.get('q')
    if query:
        companies = companies.filter(name__icontains=query) | companies.filter(industry__icontains=query)
    return render(request, 'companies/company_list.html', {'companies': companies})

@login_required
def company_detail(request, pk):
    company = get_object_or_404(CompanyProfile, pk=pk)
    jobs = company.jobs.filter(is_active=True)
    return render(request, 'companies/company_detail.html', {'company': company, 'jobs': jobs})

@login_required
def company_create(request):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Company created successfully.")
            return redirect('companies:company_list')
    else:
        form = CompanyProfileForm()
    return render(request, 'companies/company_create.html', {'form': form})

@login_required
def company_update(request, pk):
    company = get_object_or_404(CompanyProfile, pk=pk)
    if request.user.role == 'company' and request.user.company_profile != company:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated.")
            return redirect('companies:company_detail', pk=company.pk)
    else:
        form = CompanyProfileForm(instance=company)
    return render(request, 'companies/company_update.html', {'form': form, 'company': company})

@login_required
def company_delete(request, pk):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    company = get_object_or_404(CompanyProfile, pk=pk)
    if request.method == 'POST':
        company.user.delete() # Deletes user and company profile cascades
        messages.success(request, "Company profile deleted.")
        return redirect('companies:company_list')
    return render(request, 'companies/company_delete.html', {'company': company})

@login_required
def company_profile(request):
    try:
        company = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        messages.error(request, "Create company profile first.")
        return redirect('accounts:edit_profile')
    return render(request, 'companies/company_profile.html', {'company': company})

@login_required
def company_jobs(request):
    try:
        company = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
    jobs = company.jobs.all()
    return render(request, 'companies/company_jobs.html', {'jobs': jobs})

@login_required
def company_students(request):
    try:
        company = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
    applications = Application.objects.filter(job__company=company)
    return render(request, 'companies/company_students.html', {'applications': applications})
