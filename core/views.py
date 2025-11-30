from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
# TODO: 모델 이름을 실제 파일에 맞게 수정하세요.
from .models import DepartmentAdmission, AdmissionResult

def index(request):
    return render(request, 'core/index.html')

def highschool_search(request):
    return render(request, 'core/highschool_search.html')

def edurank_search(request):
   return render(request, 'core/edurank_search.html')

def department_search_api(request):
    univ_query = request.GET.get('university', '').strip()
    dept_query = request.GET.get('department', '').strip()

    # DB 필터링 로직
    filters = Q()
    if univ_query:
        filters &= Q(university__icontains=univ_query)
    if dept_query:
        filters &= Q(department__icontains=dept_query)

    departments = DepartmentAdmission.objects.filter(filters).prefetch_related('results')
    
    data = []
    for dept in departments:
        # 클라이언트에 전달할 JSON 형식으로 변환
        item = {
            'id': dept.id,
            'university': dept.university,
            'division': dept.division,
            'department': dept.department,
            'recruitment_group': dept.recruitment_group,
            'standards': dept.standards_json, # JSONField는 자동으로 Python 객체로 로드됨
            'scoring': dept.scoring_json,
            'results': [
                {
                    'year': r.year,
                    'quota': r.quota,
                    'korean_grade': r.korean_grade, 
                    'korean_percentile': r.korean_percentile,
                    'math_grade': r.math_grade,
                    'math_percentile': r.math_percentile,
                    'english_grade': r.english_grade,
                    'inquiry_grade': r.inquiry_grade,
                    'inquiry_percentile': r.inquiry_percentile,
                } for r in dept.results.all().order_by('-year')
            ]
        }
        data.append(item)

    return JsonResponse(data, safe=False)