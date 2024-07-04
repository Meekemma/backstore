# from background_task import background
# from .models import User_tool

# @background(schedule=300)  # 300 seconds = 5 minutes
# def revert_to_freemium(user_tool_id):
#     try:
#         user_tool = User_tool.objects.get(pk=user_tool_id)
#         user_tool.pricing = 'Freemium'
#         user_tool.save()
#     except User_tool.DoesNotExist:
#         pass