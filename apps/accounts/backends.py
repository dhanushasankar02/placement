from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class FlexibleAuthBackend(ModelBackend):
    """
    Allows authentication using:
    - Exact username
    - Case-insensitive username
    - Username with spaces removed (e.g. 'Groww park' -> 'growwpark')
    - Email address (e.g. 'growwpark@gmail.com')
    - Company profile name (e.g. 'Groww Park')
    - Student profile roll number (e.g. '12' or 'C22UG219CAP008')
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        identifier = username.strip()
        cleaned_identifier = identifier.replace(" ", "")

        query = (
            Q(username__iexact=identifier) |
            Q(username__iexact=cleaned_identifier) |
            Q(email__iexact=identifier) |
            Q(company_profile__name__iexact=identifier) |
            Q(company_profile__name__iexact=cleaned_identifier) |
            Q(student_profile__roll_number__iexact=identifier)
        )
        
        users = User.objects.filter(query).distinct()
        for user in users:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        return None
