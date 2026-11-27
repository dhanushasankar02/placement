import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from apps.students.models import StudentProfile
from apps.companies.models import CompanyProfile
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.interviews.models import Interview

@login_required
def reports_home(request):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    return render(request, 'reports/reports.html')

@login_required
def placement_report(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    export = request.GET.get('export')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="placement_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Name', 'Department', 'Course', 'CGPA', 'Placement Status'])
        for s in StudentProfile.objects.all():
            writer.writerow([s.roll_number, s.user.get_full_name(), s.department, s.course, s.cgpa, s.get_placement_status_display()])
        return response
        
    students = StudentProfile.objects.all()
    return render(request, 'reports/placement_report.html', {'students': students})

@login_required
def student_report(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    export = request.GET.get('export')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Name', 'Email', 'Batch', 'CGPA'])
        for s in StudentProfile.objects.all():
            writer.writerow([s.roll_number, s.user.get_full_name(), s.user.email, s.batch_year, s.cgpa])
        return response
        
    students = StudentProfile.objects.all()
    return render(request, 'reports/student_report.html', {'students': students})

@login_required
def company_report(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    export = request.GET.get('export')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="company_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Company Name', 'Industry', 'Website', 'Email', 'Jobs Posted'])
        for c in CompanyProfile.objects.annotate(job_count=Count('jobs')):
            writer.writerow([c.name, c.industry, c.website, c.contact_email, c.job_count])
        return response
        
    companies = CompanyProfile.objects.annotate(job_count=Count('jobs'))
    return render(request, 'reports/company_report.html', {'companies': companies})

@login_required
def job_report(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    export = request.GET.get('export')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="job_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Job Title', 'Company', 'Location', 'Package', 'Min CGPA Criteria', 'Applications Count'])
        for j in Job.objects.annotate(app_count=Count('applications')):
            writer.writerow([j.title, j.company.name, j.location, j.salary_package, j.eligibility_criteria, j.app_count])
        return response
        
    jobs = Job.objects.annotate(app_count=Count('applications'))
    return render(request, 'reports/job_report.html', {'jobs': jobs})

@login_required
def interview_report(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    export = request.GET.get('export')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="interview_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Job Title', 'Company', 'Round', 'Date', 'Status', 'Result'])
        for i in Interview.objects.all():
            writer.writerow([
                i.application.student.user.get_full_name(),
                i.application.job.title,
                i.application.job.company.name,
                i.round_name,
                i.interview_date,
                i.get_status_display(),
                i.get_result_display()
            ])
        return response
        
    interviews = Interview.objects.all()
    return render(request, 'reports/interview_report.html', {'interviews': interviews})

@login_required
def analytics_view(request):
    if request.user.role not in ['admin', 'officer']:
        return redirect('dashboard:home')
        
    total_students = StudentProfile.objects.count()
    placed_students = StudentProfile.objects.filter(placement_status='placed').count()
    unplaced_students = StudentProfile.objects.filter(placement_status='unplaced').count()
    shortlisted_students = StudentProfile.objects.filter(placement_status='shortlisted').count()
    
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    total_interviews = Interview.objects.count()
    
    average_cgpa = StudentProfile.objects.aggregate(Avg('cgpa'))['cgpa__avg'] or 0.00
    average_cgpa = round(average_cgpa, 2)
    
    # department breakdown
    dept_stats = StudentProfile.objects.values('department').annotate(
        total=Count('id'),
        placed=Count('id', filter=Q(placement_status='placed'))
    )
    
    dept_stats = list(dept_stats)
    for d in dept_stats:
        d['placed_rate'] = round((d['placed'] / d['total']) * 100, 1) if d['total'] > 0 else 0
        
    placement_rate = round((placed_students / total_students) * 100, 1) if total_students > 0 else 0
    
    context = {
        'total_students': total_students,
        'placed_students': placed_students,
        'unplaced_students': unplaced_students,
        'shortlisted_students': shortlisted_students,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_interviews': total_interviews,
        'average_cgpa': average_cgpa,
        'dept_stats': dept_stats,
        'placement_rate': placement_rate,
    }
    return render(request, 'reports/analytics.html', context)
