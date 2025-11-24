from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HighSchoolViewSet

router = DefaultRouter()
router.register(r'', HighSchoolViewSet, basename='highschool')

urlpatterns = [
    path('', include(router.urls)),
]