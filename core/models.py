# core/models.py

from django.db import models

# ❌ 이 파일 내부에서는 다른 앱의 모델을 임포트하지 않습니다.

class AdmissionResult(models.Model):
    # 결과를 위한 서브 모델 (일대다 관계)
    year = models.IntegerField()
    quota = models.IntegerField()
    korean_grade = models.FloatField()
    korean_percentile = models.IntegerField()
    math_grade = models.FloatField()
    math_percentile = models.IntegerField()
    english_grade = models.IntegerField()
    inquiry_grade = models.FloatField()
    inquiry_percentile = models.IntegerField()
    
    # 상위 모델과의 관계 설정
    department = models.ForeignKey(
        'DepartmentAdmission', 
        related_name='results', 
        on_delete=models.CASCADE
    )

class DepartmentAdmission(models.Model):
    # 주요 대학/학과 정보
    # 이 필드들이 CharField이므로, 로드 스크립트에서 이름 문자열을 넣어줘야 합니다.
    university = models.CharField(max_length=50)
    division = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    recruitment_group = models.CharField(max_length=10)
    standards_json = models.JSONField(default=list) 
    scoring_json = models.JSONField(default=dict) 

    def __str__(self):
        return f"{self.university} - {self.department}"