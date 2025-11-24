from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('highschool-search/', views.highschool_search, name='highschool_search'),
]