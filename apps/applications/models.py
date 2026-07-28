from django.db import models
from apps.jobs.models import Job
from apps.students.models import StudentProfile

class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_letter = models.TextField(blank=True)
    feedback = models.TextField(blank=True, help_text="Feedback from the recruiter")

    class Meta:
        unique_together = ('job', 'student')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.job.title}"
