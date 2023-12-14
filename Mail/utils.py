from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class MailManager():
    """Class to manage emails"""

    def __init__(self, user):
        self.user = user

    def send_email(self, subject, html_message, plain_message, from_email, to):
        """Sends an email"""
        send_mail(subject, plain_message, from_email,
                  [to], html_message=html_message)
        return True

    def send_email_with_template(self, subject, template, context, from_email, to):
        """Sends an email with a template"""
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, from_email,
                  [to], html_message=html_message)
        return True


def sendEmail(request, user, code):
    subject = 'Pssst! Your secret code is...'
    html_message = render_to_string(
        'auth/2fa_email.html', {'user': user, 'code': code})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to = user.email
    send_mail(subject, plain_message, from_email,
              [to], html_message=html_message)
    return HttpResponse('Email sent')
