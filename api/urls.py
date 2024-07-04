from django.urls import path
from . import views_main
from . import views_admin
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from .views_main import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [


    
    # path('', SpectacularAPIView.as_view(), name='schema'),
    # # Optional UI:
    # path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/password_reset/request/', reset_password_request_token, name='reset_password_request_token'),
    path('api/password_reset/confirm/', reset_password_confirm, name='reset_password_confirm'),


    path('register/', views_main.registerUsers, name='register'),
    path('change-password/', views_main.changePasswordView, name='change-password'),
    path('verify_code/', views_main.code_verification, name='verify_code'),
    path('resend-otp/', views_main.resend_otp, name='resend-otp'),
    path('user_profile/<int:user_id>/', views_main.user_profile, name='user_profile'),
    path('role_list/', views_main.user_roles, name='role_list'),


    path('user-list/', views_admin.user_list, name='user-list'),
    path('user/<int:user_id>/', views_admin.User_admin, name='user-admin'),
    path('ping/', views_main.mailchimp_ping_view, name='ping'), 


]
