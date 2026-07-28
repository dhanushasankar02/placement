from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Application
from apps.jobs.models import Job
from apps.students.models import StudentProfile
from .forms import ApplicationForm, ApplicationStatusForm
from apps.notifications.models import Notification

@login_required
def application_list(request):
    if request.user.role == 'student':
        student = request.user.student_profile
        applications = Application.objects.filter(student=student)
    elif request.user.role == 'company':
        company = request.user.company_profile
        applications = Application.objects.filter(job__company=company)
    else:
        applications = Application.objects.all()
        
    return render(request, 'applications/application_list.html', {'applications': applications})

@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    # Check permissions
    if request.user.role == 'student' and application.student != request.user.student_profile:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    elif request.user.role == 'company' and application.job.company != request.user.company_profile:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    form = ApplicationStatusForm(instance=application)
    return render(request, 'applications/application_detail.html', {'application': application, 'form': form})

@login_required
def application_create(request, job_id):
    if request.user.role != 'student':
        messages.error(request, "Only students can apply for jobs.")
        return redirect('jobs:job_detail', pk=job_id)
        
    student = request.user.student_profile
    job = get_object_or_404(Job, pk=job_id)
    
    # Check eligibility
    if student.cgpa < job.eligibility_criteria:
        messages.error(request, f"You do not meet the minimum eligibility CGPA of {job.eligibility_criteria} for this job.")
        return redirect('jobs:job_detail', pk=job_id)
        
    # Check if already applied
    if Application.objects.filter(student=student, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', pk=job_id)
        
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.student = student
            app.job = job
            # Use profile resume if not uploaded specifically
            if not app.resume:
                app.resume = student.resume
            app.save()
            
            # Notify Recruiter/Company
            Notification.objects.create(
                user=job.company.user,
                title="New Job Application Received",
                message=f"Student {student.user.get_full_name()} has applied for your job post: {job.title}."
            )
            
            messages.success(request, "Application submitted successfully.")
            return redirect('applications:application_history')
    else:
        form = ApplicationForm(initial={'resume': student.resume})
        
    return render(request, 'applications/application_create.html', {'form': form, 'job': job})

@login_required
def application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    # Only company or admin can change status
    if request.user.role == 'company' and application.job.company != request.user.company_profile:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        old_status = application.status
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save()
            
            # Update student placement status if selected
            if app.status == 'selected':
                app.student.placement_status = 'placed'
                app.student.save()
            elif app.status == 'shortlisted':
                app.student.placement_status = 'shortlisted'
                app.student.save()
                
            # Send Notification to Student
            Notification.objects.create(
                user=app.student.user,
                title="Application Status Updated",
                message=f"Your application status for {app.job.title} has been updated to {app.get_status_display()}.",
            )
            
            # Send Email to Student if status is changed to shortlisted
            if app.status == 'shortlisted' and old_status != 'shortlisted':
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = "Congratulations! You have been shortlisted"
                message = f"Dear {app.student.user.get_full_name()},\n\nWe are pleased to inform you that your application for {app.job.title} has been shortlisted. Please check your calendar for scheduled interview rounds."
                
                recipient_list = [app.student.user.email]
                if recipient_list[0]:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        recipient_list,
                        fail_silently=True,
                    )
            
            messages.success(request, f"Application status updated to {app.get_status_display()}.")
            return redirect('applications:application_detail', pk=application.pk)
            
    return redirect('applications:application_detail', pk=application.pk)

@login_required
def application_history(request):
    if request.user.role != 'student':
        return redirect('applications:application_list')
    student = request.user.student_profile
    applications = Application.objects.filter(student=student).order_by('-applied_at')
    return render(request, 'applications/application_history.html', {'applications': applications})

@login_required
def shortlisted_view(request):
    if request.user.role == 'company':
        apps = Application.objects.filter(job__company=request.user.company_profile, status='shortlisted')
    else:
        apps = Application.objects.filter(status='shortlisted')
    return render(request, 'applications/shortlisted.html', {'applications': apps})

@login_required
def rejected_view(request):
    if request.user.role == 'company':
        apps = Application.objects.filter(job__company=request.user.company_profile, status='rejected')
    else:
        apps = Application.objects.filter(status='rejected')
    return render(request, 'applications/rejected.html', {'applications': apps})

@login_required
def selected_view(request):
    if request.user.role == 'company':
        apps = Application.objects.filter(job__company=request.user.company_profile, status='selected')
    else:
        apps = Application.objects.filter(status='selected')
    return render(request, 'applications/selected.html', {'applications': apps})
