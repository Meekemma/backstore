from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
# from .tasks import revert_to_freemium
def update_combined_tool(instance, created, **kwargs):
    user = instance.user
    try:
        # Ensure only one draft CombinedTool exists per user
        combined_tool = CombinedTool.objects.filter(user=user, status='draft').first()

        if not combined_tool or combined_tool.user_tool and combined_tool.tool_info and  combined_tool.setup:
            # Create a new CombinedTool if no draft exists
            combined_tool = CombinedTool.objects.create(
                user=user,
                user_tool=None,
                setup=None,
                tool_info=None,
                status='draft'
            )

    
        # Update the CombinedTool with the new instance
        if isinstance(instance, User_tool):
            combined_tool.user_tool = instance
        elif isinstance(instance, SetUp):
            combined_tool.setup = instance
        elif isinstance(instance, ToolInfo):
            combined_tool.tool_info = instance

        # Update the status based on completion
        is_admin = user.is_staff  

        # Update the status based on completion and user type
        if is_admin:
            combined_tool.status = 'publish'
        else:
            if combined_tool.user_tool and combined_tool.tool_info:
                combined_tool.status = 'publish'
            else:
                combined_tool.status = 'draft'

        combined_tool.save()

    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error: {e}")

# Connect the post_save signal to the update_combined_tool function for each model
@receiver(post_save, sender=User_tool)
def user_tool_saved(sender, instance, created, **kwargs):
    update_combined_tool(instance, created, **kwargs)

@receiver(post_save, sender=SetUp)
def setup_saved(sender, instance, created, **kwargs):
    update_combined_tool(instance, created, **kwargs)

@receiver(post_save, sender=ToolInfo)
def tool_info_saved(sender, instance, created, **kwargs):
    update_combined_tool(instance, created, **kwargs)












# @receiver(post_save, sender=User_tool)
# def handle_premium_pricing(sender, instance, **kwargs):
#     if instance.pricing == 'Premium':
#         # Schedule the task to revert to 'Freemium' in 5 minutes
#         revert_to_freemium(instance.id)

