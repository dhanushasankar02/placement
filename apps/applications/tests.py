from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from apps.students.models import StudentProfile
from apps.companies.models import CompanyProfile
from apps.jobs.models import Job
from apps.applications.models import Application

User = get_user_model()

class ApplicationEmailNotificationTestCase(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='student',
            first_name='John',
            last_name='Doe',
            email='student@example.com',
            password='password123',
            role='student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            roll_number='ROLL001',
            department='CSE',
            course='B.Tech',
            batch_year=2026,
            cgpa=9.00
        )
        
        # Create company user
        self.company_user = User.objects.create_user(
            username='company',
            email='company@example.com',
            password='password123',
            role='company'
        )
        self.company_profile = CompanyProfile.objects.create(
            user=self.company_user,
            name='Test Corp',
            industry='Tech',
            contact_email='contact@testcorp.com'
        )
        
        # Create job
        self.job = Job.objects.create(
            company=self.company_profile,
            title='Software Engineer',
            description='A great job',
            location='Remote',
            salary_package='12 LPA',
            eligibility_criteria=8.00,
            application_deadline=timezone.now() + timedelta(days=5)
        )
        
        # Create application
        self.application = Application.objects.create(
            job=self.job,
            student=self.student_profile,
            status='applied'
        )

    def test_shortlist_sends_email(self):
        # Log in as company user
        self.client.login(username='company', password='password123')
        
        # Clear outbox
        mail.outbox = []
        
        # Post to change status to shortlisted
        response = self.client.post(
            reverse('applications:application_status', kwargs={'pk': self.application.pk}),
            data={
                'status': 'shortlisted',
                'feedback': 'Good profile.'
            }
        )
        
        # Check redirect
        self.assertRedirects(response, reverse('applications:application_detail', kwargs={'pk': self.application.pk}))
        
        # Refresh from database
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'shortlisted')
        
        # Verify that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "Congratulations! You have been shortlisted")
        self.assertIn("Dear John Doe", sent_email.body)
        self.assertIn("Software Engineer", sent_email.body)
        self.assertEqual(sent_email.to, [self.student_user.email])

    def test_update_without_changing_status_does_not_send_email(self):
        # Log in as company user
        self.client.login(username='company', password='password123')
        
        # Clear outbox
        mail.outbox = []
        
        # Post to change feedback but keep status as applied
        response = self.client.post(
            reverse('applications:application_status', kwargs={'pk': self.application.pk}),
            data={
                'status': 'applied',
                'feedback': 'Under review.'
            }
        )
        
        # Refresh from database
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')
        
        # Verify that no email was sent
        self.assertEqual(len(mail.outbox), 0)

