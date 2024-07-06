from django.shortcuts import render,redirect
import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,parser_classes,renderer_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import login,logout
from rest_framework.views import APIView
from .services import get_user_data
from .serializers import RegisterUserSerializer,changePasswordSerializer,UserProfileSerializer,UserRoleSerializer,AuthSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import send_code_to_user
from mailchimp_marketing import Client
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

# Custom serializer for obtaining JWT token with additional claims
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        token['is_premium'] = user.is_premium
        

        return token
    
# validate method is overridden to add extra responses to the data returned by the parent class's validate method.
    def validate(self, attrs):
        # call validates the provided attributes using the parent class's validate method and returns the validated data.
        data = super().validate(attrs)

        # Add extra responses
        # Adds the user id to the response
        data.update({'user_id': self.user.id})
        full_name = f"{self.user.first_name} {self.user.last_name}"
        data.update({'full_name': full_name})
        data.update({'email': self.user.email})
        data.update({'is_verified': self.user.is_verified})
        data.update({'is_premium': self.user.is_premium})

        return data

       
    
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class =MyTokenObtainPairSerializer 


@api_view(['GET'])
def google_login(request):
    auth_serializer = AuthSerializer(data=request.GET)
    auth_serializer.is_valid(raise_exception=True)
    
    validated_data = auth_serializer.validated_data
    user_data = get_user_data(validated_data)
    
    user = User.objects.get(email=user_data['email'])
    login(request, user)
    
    response_data = {
        'access_token': user_data['access_token'],
        'refresh_token': user_data['refresh_token'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'email': user_data['email']
    }

    return Response(response_data, status=status.HTTP_200_OK)



class LogoutApi(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse('200')


@api_view(['POST'])
def registerUsers(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()  # Save the user
        send_code_to_user(user.email)  # Send email to the user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def changePasswordView(request):
    """
    API endpoint to change the password of the authenticated user.
    """
    if request.method == 'PUT':
        serializer=changePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': 'password changed successfully'}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to changed password", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def code_verification(request):
    if request.method == 'POST':
        otp_code = request.data.get('code') # Extract the OTP code from the request data
        if not otp_code:
            # If OTP code is not provided, return a bad request response
            return Response({'message': 'Passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find a OneTimePassword object with the provided OTP code
            user_code_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True  # If the user is not verified, mark them as verified and save
                user.save()
                return Response({'message': 'Account email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Code is invalid, user already verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        except OneTimePassword.DoesNotExist:
            return Response({'message': 'Invalid passcode'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    send_result = send_code_to_user(user.email)
    if "Failed" in send_result:
        return Response({'error': send_result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Assuming the send_code_to_user function returns a success message on success
    if send_result == "OTP sent successfully":
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    else:
        # Handling any other unexpected response from the utility function
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_roles(request):
    role = UserRole.objects.all()
    serializer = UserRoleSerializer(role, many=True)
    return Response(serializer.data)





@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])
def user_profile(request, user_id):
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        try:
            profile_picture = request.FILES.get('profile_picture')
            gender = request.data.get('gender')
            country = request.data.get('country')
            company = request.data.get('company')
            role_data = json.loads(request.data.get('role', '{}'))

            # Extract role name from the parsed JSON data
            role_name = role_data.get('name') if role_data else None

            # Now, handle the role association
            if role_name:
                # Assuming UserRole objects are already created, fetch the relevant role
                role_instance = UserRole.objects.filter(name=role_name).first()
            else:
                role_instance = None

            # Update UserProfile fields
            profile.gender = gender
            profile.country = country
            profile.company = company
            profile.role = role_instance

            if profile_picture:
                profile.profile_picture = profile_picture

            profile.save()

            return Response({"message": "User profile updated successfully"}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON data for role"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




