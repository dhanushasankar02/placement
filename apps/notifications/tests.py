from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import SentEmail

User = get_user_model()

class WebmailTests(TestCase):
    def setUp(self):
        # Create student and company users
        self.student_user = User.objects.create_user(
            username='sam_student', 
            email='samjarvis890@gmail.com', 
            password='password123',
            role='student'
        )
        self.company_user = User.objects.create_user(
            username='tamil_recruiter', 
            email='growwpark@gmail.com', 
            password='password123',
            role='company'
        )
        
    from unittest.mock import patch

    @override_settings(EMAIL_BACKEND='apps.notifications.email_backend.DatabaseEmailBackend')
    @patch('django.core.mail.backends.smtp.EmailBackend.send_messages')
    def test_database_email_backend_logs_emails(self, mock_send_messages):
        mock_send_messages.return_value = 1
        # Send an email using Django's send_mail
        send_mail(
            subject='Test Subject',
            message='Test Body',
            from_email='placement@example.com',
            recipient_list=['samjarvis890@gmail.com']
        )
        
        # Verify it was logged in the SentEmail model
        logged_emails = SentEmail.objects.filter(recipient='samjarvis890@gmail.com')
        self.assertEqual(logged_emails.count(), 1)
        self.assertEqual(logged_emails.first().subject, 'Test Subject')
        self.assertEqual(logged_emails.first().body, 'Test Body')

    def test_student_can_view_own_webmail(self):
        # Log in as student
        self.client.login(username='sam_student', password='password123')
        
        # Log an email
        SentEmail.objects.create(
            recipient='samjarvis890@gmail.com',
            subject='Shortlisted!',
            body='You have been shortlisted'
        )
        
        # Get webmail page
        response = self.client.get(reverse('notifications:webmail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shortlisted!')
        
    def test_recruiter_can_view_student_webmail(self):
        # Log in as company recruiter
        self.client.login(username='tamil_recruiter', password='password123')
        
        # Log an email
        SentEmail.objects.create(
            recipient='samjarvis890@gmail.com',
            subject='Shortlisted!',
            body='You have been shortlisted'
        )
        
        # Get webmail page
        response = self.client.get(reverse('notifications:webmail') + '?email=samjarvis890@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shortlisted!')
