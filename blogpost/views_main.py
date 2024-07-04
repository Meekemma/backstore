from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from blogpost.serializers_main import PostSerializer 
from blogpost.serializers_admin import PopularPostSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
User = get_user_model()
from blogpost.models import *






@api_view(['GET'])
def blog_post(request, post_id=None):
    if post_id is not None:
        try:
            post = Post.objects.get(id=post_id, status='Publish')
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        posts = Post.objects.filter(status='Publish')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def similar_blog_view(request, category_id):
    try:
        category = BlogCategory.objects.get(pk=category_id)
    except BlogCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    posts = Post.objects.filter(blog_category=category, status='Publish')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)






@api_view(['GET'])
def get_all_popular_posts(request):
    popular_posts = PopularPost.objects.all()
    serializer = PopularPostSerializer(popular_posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_popular_post(request, pk):
    try:
        popular_post = PopularPost.objects.get(pk=pk)
    except PopularPost.DoesNotExist:
        return Response({'error': 'Popular post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PopularPostSerializer(popular_post)
    return Response(serializer.data, status=status.HTTP_200_OK)




class UserPostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title']