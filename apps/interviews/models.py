from django.db import models
from apps.applications.models import Application

class Interview(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    RESULT_CHOICES = (
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('rejected', 'Rejected'),
    )
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateTimeField()
    location_or_link = models.CharField(max_length=255, help_text="Online link or physical location")
    round_number = models.IntegerField(default=1)
    round_name = models.CharField(max_length=100, help_text="e.g. Technical Round 1, HR Interview")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(blank=True, null=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')

    def __str__(self):
        return f"Round {self.round_number}: {self.round_name} for {self.application.student.user.get_full_name()}"
