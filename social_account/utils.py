from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class Google:
    @staticmethod
    def validate(access_token):
        try:
            # Verify the provided access token
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            if "accounts.google.com" in id_info['iss']:
                # Check if the issuer of the token is from "accounts.google.com"
                return id_info
            else:
                raise AuthenticationFailed("Invalid token issuer")
        except Exception as e:
            raise AuthenticationFailed("Token is invalid or has expired")

def login_social_user(email, password):
    # Authenticate the user using the provided email and password
    user = authenticate(email=email, password=password)
    if not user:
        raise AuthenticationFailed("Invalid credentials, please try again")
    
    # Generate tokens or retrieve existing tokens
    user_token = user.tokens()
    
    return {
        'email': user.email,
        'full_name': user.get_full_name(),
        'access_token': str(user_token.get('access')),
        'refresh_token': str(user_token.get('refresh'))
    }

def register_social_user(provider, email, first_name, last_name):
    users = User.objects.filter(email=email)
    
    if users.exists():
        # Check if the provider matches the authentication provider of the existing user
        existing_user = users[0]
        if provider == existing_user.auth_provider:
            # If the provider matches, login the user using social authentication
            return login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
        else:
            raise AuthenticationFailed(f"Please continue your login with {existing_user.auth_provider}")
    else:
        # If a user with the provided email doesn't exist, create a new user
        new_user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_AUTH_PASSWORD
        }
        # Create a new user with the provided information
        new_user = User.objects.create_user(**new_user_data)
        new_user.auth_provider = provider
        new_user.is_verified = True
        new_user.save()
        
        # After user registration, login the user using social authentication
        return login_social_user(email=new_user.email, password=settings.SOCIAL_AUTH_PASSWORD)
