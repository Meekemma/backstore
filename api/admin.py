from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import User
from .models import *


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'email', 'first_name', 'last_name', 'is_active','profile_picture', 'is_staff', 'is_superuser', 'is_verified', 'is_premium', 'get_groups_display', 'auth_provider']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    list_filter = ['is_premium', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','is_premium', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser','is_premium', 'groups'),
        }),
    )
    ordering = ('email',)

    def get_groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups_display.short_description = 'Groups'






class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'country', 'profile_picture', 'role', 'company', 'date_created', 'date_updated')
    search_fields = ('user__email', 'first_name', 'last_name', 'email')
    list_filter = ('role', 'date_created', 'date_updated')



class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id','name',)




class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user','code')  
    search_fields = ('user__first_name', 'user__last_name', 'code') 





# Register the CustomUser model with the CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(OneTimePassword, OneTimePasswordAdmin)
