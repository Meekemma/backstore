from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from .views import health_check

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define the schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Geeks Tool API",
        default_version='v1',
        description="API Created by Meeky",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Define the URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('geeks_tools/', include('geeks_tools.urls')),
    path('blogpost/', include('blogpost.urls')),
    path('payment/', include('payment.urls')),
    path('health/', health_check, name='health_check'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    re_path(r'auth/', include('drf_social_oauth2.urls', namespace='drf')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
