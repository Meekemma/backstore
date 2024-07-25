import json
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Group
from geeks_tools.serializers_main import CategoryListSerializer,SubcategorylistSerializer,HashtagSerializer,UserToolSerializer,SetUpSerializer,ToolInfoSerializer,SubscriptionSerializer,BookmarkSerializer,CombinedToolSerializer,BestToolSerializer,CsvToolSerializer
from geeks_tools.serializers_admin import AdminSuggestionSerializer,AdminPopularSearchSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from .filters import CombinedToolFilter,CsvToolFilter
from api.permissions import IsPremium
from django.contrib.auth import get_user_model
User = get_user_model()
from geeks_tools.models import *
from django.conf import settings
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

# Create your views here.



mailchimp = Client()
mailchimp.set_config({
  'api_key': settings.MAILCHIMP_API_KEY,
  'server': settings.MAILCHIMP_REGION,
})


def mailchimp_ping_view(request):
    response = mailchimp.ping.get()
    return JsonResponse(response)

# Create your views here.




@api_view(['GET'])
@permission_classes([AllowAny])
@parser_classes([FormParser, MultiPartParser])
def categorty_list(request):
    category = Category.objects.all()
    serializer = CategoryListSerializer(category, many=True)
    return Response(serializer.data)





@api_view(['GET'])
@permission_classes([AllowAny])
def category_subcategories(request, category_id):
    try:
        # Retrieve the Category instance
        category = Category.objects.get(pk=category_id)
        
        # Retrieve all subcategories associated with the category
        subcategories = Subcategory.objects.filter(category=category)

        # Serialize the subcategories data
        serialized_data = SubcategorylistSerializer(subcategories, many=True).data

        return Response(serialized_data)

    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)





@api_view(['GET'])
@permission_classes([AllowAny])
def hashtag_list(request, subcategory_id):
    try:
         # Retrieve the Subcategory instance
        subcategory =Subcategory.objects.get(pk=subcategory_id)
         # Retrieve all hashtags associated with the subcategory
        hashtags = Hashtag.objects.filter(subcategories=subcategory)


        serializer = HashtagSerializer(hashtags, many=True)
        return Response(serializer.data)
    except Subcategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)

    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])
def user_tool_creation(request):
    try:
        # Accessing form data
        form_data = request.data

        # Parsing nested JSON fields
        category_data = json.loads(form_data.get('category', '{}'))
        subcategory_data = json.loads(form_data.get('subcategory', '{}'))
        hashtags_data = json.loads(form_data.get('hashtag', '[]'))

        # Construct data dictionary for validation
        data = {
            'name': form_data.get('name'),
            'url': form_data.get('url'),
            'logo': form_data.get('logo'),
            'intro': form_data.get('intro'),
            'pricing': form_data.get('pricing'),
            'category': category_data,
            'subcategory': subcategory_data,
            'hashtag': hashtags_data,
            'user': request.user.id  # Assuming user is required in validated_data
        }

        # Validate data using the serializer
        serializer = UserToolSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Extract and create or get Category and Subcategory
        category_name = validated_data.pop('category')['name']
        subcategory_name = validated_data.pop('subcategory')['name']

        category, created = Category.objects.get_or_create(name=category_name)
        subcategory, created = Subcategory.objects.get_or_create(name=subcategory_name, category=category)

        # Create User_tool object
        user_tool = User_tool.objects.create(
            user=request.user,
            name=validated_data['name'],
            url=validated_data['url'],
            logo=validated_data['logo'],
            intro=validated_data['intro'],
            pricing=validated_data['pricing'],
            category=category,
            subcategory=subcategory
        )

        # Extract and create or get Hashtags
        for hashtag_data in validated_data.pop('hashtag'):
            hashtag_term = hashtag_data['term']
            hashtag, created = Hashtag.objects.get_or_create(term=hashtag_term)
            user_tool.hashtag.add(hashtag)

        # Serialize and return the created user tool
        result_serializer = UserToolSerializer(user_tool)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
    except serializers.ValidationError as e:
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tool(request, tool_id):
    try:
        # Fetch the User_tool object by ID
        user_tool = User_tool.objects.get(id=tool_id, user=request.user)

        # Serialize the User_tool object
        serializer = UserToolSerializer(user_tool)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User_tool.DoesNotExist:
        # Return a 404 response if the object does not exist
        return Response({"error": "User tool not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Return a 500 response for any other exceptions
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bookmark_list_create(request):
    if request.method == 'GET':
        bookmarks = Bookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookmarkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def bookmark_detail(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
    except Bookmark.DoesNotExist:
        return Response({"error": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        serializer = BookmarkSerializer(bookmark)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        try:
            bookmark.delete()
            return Response({'message': 'Bookmark was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_setup(request):
    if request.method == 'POST':
        serializer = SetUpSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "SetUp completed successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_tool_info(request):
    if request.method == 'POST':
        serializer = ToolInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Tool Info created successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def tool_info_view(request, tool_info_id=None):
    if request.method == 'GET':
        if tool_info_id:
            try:
                tool_info = ToolInfo.objects.get(id=tool_info_id)
                serializer = ToolInfoSerializer(tool_info)
                return JsonResponse(serializer.data, status=200)
            except ToolInfo.DoesNotExist:
                return JsonResponse({'error': 'ToolInfo not found'}, status=404)
        else:
            tool_infos = ToolInfo.objects.all()
            serializer = ToolInfoSerializer(tool_infos, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)




@api_view(['GET'])
def all_combined_view(request):
    csvtools = CsvTool.objects.all()
    csvtool_serializer = CsvToolSerializer(csvtools, many=True)

    # Retrieve and serialize CombinedTool objects
    combined_tools = CombinedTool.objects.filter(status='publish')
    combined_tool_serializer = CombinedToolSerializer(combined_tools, many=True)

    # Combine the serialized data
    combined_data = {
        'csvtools': csvtool_serializer.data,
        'combined_tools': combined_tool_serializer.data
    }

    return Response(combined_data)



@api_view(['GET'])
def user_csvtool_detail(request, pk):
    try:
        csvtool = CsvTool.objects.get(pk=pk)
    except CsvTool.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CsvToolSerializer(csvtool)
        return Response(serializer.data)
    

@api_view(['GET'])
def user_combinedtool_detail(request, pk):
    try:
        combined_tool = CombinedTool.objects.get(pk=pk)
    except CombinedTool.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CombinedToolSerializer(combined_tool)
        return Response(serializer.data)





@api_view(['GET'])
def general_tool_view(request, tool_id=None):
    if tool_id is not None:
        try:
            # Retrieve the specific instance of CombinedTool by ID and status 'publish'
            combined_tool = CombinedTool.objects.get(id=tool_id, status='publish', user_tool__pricing='Freemium')

            # Serialize the combined data for the specific tool
            serialized_data = {
                'id': combined_tool.id,
                'user_tool': UserToolSerializer(combined_tool.user_tool).data,
                'setup': SetUpSerializer(combined_tool.setup).data,
                'tool_info': ToolInfoSerializer(combined_tool.tool_info).data
            }

            return Response(serialized_data, status=status.HTTP_200_OK)
        except CombinedTool.DoesNotExist:
            return Response({'error': 'CombinedTool not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Retrieve all instances of CombinedTool with status 'publish'
        combined_tools = CombinedTool.objects.filter(status='publish', user_tool__pricing='Freemium')

        # Serialize the combined data for all tools
        serialized_data = [
            {
                'id': tool.id,
                'user_tool': UserToolSerializer(tool.user_tool).data,
                'setup': SetUpSerializer(tool.setup).data,
                'tool_info': ToolInfoSerializer(tool.tool_info).data
            }
            for tool in combined_tools
        ]

        return Response(serialized_data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tools_view(request):
    combined_tools = CombinedTool.objects.filter(status='publish', user_tool__user=request.user)
    serialized_data = CombinedToolSerializer(combined_tools, many=True).data
    return Response(serialized_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tool_detail_view(request, pk):
    try:
        combined_tool = CombinedTool.objects.get(id=pk, status='publish', user_tool__user=request.user)
        serialized_data = CombinedToolSerializer(combined_tool).data
    except CombinedTool.DoesNotExist:
        return Response({'error': 'CombinedTool not found or you do not have permission to access it.'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serialized_data, status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def publish_update(request, pk):
    try:
        combined_tool = CombinedTool.objects.get(pk=pk, user_tool__user=request.user, status='publish')
    except CombinedTool.DoesNotExist:
        return Response({'error': 'Publish CombinedTool not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    data['status'] = 'publish'

    serializer = CombinedToolSerializer(combined_tool, data=data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def draft_combined_tools(request):
    user = request.user
    draft_tools = CombinedTool.objects.filter(user_tool__user=user, status='draft')
    serializer = CombinedToolSerializer(draft_tools, many=True)
    return Response(serializer.data)





@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def draft_update(request, pk):
    try:
        combined_tool = CombinedTool.objects.get(pk=pk, user_tool__user=request.user, status='draft')
    except CombinedTool.DoesNotExist:
        return Response({'error': 'Draft CombinedTool not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    data['status'] = 'publish'

    serializer = CombinedToolSerializer(combined_tool, data=data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def premium_combined_tools(request):
    combined_tools = CombinedTool.objects.filter(created_by='premium_user', status='publish')
    serializer = CombinedToolSerializer(combined_tools, many=True)
    return Response(serializer.data)





@api_view(['POST'])
def email_subcription(request):
    if request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Email Subcription was successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def subscription_create_view(request):
    if request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            # Save subscription to database
            subscription = serializer.save()

            # Add email to Mailchimp audience
            mailchimp = Client()
            mailchimp.set_config({
                'api_key': settings.MAILCHIMP_API_KEY,
                'server': settings.MAILCHIMP_REGION,
            })
            audience_id = settings.MAILCHIMP_MARKETING_AUDIENCE_ID

            try:
                # Add email to Mailchimp audience
                mailchimp.lists.add_list_member(audience_id, {
                    'email_address': subscription.email,
                    'status': 'subscribed' if subscription.is_subscribed else 'unsubscribed'
                })
            except ApiClientError as error:
                # Handle Mailchimp API errors
                subscription.delete()  # Rollback database operation if Mailchimp operation fails
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


@api_view(['GET'])
@permission_classes([AllowAny])
@parser_classes([FormParser, MultiPartParser])
def popular_search_view(request):
    popular_search = PopularSearch.objects.all()
    serializer = AdminPopularSearchSerializer(popular_search, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([AllowAny])
def suggestion_view(request):
    suggestion = Suggestion.objects.all()
    serializer = AdminSuggestionSerializer(suggestion, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([AllowAny])
@parser_classes([FormParser, MultiPartParser])
def best_tool_view(request):
    best_tool = BestTool.objects.all()
    serializer = BestToolSerializer(best_tool, many=True)
    return Response(serializer.data)



class CsvToolListView(generics.ListAPIView):
    queryset = CsvTool.objects.all()
    serializer_class = CsvToolSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CsvToolFilter



class CombinedToolListView(generics.ListAPIView):
    queryset = CombinedTool.objects.all()
    serializer_class = CombinedToolSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CombinedToolFilter


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def user_tool_csv(request):
    try:
        # Assuming JSON data is sent in request.data as a list of objects
        json_data = request.data

        if not isinstance(json_data, list):
            return Response({"error": "Expected a list of objects"}, status=status.HTTP_400_BAD_REQUEST)

        created_objects = []
        errors = []

        for item in json_data:
            serializer = UserToolSerializer(data=item, context={'request': request})
            if serializer.is_valid():
                validated_data = serializer.validated_data

                # Extract and create or get Category and Subcategory
                category_name = validated_data.pop('category')['name']
                subcategory_name = validated_data.pop('subcategory')['name']

                category, created = Category.objects.get_or_create(name=category_name)
                subcategory, created = Subcategory.objects.get_or_create(name=subcategory_name, category=category)

                # Create User_tool object
                user_tool = User_tool.objects.create(
                    user=request.user,
                    name=validated_data['name'],
                    url=validated_data['url'],
                    logo=validated_data['logo'],
                    intro=validated_data['intro'],
                    pricing=validated_data['pricing'],
                    category=category,
                    subcategory=subcategory
                )

                # Extract and create or get Hashtags
                for hashtag_data in validated_data.pop('hashtag'):
                    hashtag_term = hashtag_data['term']
                    hashtag, created = Hashtag.objects.get_or_create(term=hashtag_term)
                    user_tool.hashtag.add(hashtag)

                created_objects.append(user_tool)
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

        result_serializer = UserToolSerializer(created_objects, many=True)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
