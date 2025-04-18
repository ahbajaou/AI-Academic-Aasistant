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
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view

from django.conf import settings
from django.conf.urls.static import static


@ensure_csrf_cookie
@api_view(['GET'])
def get_csrf_token(request):
    return response.Response({'detail': 'CSRF cookie set'})

urlpatterns = [
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path('', include('zauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
