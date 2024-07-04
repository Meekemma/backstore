from rest_framework import serializers
from django.utils import timezone
from django.core.validators import EmailValidator
from blogpost.models import *

from django.contrib.auth import get_user_model
User = get_user_model()


from rest_framework import serializers



class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name']
        read_only_fields = ['id']

class AdminPostSerializer(serializers.ModelSerializer):
    blog_category = BlogCategorySerializer()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'status', 'image', 'blog_category', 'created_on', 'updated_on']
        read_only_fields = ['id', 'created_on', 'updated_on']

    def create(self, validated_data):
        blog_category_data = validated_data.pop('blog_category')
        user = self.context['request'].user
        
        # Create or get the BlogCategory instance
        blog_category, created = BlogCategory.objects.get_or_create(**blog_category_data)
        
        # Create the Post instance and associate it with the BlogCategory
        post = Post.objects.create(user=user, blog_category=blog_category, **validated_data)
        
        return post

    def update(self, instance, validated_data):
        blog_category_data = validated_data.pop('blog_category', None)

        # Update or create the BlogCategory instance if data is provided
        if blog_category_data is not None:
            blog_category, created = BlogCategory.objects.get_or_create(**blog_category_data)
            instance.blog_category = blog_category

        # Update the Post fields
        for attr, value in validated_data.items():
            if attr == 'image' and value is None:
                continue  # Skip updating the image if it is None
            setattr(instance, attr, value)
        instance.save()
        
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['blog_category'] = BlogCategorySerializer(instance.blog_category).data
        return representation






class PopularPostSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = PopularPost
        fields = ['id', 'post', 'status', 'created_on', 'updated_on']
        read_only_fields = ['id', 'created_on', 'updated_on']

    def create(self, validated_data):
        user = self.context['request'].user
        return PopularPost.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        instance.post = validated_data.get('post', instance.post)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance




