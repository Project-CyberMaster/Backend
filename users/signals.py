from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.dispatch import receiver
import random


User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.delete()


@receiver(reset_password_token_created)
def send_otp_email(sender, instance, reset_password_token, *args, **kwargs):
    """
    Sends an email containing an OTP code for password reset.
    """

    otp_code = str(random.randint(100000, 999999))  

    # Override the token key with our OTP code
    reset_password_token.key = otp_code  
    reset_password_token.save()

    email_message = f"""
    Hello {reset_password_token.user.username},

    You requested to reset your password.

    🔑 Your OTP code: {otp_code}

    If you did not request this password reset, please ignore this email.

    Best regards,  
    The Support Team
    """

    send_mail(
        subject="🔑 Password Reset - OTP Code",
        message=email_message,
        from_email="moncefzabat37@gmail.com",  
        recipient_list=[reset_password_token.user.email],  
        fail_silently=False
    )

