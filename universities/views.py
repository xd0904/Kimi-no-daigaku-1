from rest_framework import viewsets
from .models import University
from .serializers import UniversitySerializer

class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    대학 입시 정보 전체 조회 API
    GET /api/universities/
    """
    # 데이터베이스 쿼리 최적화 (대학 -> 학과 -> 입결 정보를 한 번에 가져옴)
    queryset = University.objects.all().prefetch_related('departments__admission_results')
    serializer_class = UniversitySerializer