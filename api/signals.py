
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from .models import *
from django_rest_passwordreset.signals import reset_password_token_created
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


User = get_user_model()




@receiver(post_save, sender=User)
def customer_Profile(sender, instance, created, *args, **kwargs):
    if created:
        # Ensure the necessary groups are created
        free_group, created = Group.objects.get_or_create(name='Free')
        premium_group, created = Group.objects.get_or_create(name='Premium')
        freemium_group, created = Group.objects.get_or_create(name='Freemium')
        
        # Add the user to the "Free" group by default
        instance.groups.add(free_group)

       
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
        )
        print('User Profile created for', instance.first_name)

        

@receiver(post_save, sender=User)
def update_Profile(sender, instance, created, *args, **kwargs):
    if not created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if created:
            print('User Profile was missing and has been created for existing user')
        else:
            profile.save()
            print('Profile updated!!!')






@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    
    # send an e-mail to the user
    custom_url_base = "https://geektools.vercel.app/change-password"
    context = {
        'current_user': reset_password_token.user,
        'first_name': reset_password_token.user.first_name,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(custom_url_base, reset_password_token.key)
    }


    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Reset Password For Account"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()