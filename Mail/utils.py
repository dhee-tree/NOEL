from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.template.loader import render_to_string


class MailManager():
    """Class to manage and send emails"""
    def __init__(self, email):
        self.email = email

    def ping_user_email(self, group):
        """Sends an email to pinged a user"""
        user = User.objects.get(email=self.email)
        subject = 'Santa wants your address!'
        html_message = render_to_string('mail/ping_email.html', {'group': group, 'user': user})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = self.email
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
