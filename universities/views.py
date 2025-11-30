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
    # 데이터베이스 쿼리 최적화 (대학 -> 학과 -> 입결 정보를 한 번에 가져옴)
    queryset = University.objects.all().prefetch_related('departments__admission_results')
    serializer_class = UniversitySerializer

def university_info_view(request):
    """대학 정보를 보여주는 페이지를 렌더링합니다."""
    # 여기에 데이터 로직을 추가할 수 있습니다.
    
    # 예시로 간단한 HTML을 반환하거나, 실제 템플릿을 렌더링합니다.
    # return render(request, 'universities/university_info.html', {})
    
    return HttpResponse("<h1>대학 정보 페이지입니다.</h1>")