from rest_framework import viewsets
from .models import University
from .serializers import UniversitySerializer
from django.shortcuts import render
from django.http import HttpResponse

class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    대학 입시 정보 전체 조회 API
    GET /api/universities/
    """
    # [수정됨] 데이터베이스 쿼리 최적화 경로 수정
    # 대학 -> 계열(divisions) -> 학과(departments) -> 입결(admission_results) 순서로 접근
    queryset = University.objects.all().prefetch_related(
        'divisions__departments__admission_results'
    )
    
    serializer_class = UniversitySerializer

def university_info_view(request):
    """대학 정보를 보여주는 페이지를 렌더링합니다."""
    return HttpResponse("<h1>대학 정보 페이지입니다.</h1>")