from django.shortcuts import render
from rest_framework import status
import  io
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny,IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.contrib.auth.models import Group
from geeks_tools.serializers_admin import AdminCategorySerializer,AdminSubcategorySerializer,AdminHashtagSerializer,AdminPopularSearchSerializer,AdminSuggestionSerializer,AdminCombinedToolSerializer,CsvToolSerializer
from geeks_tools.serializers_main import CombinedToolSerializer,BestToolSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from geeks_tools.models import *
import pandas as pd




#ADMINISTRATION USERS VIEW


@api_view(['GET'])
@permission_classes([IsAdminUser])
def categoriesList(request):
    categories = Category.objects.all()
    serializer = AdminCategorySerializer(categories, many=True)
    return Response(serializer.data)




@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def createHashtag(request):
    if request.method == 'GET':
        hashtag = Hashtag.objects.all()
        serializer = AdminHashtagSerializer(hashtag, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminHashtagSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def sub_category_view(request):
    if request.method == 'GET':
        sub_category=Subcategory.objects.all()
        serializer = AdminSubcategorySerializer(sub_category, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminSubcategorySerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'sub category created successfully'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def update_subcategory_view(request, pk):
    try:
        sub_category = Subcategory.objects.get(id=pk)
    except Subcategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = AdminSubcategorySerializer(sub_category, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Subcategory updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sub_category.delete()
        return Response({'message': 'Subcategory deleted successfully'}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def hashtag_view(request):
    if request.method == 'GET':
        hash_tag=Hashtag.objects.all()
        serializer = AdminHashtagSerializer(hash_tag, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminHashtagSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'hashtag created successfully'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)





@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def update_hashtag_view(request, pk):
    try:
        hashtag = Hashtag.objects.get(pk=pk)
    except Hashtag.DoesNotExist:
        return Response({'error': 'Hashtag not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = AdminHashtagSerializer(hashtag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Hashtag updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        hashtag.delete()
        return Response({'message': 'Hashtag deleted successfully'}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
@parser_classes([FormParser, MultiPartParser])
def popular_search(request):
    if request.method == 'GET':
        popular_search = PopularSearch.objects.all()
        serializer = AdminPopularSearchSerializer(popular_search, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminPopularSearchSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
@parser_classes([FormParser, MultiPartParser])
def update_popular_search(request, pk):
    try:
        popular_search = PopularSearch.objects.get(id=pk)
    except PopularSearch.DoesNotExist:
        return Response({'error': 'Popular search not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = AdminPopularSearchSerializer(popular_search, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Popular search updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        popular_search.delete()
        return Response({'message': 'Popular deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def suggestions(request):
    if request.method == 'GET':
        suggestion = Suggestion.objects.all()
        serializer = AdminSuggestionSerializer(suggestion, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminSuggestionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def update_suggestion(request, pk):
    try:
        suggestion = Suggestion.objects.get(id=pk)
    except Suggestion.DoesNotExist:
        return Response({'error': 'Popular search not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = AdminSuggestionSerializer(suggestion, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'suggestion search updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        suggestion.delete()
        return Response({'message': 'suggestion deleted successfully'}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
def combine_tool_list(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)

        combined_tools = CombinedTool.objects.filter(status='publish',  user_tool__category=category)

        serialized_data = CombinedToolSerializer(combined_tools, many=True).data

        return Response(serialized_data)

    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser])
# def best_tool_create(request):
#     if request.method == 'POST':
#         serializer = BestToolSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def best_tool_create(request):
    if request.method == 'POST':
        try:
            form_data = request.data
            image = request.FILES.get('image')
            category_data = json.loads(form_data.get('category', '{}'))
            combined_tool_data = json.loads(form_data.get('combined_tool', '[]'))

            data = {
                'name': form_data.get('name'),
                'description': form_data.get('description'),
                'image': image,
                'category': category_data,
                'combined_tool_ids': combined_tool_data
            }

            serializer = BestToolSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=201)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=400)
        except KeyError:
            return Response({'error': 'Missing data or image'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)








@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def combined_tool_view(request):
    if request.method == 'GET':
        combined_tools = CombinedTool.objects.all()
        serializer = AdminCombinedToolSerializer(combined_tools, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AdminCombinedToolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PATCH'])
def update_combined_tool_view(request, Combined_tool_id):
    try:
        combined_tool= CombinedTool.objects.get(id=Combined_tool_id)
    except CombinedTool.DoesNotExist:
        return Response ({'error': 'Hashtag not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        serializer = AdminCombinedToolSerializer(combined_tool, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'combined tool updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 



@api_view(['POST'])
@permission_classes([IsAdminUser])
def csvtool_list(request):
    if request.method == 'POST':
        serializer = CsvToolSerializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_csvtool_detail(request, pk):
    try:
        csvtool = CsvTool.objects.get(pk=pk)
    except CsvTool.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CsvToolSerializer(csvtool)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CsvToolSerializer(csvtool, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        csvtool.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def csvtool_detail(request, pk):
    try:
        csvtool = CsvTool.objects.get(pk=pk)
    except CsvTool.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CsvToolSerializer(csvtool)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CsvToolSerializer(csvtool, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        csvtool.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    



