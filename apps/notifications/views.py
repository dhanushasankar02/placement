from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Notification, SentEmail

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

@login_required
def unread_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return render(request, 'notifications/unread_notifications.html', {'notifications': notifications})

@login_required
def email_templates(request):
    # Dummy placeholder view
    return render(request, 'notifications/email_templates.html')

@login_required
def webmail(request):
    user = request.user
    User = get_user_model()
    
    # Students can only view their own emails
    if user.role == 'student':
        emails = SentEmail.objects.filter(recipient=user.email).order_by('-sent_at')
        email_list = None
        selected_email = user.email
    else:
        # Recruiters, officers, admins can view any student's email inbox
        students = User.objects.filter(role='student').order_by('username')
        selected_email = request.GET.get('email', '')
        
        # Default to Sam Jarvis email if not chosen
        if not selected_email:
            sam_user = User.objects.filter(email='samjarvis890@gmail.com').first()
            if sam_user:
                selected_email = sam_user.email
            elif students.exists():
                selected_email = students.first().email
                
        emails = SentEmail.objects.filter(recipient=selected_email).order_by('-sent_at')
        email_list = [{'email': u.email, 'name': u.get_full_name() or u.username} for u in students]

    # Handle viewing a specific email content in the detail pane
    active_email_id = request.GET.get('id')
    active_email = None
    if active_email_id:
        active_email = emails.filter(pk=active_email_id).first()
    if not active_email and emails.exists():
        active_email = emails.first()

    context = {
        'emails': emails,
        'selected_email': selected_email,
        'email_list': email_list,
        'active_email': active_email,
    }
    return render(request, 'notifications/webmail.html', context)

