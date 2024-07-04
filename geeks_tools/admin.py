from django.contrib import admin
from geeks_tools.models import Category, Hashtag, User_tool, SetUp, ToolInfo, Subscription,Subcategory,Bookmark,CombinedTool,PopularSearch,Suggestion,BestTool,CsvTool
from .models import User
from django.contrib.auth import get_user_model
User = get_user_model()



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)



@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)



@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('text',)



@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)




@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('id', 'term', 'subcategories')
    search_fields = ('term', 'subcategories__name')
    list_filter = ('subcategories',)




@admin.register(User_tool)
class UserToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name','logo', 'url', 'intro', 'category', 'subcategory', 'display_hashtags', 'pricing', 'created_at')
    search_fields = ('name', 'user__username', 'category__name', 'subcategory__name')
    list_filter = ('category', 'subcategory', 'pricing', 'created_at')

    def display_hashtags(self, obj):
        return ", ".join([hashtag.term for hashtag in obj.hashtag.all()])
    display_hashtags.short_description = 'Hashtags'




@admin.register(SetUp)
class SetUpAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'package_name','features','Pricing','timeline']
    search_fields = ['package_name']
    list_filter = ['timeline']



@admin.register(ToolInfo)
class ToolInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'image1','image2','image2','agent', 'features', 'video',]
    search_fields = ['user__first_name', 'description', 'agent', 'features']


    
    


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_subscribed']
    list_filter = ['is_subscribed']
    search_fields = ['email']

admin.site.register(Subscription, SubscriptionAdmin)




# Optionally, create a custom admin class for CombinedTool
class CombinedToolAdmin(admin.ModelAdmin):
    list_display = ('id','user_tool', 'setup', 'tool_info', 'status','created_by','created_at')
    search_fields = ('user_tool__name', 'setup__package_name', 'tool_info__description')
    list_filter = ('status',)

admin.site.register(CombinedTool, CombinedToolAdmin)





class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'combined_tool_info', 'csv_tool_name', 'created_at')
    list_filter = ('user',)

    def combined_tool_info(self, obj):
        if obj.combined_tool:
            return f"CombinedTool ID: {obj.combined_tool.id}"
        else:
            return '-'

    def csv_tool_name(self, obj):
        return obj.csv_tool.name if obj.csv_tool else '-'

    combined_tool_info.short_description = 'Combined Tool'

admin.site.register(Bookmark, BookmarkAdmin)





@admin.register(BestTool)
class BestToolAdmin(admin.ModelAdmin):
    list_display = ('user','name', 'category', 'image', 'display_combined_tool')  # Customize fields displayed in list view
    list_filter = ('category',)  # Add filters for categories
    search_fields = ('name', 'description')  # Add search functionality for name and description
    filter_horizontal = ('combined_tool',)  # Add a horizontal filter for many-to-many field

   

    def display_combined_tool(self, obj):
        return ', '.join([ct.name for ct in obj.combined_tool.all()])

    display_combined_tool.short_description = 'Combined Tools' 





# Optional: Create a custom admin class to customize the admin interface
class CsvToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'category', 'subcategory', 'hashtag', 'intro', 'pricing','logo','image1', 'created_by', 'created_at')
    search_fields = ('name', 'category', 'subcategory', 'tag')
    list_filter = ('category', 'subcategory', 'created_at')
    readonly_fields = ('created_by',)

# Register the model with the custom admin class
admin.site.register(CsvTool, CsvToolAdmin)
