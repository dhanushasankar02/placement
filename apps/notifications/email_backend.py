from django.core.mail.backends.smtp import EmailBackend as SmtpEmailBackend
from .models import SentEmail

class DatabaseEmailBackend(SmtpEmailBackend):
    def send_messages(self, email_messages):
        if email_messages:
            for message in email_messages:
                for recipient in message.recipients():
                    SentEmail.objects.create(
                        recipient=recipient,
                        subject=message.subject,
                        body=message.body
                    )
        try:
            return super().send_messages(email_messages)
        except Exception:
            if not self.fail_silently:
                raise
            return 0
