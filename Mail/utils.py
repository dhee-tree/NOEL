from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from decouple import config
from django.core.signing import TimestampSigner
from django.core.mail import EmailMultiAlternatives

FRONTEND_URL = getattr(settings, 'FRONTEND_URL', None)


def get_unsubscribe_url(user):
    signer = TimestampSigner()
    signed_id = signer.sign(user.id)
    return f"{FRONTEND_URL}/email-preferences?token={signed_id}"


# Valid for 30 days
def get_user_from_preference_token(token, max_age=60*60*24*30):
    signer = TimestampSigner()
    try:
        user_id = signer.unsign(token, max_age=max_age)
        return User.objects.get(pk=user_id)
    except Exception:
        return None


class MailManager():
    """Class to manage and send emails"""

    def __init__(self, user):
        self.user = user
        self.email = user.email
        self.from_email = settings.EMAIL_HOST_USER

    def ping_user_address(self, group):
        """Sends an email to pinged a user"""
        subject = 'Santa wants your address!'
        context = {'group': group, 'user': self.user,
                   'frontend_url': FRONTEND_URL}
        template_name = 'mail/ping_address.html'

        try:
            self.send_transactional_email(
                self.user,
                subject,
                template_name,
                context
            )
            return True
        except Exception as e:
            print(e)
            return False

    def ping_user_wishlist(self, group):
        """Sends an email to pinged a user to update their wishlist"""
        subject = 'Santa wants to see your wishlist!'
        context = {'group': group, 'user': self.user,
                   'frontend_url': FRONTEND_URL}
        template_name = 'mail/ping_wishlist.html'

        try:
            self.send_transactional_email(
                self.user,
                subject,
                template_name,
                context
            )
            return True
        except Exception as e:
            print(e)
            return False

    def send_verification_email(self, first_name, verification_code):
        """Sends an email to verify a user"""
        subject = 'Verify your email'
        context = {'verification_code': verification_code,
                   'first_name': first_name, 'frontend_url': FRONTEND_URL}
        template_name = 'mail/verify_email.html'
        try:
            self.send_transactional_email(
                self.user,
                subject,
                template_name,
                context
            )
            return True
        except Exception as e:
            print(e)
            return False

    def send_reset_password_email(self, name=None, uid=None, token=None):
        """Sends an email to reset a user's password using uid/token or a full reset link.

        This function no longer supports the legacy `uuid`/`verification_code` flow.
        """
        subject = 'Reset your password'
        reset_link = FRONTEND_URL + \
            f'/reset-password/confirm?uid={uid}&token={token}'
        template_name = 'mail/reset_password.html'
        context = {'name': name, 'reset_link': reset_link}

        try:
            self.send_transactional_email(
                self.user,
                subject,
                template_name,
                context
            )
            return True
        except Exception as e:
            print(e)
            return False

    def send_reset_password_confirm_email(self, name):
        """Sends an email to confirm a user's password reset"""
        subject = 'Password reset successful'
        template_name = 'mail/reset_password_confirm.html'
        context = {'name': name, 'frontend_url': FRONTEND_URL}
        try:
            self.send_transactional_email(
                self.user,
                subject,
                template_name,
                context
            )
            return True
        except Exception as e:
            print(e)
            return False

    def send_marketing_email(self, user, subject, message):
        if not hasattr(user, 'communication_preferences'):
            return

        if not user.communication_preferences.allow_marketing:
            print(
                f"Skipping marketing email for {self.email} - User opted out.")
            return

        send_mail(
            subject,
            message,
            self.from_email,
            [self.email],
            fail_silently=False,
        )

    def send_transactional_email(self, user, subject, template_name, context):
        magic_link = get_unsubscribe_url(user)

        context['unsubscribe_url'] = magic_link

        html_content = render_to_string(template_name, context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body="Please enable HTML to view this email.",
            from_email=self.from_email,
            to=[self.email],
        )
        msg.attach_alternative(html_content, "text/html")

        msg.extra_headers = {
            "List-Unsubscribe": f"<{magic_link}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"
        }

        msg.send()

    ## Admin emails ##
    def send_contact_message(self, name, message, subject=None):
        """Sends an email to the admin with a contact message

        Args:
            name: sender name
            message: message body
            subject: optional subject line provided by sender
        """
        subject_header = subject if subject else f'Contact message from {name}'
        html_message = render_to_string('mail/contact_message.html', {
                                        'name': name, 'message': message, 'email': self.email, 'subject': subject})
        plain_message = strip_tags(html_message)
        from_email = self.from_email
        to = config('ADMIN_EMAIL')
        try:
            send_mail(subject_header, plain_message, from_email,
                      [to], html_message=html_message)
            return True
        except Exception as e:
            print(e)
            return False
