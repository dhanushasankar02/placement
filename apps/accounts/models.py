from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('company', 'Company'),
        ('officer', 'Placement Officer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def is_student(self):
        return self.role == 'student'

    def is_company(self):
        return self.role == 'company'

    def is_officer(self):
        return self.role == 'officer' or self.role == 'admin'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
