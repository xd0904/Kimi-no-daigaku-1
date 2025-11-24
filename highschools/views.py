from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import HighSchool
from .serializers import HighSchoolSerializer

class HighSchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    특성화고 및 학과 정보 조회 API
    """
    queryset = HighSchool.objects.all()
    serializer_class = HighSchoolSerializer

    def get_queryset(self):
        """
        URL 파라미터로 region(교육청)이 들어오면 필터링합니다.
        예: /api/highschools/?region=서울특별시교육청
        """
        queryset = super().get_queryset()
        region = self.request.query_params.get('region')
        
        if region:
            queryset = queryset.filter(region__contains=region)
        return queryset

    @action(detail=False, methods=['get'])
    def regions(self, request):
        """
        등록된 모든 시도교육청 목록을 중복 없이 반환합니다.
        용도: 프론트엔드에서 '지역 선택' 드롭박스를 만들 때 사용
        URL: /api/highschools/regions/
        """
        regions = HighSchool.objects.values_list('region', flat=True).distinct().order_by('region')
        return Response(list(regions))