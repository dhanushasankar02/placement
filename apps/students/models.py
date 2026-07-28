from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    STATUS_CHOICES = (
        ('unplaced', 'Unplaced'),
        ('shortlisted', 'Shortlisted'),
        ('placed', 'Placed'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    batch_year = models.IntegerField()
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    phone = models.CharField(max_length=15, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    placement_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unplaced')

    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"

class Education(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='education_history')
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=250)
    passing_year = models.IntegerField()
    percentage_cgpa = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Certificate(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    credential_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return self.name
