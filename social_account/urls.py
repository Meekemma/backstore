from django.urls import path

from social_account.views import GoogleSocialAuthView

urlpatterns = [
    path('google/', GoogleSocialAuthView.as_view(), name='google') 

]