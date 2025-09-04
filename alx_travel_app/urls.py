"""
URL configuration for alx_travel_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="ALX Travel App API",
        default_version='v1',
        description="""
        A comprehensive travel booking platform API built with Django REST Framework.
        
        ## Features
        - User authentication and profile management
        - Trip browsing and booking
        - Destination management
        - Booking history and status tracking
        - Admin functionality for trip and booking management
        
        ## Authentication
        This API uses Token-based authentication. Include your token in the Authorization header:
        `Authorization: Token your_token_here`
        
        ## Rate Limiting
        - Authenticated users: 1000 requests/hour
        - Anonymous users: 100 requests/hour
        
        ## Support
        For API support, contact: uhuribhang211@gmail.com
        """,
        terms_of_service="https://www.alx-travel.com/terms/",
        contact=openapi.Contact(
            name="ALX Travel App Support",
            email="uhuribhang211@gmail.com",
            url="https://www.alx-travel.com/support/"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include('trips.urls')),
    path('api/v1/', include('bookings.urls')),
    path('api/v1/', include('users.urls')),
    
    # API Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-alt'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
