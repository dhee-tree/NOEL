import random, string
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def authCodeGenerator():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def groupJoinCode():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def sendEmail(request, user, code):
    subject = 'Pssst! Your secret code is...'
    html_message = render_to_string('auth/2fa_email.html', {'user': user, 'code': code})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to = user.email
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return HttpResponse('Email sent')
