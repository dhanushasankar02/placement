from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.students.models import StudentProfile
from apps.companies.models import CompanyProfile
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.interviews.models import Interview
from django.db.models import Count, Q
from django.utils import timezone

@login_required
def dashboard_home(request):
    user = request.user
    if user.role == 'student':
        return student_dashboard(request)
    elif user.role == 'company':
        return company_dashboard(request)
    elif user.role in ['officer', 'admin']:
        return admin_dashboard(request)
    return redirect('accounts:login')

@login_required
def student_dashboard(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    apps = Application.objects.filter(student=student)
    applied_count = apps.count()
    shortlisted_count = apps.filter(status='shortlisted').count()
    selected_count = apps.filter(status='selected').count()
    
    upcoming_interviews = Interview.objects.filter(
        application__student=student,
        interview_date__gte=timezone.now(),
        status='scheduled'
    ).order_by('interview_date')[:5]
    
    recent_applications = apps.order_by('-applied_at')[:5]
    
    # Latest jobs eligible for student
    eligible_jobs = Job.objects.filter(
        is_active=True,
        eligibility_criteria__lte=student.cgpa,
        application_deadline__gte=timezone.now()
    ).exclude(applications__student=student).order_by('-created_at')[:5]

    context = {
        'student': student,
        'applied_count': applied_count,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
        'upcoming_interviews': upcoming_interviews,
        'recent_applications': recent_applications,
        'eligible_jobs': eligible_jobs,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def company_dashboard(request):
    try:
        company = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    jobs = Job.objects.filter(company=company)
    active_jobs_count = jobs.filter(is_active=True).count()
    
    total_apps = Application.objects.filter(job__company=company)
    total_apps_count = total_apps.count()
    pending_apps_count = total_apps.filter(status='applied').count()
    shortlisted_count = total_apps.filter(status='shortlisted').count()
    
    recent_apps = total_apps.order_by('-applied_at')[:5]
    
    upcoming_interviews = Interview.objects.filter(
        application__job__company=company,
        interview_date__gte=timezone.now(),
        status='scheduled'
    ).order_by('interview_date')[:5]

    context = {
        'company': company,
        'active_jobs_count': active_jobs_count,
        'total_apps_count': total_apps_count,
        'pending_apps_count': pending_apps_count,
        'shortlisted_count': shortlisted_count,
        'recent_applications': recent_apps,
        'upcoming_interviews': upcoming_interviews,
    }
    return render(request, 'dashboard/company_dashboard.html', context)

@login_required
def admin_dashboard(request):
    # Placement Officer or Admin view
    student_count = StudentProfile.objects.count()
    placed_count = StudentProfile.objects.filter(placement_status='placed').count()
    unplaced_count = StudentProfile.objects.filter(placement_status='unplaced').count()
    
    company_count = CompanyProfile.objects.count()
    job_count = Job.objects.count()
    active_job_count = Job.objects.filter(is_active=True).count()
    application_count = Application.objects.count()
    
    placement_rate = 0
    if student_count > 0:
        placement_rate = round((placed_count / student_count) * 100, 2)
        
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_applications = Application.objects.order_by('-applied_at')[:5]
    
    context = {
        'student_count': student_count,
        'placed_count': placed_count,
        'unplaced_count': unplaced_count,
        'company_count': company_count,
        'job_count': job_count,
        'active_job_count': active_job_count,
        'application_count': application_count,
        'placement_rate': placement_rate,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
    }
    # User requested placement_officer_dashboard.html too. Let's render the admin one.
    return render(request, 'dashboard/admin_dashboard.html', context)
