from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from decouple import config


class MailManager():
    """Class to manage and send emails"""
    def __init__(self, email):
        self.email = email
        self.frontend_url = getattr(settings, 'FRONTEND_URL', None)
        self.from_email = settings.EMAIL_HOST_USER

    def ping_user_address(self, group):
        """Sends an email to pinged a user"""
        user = User.objects.get(email=self.email)
        subject = 'Santa wants your address!'
        html_message = render_to_string('mail/ping_address.html', {'group': group, 'user': user, 'frontend_url': self.frontend_url})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = self.email
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
        
    def ping_user_wishlist(self, group):
        """Sends an email to pinged a user to update their wishlist"""
        user = User.objects.get(email=self.email)
        subject = 'Santa wants to see your wishlist!'
        html_message = render_to_string('mail/ping_wishlist.html', {'group': group, 'user': user, 'frontend_url': self.frontend_url})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = self.email
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False

    def send_verification_email(self, first_name, verification_code):
        """Sends an email to verify a user"""
        subject = 'Verify your email'
        html_message = render_to_string('mail/verify_email.html', {'verification_code': verification_code, 'first_name': first_name, 'frontend_url': self.frontend_url})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = self.email
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
        
    def send_contact_message(self, name, message):
        """Sends an email to the admin with a contact message"""
        subject = 'Contact message from {}'.format(name)
        html_message = render_to_string('mail/contact_message.html', {'name': name, 'message': message, 'email': self.email})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = config('ADMIN_EMAIL')
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
        
    def send_reset_password_email(self, name=None, uid=None, token=None):
        """Sends an email to reset a user's password using uid/token or a full reset link.

        This function no longer supports the legacy `uuid`/`verification_code` flow.
        """
        subject = 'Reset your password'
        reset_link = self.frontend_url + f'/reset-password/confirm?uid={uid}&token={token}'

        context = {'name': name, 'reset_link': reset_link}

        html_message = render_to_string('mail/reset_password.html', context)
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = self.email
        try:
            send_mail(subject, plain_message, from_email,
                      [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
        
    
    def send_reset_password_confirm_email(self, name):
        """Sends an email to confirm a user's password reset"""
        subject = 'Password reset successful'
        html_message = render_to_string('mail/reset_password_confirm.html', {'name': name, 'frontend_url': self.frontend_url})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = self.email
        try:
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
