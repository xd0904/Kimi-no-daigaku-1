from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet

# DRF의 라우터를 사용해 자동으로 URL을 생성합니다.
router = DefaultRouter()
router.register(r'', UniversityViewSet, basename='university')

urlpatterns = [
    path('', include(router.urls)),
]