"""
URL configuration for Kimi_no_daigaku project.

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
# Kimi_no_daigaku/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # [추가]
from django.conf.urls.static import static   # [추가]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/highschools/', include('highschools.urls')),
    path('api/universities/', include('universities.urls')),
    path('', include('core.urls')),
]

# [추가] 미디어 파일 URL 연결
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)