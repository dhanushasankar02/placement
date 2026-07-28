from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Interview
from apps.applications.models import Application
from .forms import InterviewForm
from apps.notifications.models import Notification

@login_required
def interview_list(request):
    if request.user.role == 'student':
        interviews = Interview.objects.filter(application__student=request.user.student_profile).order_by('-interview_date')
    elif request.user.role == 'company':
        interviews = Interview.objects.filter(application__job__company=request.user.company_profile).order_by('-interview_date')
    else:
        interviews = Interview.objects.all().order_by('-interview_date')
    return render(request, 'interviews/interview_list.html', {'interviews': interviews})

@login_required
def interview_schedule(request, app_id=None):
    if request.user.role not in ['company', 'admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    application = None
    if app_id:
        application = get_object_or_404(Application, pk=app_id)
        
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            if application:
                interview.application = application
            else:
                # select application from post arguments
                app_pk = request.POST.get('application')
                interview.application = get_object_or_404(Application, pk=app_pk)
            interview.save()
            
            # Notify student
            Notification.objects.create(
                user=interview.application.student.user,
                title="New Interview Scheduled",
                message=f"Recruiter scheduled an interview '{interview.round_name}' on {interview.interview_date}."
            )
            
            messages.success(request, "Interview scheduled successfully.")
            return redirect('interviews:interview_list')
    else:
        form = InterviewForm()
        
    context = {'form': form, 'application': application}
    if not application:
        # fetch eligible applicants
        if request.user.role == 'company':
            context['applications'] = Application.objects.filter(job__company=request.user.company_profile, status='shortlisted')
        else:
            context['applications'] = Application.objects.filter(status='shortlisted')
            
    return render(request, 'interviews/interview_schedule.html', context)

@login_required
def interview_detail(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
    return render(request, 'interviews/interview_detail.html', {'interview': interview})

@login_required
def interview_result(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
    if request.user.role not in ['company', 'admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        result = request.POST.get('result')
        feedback = request.POST.get('feedback')
        status = request.POST.get('status', 'completed')
        
        interview.result = result
        interview.feedback = feedback
        interview.status = status
        interview.save()
        
        # Notify student
        Notification.objects.create(
            user=interview.application.student.user,
            title="Interview Result Declared",
            message=f"Result for your interview round '{interview.round_name}' is: {interview.get_result_display()}."
        )
        
        messages.success(request, "Interview results updated.")
        return redirect('interviews:interview_detail', pk=pk)
        
    return render(request, 'interviews/interview_result.html', {'interview': interview})

@login_required
def interview_feedback(request, pk):
    return redirect('interviews:interview_result', pk=pk)

@login_required
def interview_calendar(request):
    # Renders interview_calendar
    if request.user.role == 'student':
        interviews = Interview.objects.filter(application__student=request.user.student_profile, status='scheduled')
    elif request.user.role == 'company':
        interviews = Interview.objects.filter(application__job__company=request.user.company_profile, status='scheduled')
    else:
        interviews = Interview.objects.filter(status='scheduled')
    return render(request, 'interviews/interview_calendar.html', {'interviews': interviews})
