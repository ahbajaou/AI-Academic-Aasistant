"""
URL configuration for ai_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.conf.urls.static import static


# Swagger configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AI Agent API",
        default_version='v1',
        description="API documentation for AI Agent project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

@swagger_auto_schema(
    method='get',
    operation_description="Get CSRF token",
    responses={
        200: openapi.Response(
            description="CSRF token set",
            examples={
                "application/json": {
                    "detail": "CSRF cookie set"
                }
            }
        )
    }
)
@ensure_csrf_cookie
@api_view(['GET'])
def get_csrf_token(request):
    return Response({'detail': 'CSRF cookie set'})

urlpatterns = [
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path('', include('zauth.urls')),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
