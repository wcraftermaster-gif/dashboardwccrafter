import resend
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    """Backend de correo que envia via la API HTTP de Resend,
    en vez de SMTP (bloqueado en el plan free de Render)."""

    def __init__(self, api_key=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = api_key
        if self.api_key:
            resend.api_key = self.api_key

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                resend.Emails.send({
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.body,
                })
                sent_count += 1
            except Exception:
                if not self.fail_silently:
                    raise
        return sent_count