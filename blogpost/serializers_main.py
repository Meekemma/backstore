from rest_framework import serializers
from django.utils import timezone
from django.core.validators import EmailValidator
from blogpost.models import *

from django.contrib.auth import get_user_model
User = get_user_model()



class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields= ('id', 'name')
        read_only_fields = ['id']
         
#Post Serializer
class PostSerializer(serializers.ModelSerializer):
    blog_category= BlogCategorySerializer()
    class Meta:
        model = Post
        fields = ['id', 'title',  'content', 'status', 'image','blog_category', 'created_on', 'updated_on']
        read_only_fields = ['id','created_on', 'updated_on'] 