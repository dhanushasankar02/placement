from django.db import models
from django.conf import settings
from apps.companies.models import CompanyProfile
from apps.students.models import StudentProfile

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('internship', 'Internship'),
        ('part_time', 'Part-time'),
    )
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True, help_text="Additional job requirements")
    skills_required = models.TextField(blank=True, help_text="Comma-separated list of required skills")
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    salary_package = models.CharField(max_length=50, help_text="e.g. 12 LPA, 50,000/month")
    eligibility_criteria = models.DecimalField(max_digits=4, decimal_places=2, default=0.00, help_text="Minimum required CGPA")
    application_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_skills_list(self):
        if self.skills_required:
            return [s.strip() for s in self.skills_required.split(',') if s.strip()]
        return []

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class SavedJob(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_students')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student} saved {self.job.title}"
