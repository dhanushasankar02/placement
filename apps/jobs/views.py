from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Job, SavedJob
from apps.companies.models import CompanyProfile
from apps.students.models import StudentProfile
from .forms import JobForm

@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by eligibility if student
    if request.user.role == 'student':
        student = getattr(request.user, 'student_profile', None)
        if student:
            eligible_only = request.GET.get('eligible')
            if eligible_only:
                jobs = jobs.filter(eligibility_criteria__lte=student.cgpa)
                
    # Search filter
    q = request.GET.get('q')
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(company__name__icontains=q) | jobs.filter(skills_required__icontains=q)
        
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    is_saved = False
    is_eligible = True
    
    if request.user.role == 'student':
        student = getattr(request.user, 'student_profile', None)
        if student:
            has_applied = job.applications.filter(student=student).exists()
            is_saved = SavedJob.objects.filter(student=student, job=job).exists()
            is_eligible = student.cgpa >= job.eligibility_criteria
            
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'is_eligible': is_eligible,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def job_create(request):
    if request.user.role not in ['company', 'admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            if request.user.role == 'company':
                job.company = request.user.company_profile
            else:
                # admin/officer must select a company or default to first
                job.company = CompanyProfile.objects.first()
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request, 'jobs/job_create.html', {'form': form})

@login_required
def job_update(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user.role == 'company' and job.company != request.user.company_profile:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_update.html', {'form': form, 'job': job})

@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user.role == 'company' and job.company != request.user.company_profile:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('jobs:job_list')
    return render(request, 'jobs/job_delete.html', {'job': job})

@login_required
def my_jobs(request):
    if request.user.role == 'company':
        jobs = Job.objects.filter(company=request.user.company_profile)
    else:
        jobs = Job.objects.all()
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})

@login_required
def search_jobs(request):
    return redirect('jobs:job_list')

@login_required
def job_categories(request):
    # Basic landing for classifications
    jobs = Job.objects.filter(is_active=True)
    full_time = jobs.filter(job_type='full_time')
    internships = jobs.filter(job_type='internship')
    part_time = jobs.filter(job_type='part_time')
    context = {
        'full_time': full_time,
        'internships': internships,
        'part_time': part_time,
    }
    return render(request, 'jobs/job_categories.html', context)

@login_required
def save_job_view(request, pk):
    if request.user.role != 'student':
        messages.error(request, "Only students can save jobs.")
        return redirect('jobs:job_detail', pk=pk)
        
    student = request.user.student_profile
    job = get_object_or_404(Job, pk=pk)
    
    saved_job, created = SavedJob.objects.get_or_create(student=student, job=job)
    if not created:
        saved_job.delete()
        messages.success(request, "Job removed from saved list.")
    else:
        messages.success(request, "Job saved successfully.")
        
    return redirect('jobs:job_detail', pk=pk)

@login_required
def saved_jobs(request):
    if request.user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    student = request.user.student_profile
    saved = SavedJob.objects.filter(student=student)
    return render(request, 'jobs/saved_jobs.html', {'saved': saved})
