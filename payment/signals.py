from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Payment
from geeks_tools.models import CombinedTool
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def handle_unique_transaction(sender, instance, created, *args, **kwargs):
    # Check if the transaction is newly created
    if created:
        user = instance.user
        
        # Check if the user is already a premium member
        # if user.is_premium:
        #     logger.warning(f"User {user.email} is already a premium member. Payment {instance.stripe_payment_intent_id} will not be processed.")
        #     return  # Do not process if the user is already a premium member
        
        # Proceed with processing the transaction
        if instance.status == 'succeeded':
            # Mark the user as a premium member
            user.is_premium = True
            user.save()

            # Add the user to the Premium group
            premium_group, created = Group.objects.get_or_create(name='Premium')
            user.groups.add(premium_group)

            amount = instance.amount_received
            email = user.email
            domain = "GeeksTool.com"
            email_subject = "Successful Payment for the Premium Plan"
            email_message = f"The sum of {amount} {instance.currency} was made and you are now a Premium user for {domain}"

            try:
                send_email = EmailMessage(
                    email_subject,
                    email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                send_email.send(fail_silently=False)
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")





# @receiver(post_save, sender=Payment)
# def update_combined_tool(sender, instance, created, **kwargs):
#     if instance.status == 'succeeded':
#         user = instance.user
#         # Update CombinedTool instances for this user
#         CombinedTool.objects.filter(user=user).update(created_by='premium_user')