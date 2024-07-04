from django.contrib import admin
from django.contrib import admin
from blogpost.models import BlogCategory,PopularPost,Post
from .models import User
from django.contrib.auth import get_user_model
User = get_user_model()


# Register your models here.
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user','blog_category','title', 'image','status', 'created_on', 'updated_on')
    list_filter = ('status', 'created_on', 'updated_on')
    search_fields = ('title', 'content')


@admin.register(PopularPost)
class PopularPostAdmin(admin.ModelAdmin):
    list_display = ('user','post','status', 'created_on', 'updated_on')
    list_filter = ('status', 'created_on', 'updated_on')
    search_fields = ('title', 'content')