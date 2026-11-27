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
            
            # Send Email to Student
            student_user = interview.application.student.user
            if student_user.email:
                from django.core.mail import send_mail
                from django.conf import settings

                student_name = student_user.get_full_name() or student_user.username
                job_title = interview.application.job.title
                company_name = interview.application.job.company.name
                round_name = interview.round_name
                round_num = interview.round_number
                formatted_date = interview.interview_date.strftime("%B %d, %Y at %I:%M %p") if hasattr(interview.interview_date, 'strftime') else str(interview.interview_date)
                location = interview.location_or_link

                subject = f"Interview Scheduled: {round_name} - {job_title}"
                message = (
                    f"Dear {student_name},\n\n"
                    f"Your interview for the position of {job_title} at {company_name} has been scheduled.\n\n"
                    f"Interview Details:\n"
                    f"• Round: Round {round_num} ({round_name})\n"
                    f"• Date & Time: {formatted_date}\n"
                    f"• Venue / Meeting Link: {location}\n"
                    f"• Status: {interview.get_status_display()}\n"
                )
                if interview.feedback:
                    message += f"• Notes: {interview.feedback}\n"

                message += (
                    f"\nPlease ensure you are available on time. You can check the placement portal for further updates and interview details.\n\n"
                    f"Best regards,\n"
                    f"{company_name} / Placement Team"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student_user.email],
                    fail_silently=True,
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
        
        # Send Email to Student
        student_user = interview.application.student.user
        if student_user.email:
            from django.core.mail import send_mail
            from django.conf import settings

            student_name = student_user.get_full_name() or student_user.username
            job_title = interview.application.job.title
            company_name = interview.application.job.company.name

            subject = f"Interview Result Declared: {interview.round_name} - {job_title}"
            message = (
                f"Dear {student_name},\n\n"
                f"The result for your interview round '{interview.round_name}' for the position of {job_title} at {company_name} has been declared.\n\n"
                f"Result: {interview.get_result_display()}\n"
            )
            if interview.feedback:
                message += f"Feedback: {interview.feedback}\n"

            message += (
                f"\nPlease check your placement portal for more details and next steps.\n\n"
                f"Best regards,\n"
                f"{company_name} / Placement Team"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student_user.email],
                fail_silently=True,
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
