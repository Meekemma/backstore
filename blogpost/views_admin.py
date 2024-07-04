from django.shortcuts import render
from rest_framework import status
import  io
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import Group
from blogpost.serializers_admin import AdminPostSerializer,PopularPostSerializer,BlogCategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from blogpost.models import *
import pandas as pd





@api_view(['GET'])
def admin_category(request):
    category=BlogCategory.objects.all()
    serializer=BlogCategorySerializer(category, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_posts(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = AdminPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_post_by_id(request, pk):
    try:
        post = Post.objects.get(id=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AdminPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([FormParser, MultiPartParser])
def create_post(request):
    if request.method == 'POST':
        try:
            form_data = request.data
            image = request.FILES.get('image')
            blog_category_data = json.loads(request.data.get('blog_category', '[]'))

            data = {
                'title': form_data.get('title'),
                'content': form_data.get('content'),
                'status': form_data.get('status'),
                'image': image,
                'blog_category': blog_category_data
            }

            serializer = AdminPostSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


    
@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
@parser_classes([FormParser, MultiPartParser])
def update_post(request, pk):
    try:
        post = Post.objects.get(id=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method in ['PUT', 'PATCH']:
        try:
            form_data = request.data
            image = request.FILES.get('image')
            blog_category_data = json.loads(request.data.get('blog_category', '{}'))

            data = {
                'title': form_data.get('title'),
                'content': form_data.get('content'),
                'status': form_data.get('status'),
                'image': image if image else post.image,
                'blog_category': blog_category_data
            }

            serializer = AdminPostSerializer(post, data=data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'details': 'Blog post updated successfully'}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        post.delete()
        return Response({'details': 'Blog post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)




# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def admin_all_posts(request):
#     draft_post= Post.objects.all()
#     serializer = AdminPostSerializer(draft_post, many=True)
#     return Response(serializer.data)



# @api_view(['GET', 'PUT'])
# @permission_classes([IsAdminUser])
# def admin_all_posts(request, pk):
#     post= Post.objects.get(id=pk)
#     serializer = AdminPostSerializer(post, many=True)
#     return Response(serializer.data)





@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def manage_popular_posts(request):
    if request.method == 'GET':
        popular_posts = PopularPost.objects.all()
        serializer = PopularPostSerializer(popular_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PopularPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_popular_post_status(request, pk):
    try:
        popular_post = PopularPost.objects.get(pk=pk)
    except PopularPost.DoesNotExist:
        return Response({'error': 'Popular post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PopularPostSerializer(popular_post, data=request.data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





