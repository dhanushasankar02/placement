from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from apps.students.models import StudentProfile
from apps.companies.models import CompanyProfile
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.notifications.models import Notification, SentEmail

User = get_user_model()

class InterviewEmailNotificationTestCase(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='student_sam',
            first_name='Sam',
            last_name='Jarvis',
            email='samjarvis890@gmail.com',
            password='password123',
            role='student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            roll_number='14',
            department='CSE',
            course='B.Tech',
            batch_year=2026,
            cgpa=8.50
        )
        
        # Create company user
        self.company_user = User.objects.create_user(
            username='growwpark',
            email='growwpark@gmail.com',
            password='password123',
            role='company'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.company_user,
            name='Groww Park',
            industry='FinTech',
            contact_email='growwpark@gmail.com'
        )
        
        # Create job
        self.job = Job.objects.create(
            company=self.company_profile,
            title='Python Backend Developer',
            description='Django backend developer role',
            location='Bangalore',
            salary_package='10 LPA',
            eligibility_criteria=7.50,
            application_deadline=timezone.now() + timedelta(days=10)
        )
        
        # Create application (shortlisted)
        self.application = Application.objects.create(
            job=self.job,
            student=self.student_profile,
            status='shortlisted'
        )

    def test_schedule_interview_sends_email_to_student(self):
        self.client.login(username='growwpark', password='password123')
        mail.outbox = []

        interview_time = (timezone.now() + timedelta(days=2)).replace(microsecond=0)
        formatted_input_time = interview_time.strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(
            reverse('interviews:interview_schedule_app', kwargs={'app_id': self.application.pk}),
            data={
                'interview_date': formatted_input_time,
                'location_or_link': 'https://meet.google.com/abc-defg-hij',
                'round_number': 1,
                'round_name': 'Technical Interview Round 1',
                'status': 'scheduled',
                'result': 'pending',
                'feedback': 'Please be ready with a Python coding IDE.'
            }
        )

        self.assertRedirects(response, reverse('interviews:interview_list'))

        # Check interview created in database
        interview = Interview.objects.filter(application=self.application).first()
        self.assertIsNotNone(interview)
        self.assertEqual(interview.round_name, 'Technical Interview Round 1')

        # Check in-app notification
        notification = Notification.objects.filter(user=self.student_user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, 'New Interview Scheduled')

        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.student_user.email])
        self.assertIn("Interview Scheduled: Technical Interview Round 1 - Python Backend Developer", sent_email.subject)
        self.assertIn("Dear Sam Jarvis", sent_email.body)
        self.assertIn("Python Backend Developer", sent_email.body)
        self.assertIn("Groww Park", sent_email.body)
        self.assertIn("Round 1 (Technical Interview Round 1)", sent_email.body)
        self.assertIn("https://meet.google.com/abc-defg-hij", sent_email.body)
        self.assertIn("Please be ready with a Python coding IDE.", sent_email.body)

    def test_schedule_interview_general_form_sends_email_to_student(self):
        # Testing schedule view without app_id in URL (application selected via POST data)
        self.client.login(username='growwpark', password='password123')
        mail.outbox = []

        interview_time = (timezone.now() + timedelta(days=3)).replace(microsecond=0)
        formatted_input_time = interview_time.strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(
            reverse('interviews:interview_schedule'),
            data={
                'application': self.application.pk,
                'interview_date': formatted_input_time,
                'location_or_link': 'Office Campus, 3rd Floor',
                'round_number': 2,
                'round_name': 'HR Round',
                'status': 'scheduled',
                'result': 'pending',
                'feedback': 'Bring original certificates.'
            }
        )

        self.assertRedirects(response, reverse('interviews:interview_list'))

        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.student_user.email])
        self.assertIn("HR Round", sent_email.subject)
        self.assertIn("Office Campus, 3rd Floor", sent_email.body)
        self.assertIn("Bring original certificates.", sent_email.body)

    def test_interview_result_update_sends_email_to_student(self):
        self.client.login(username='growwpark', password='password123')
        interview = Interview.objects.create(
            application=self.application,
            interview_date=timezone.now() + timedelta(days=1),
            location_or_link='Online',
            round_number=1,
            round_name='Technical Round',
            status='scheduled',
            result='pending'
        )

        mail.outbox = []

        response = self.client.post(
            reverse('interviews:interview_result', kwargs={'pk': interview.pk}),
            data={
                'result': 'cleared',
                'feedback': 'Excellent problem solving skills.',
                'status': 'completed'
            }
        )

        self.assertRedirects(response, reverse('interviews:interview_detail', kwargs={'pk': interview.pk}))

        # Refresh interview
        interview.refresh_from_db()
        self.assertEqual(interview.result, 'cleared')
        self.assertEqual(interview.status, 'completed')

        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.student_user.email])
        self.assertIn("Interview Result Declared: Technical Round", sent_email.subject)
        self.assertIn("Cleared", sent_email.body)
        self.assertIn("Excellent problem solving skills.", sent_email.body)

    @override_settings(EMAIL_BACKEND='apps.notifications.email_backend.DatabaseEmailBackend')
    @patch('django.core.mail.backends.smtp.EmailBackend.send_messages')
    def test_schedule_interview_logs_in_database_email_backend(self, mock_send_messages):
        mock_send_messages.return_value = 1
        self.client.login(username='growwpark', password='password123')

        interview_time = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
        formatted_input_time = interview_time.strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(
            reverse('interviews:interview_schedule_app', kwargs={'app_id': self.application.pk}),
            data={
                'interview_date': formatted_input_time,
                'location_or_link': 'Zoom Link',
                'round_number': 1,
                'round_name': 'Coding Round',
                'status': 'scheduled',
                'result': 'pending',
                'feedback': ''
            }
        )

        self.assertRedirects(response, reverse('interviews:interview_list'))

        # Verify entry created in SentEmail model
        logged = SentEmail.objects.filter(recipient=self.student_user.email)
        self.assertTrue(logged.exists())
        email_record = logged.order_by('-sent_at').first()
        self.assertIn("Interview Scheduled: Coding Round", email_record.subject)
        self.assertIn("Dear Sam Jarvis", email_record.body)
