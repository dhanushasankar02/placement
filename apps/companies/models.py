from django.db import models
from django.conf import settings

class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_profile')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
