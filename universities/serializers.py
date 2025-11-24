# universities/serializers.py

from rest_framework import serializers
from .models import University, UniversityDepartment, AdmissionResult

class AdmissionResultSerializer(serializers.ModelSerializer):
    # 모델의 @property로 만든 계산된 필드 추가
    average_percentile = serializers.FloatField(read_only=True)

    class Meta:
        model = AdmissionResult
        fields = [
            'year', 
            'recruit_count', 
            'total_average_grade',
            'average_percentile',  # [추가] 자동 계산된 평균 백분위
            'korean_grade', 'korean_percentile',
            'math_grade', 'math_percentile',
            'english_grade', 'english_percentile',
            'inquiry_grade', 'inquiry_percentile'
        ]

# 나머지 Serializer들은 기존 유지
class UniversityDepartmentSerializer(serializers.ModelSerializer):
    recruitment_guideline = serializers.SerializerMethodField()
    admission_history = AdmissionResultSerializer(many=True, source='admission_results', read_only=True)

    class Meta:
        model = UniversityDepartment
        fields = ['id', 'name', 'recruitment_guideline', 'admission_history']

    def get_recruitment_guideline(self, obj):
        # (이전 코드와 동일 - 생략)
        korean = obj.korean_ratio if obj.korean_ratio is not None else obj.university.default_korean_ratio
        math = obj.math_ratio if obj.math_ratio is not None else obj.university.default_math_ratio
        inquiry = obj.inquiry_ratio if obj.inquiry_ratio is not None else obj.university.default_inquiry_ratio
        
        eng_method = obj.english_method or obj.university.default_english_method
        eng_ratio = obj.english_ratio if obj.english_ratio is not None else obj.university.default_english_ratio
        eng_table = obj.english_grade_points if obj.english_grade_points else obj.university.default_english_grade_points

        return {
            "reflection_ratios": {
                "korean": korean, "math": math, "inquiry": inquiry,
            },
            "english_info": {
                "method": eng_method,
                "ratio": eng_ratio if eng_method == 'RATIO' else 0,
                "grade_points": eng_table if eng_method != 'RATIO' else None
            }
        }

class UniversitySerializer(serializers.ModelSerializer):
    departments = UniversityDepartmentSerializer(many=True, read_only=True)
    standard_guide_image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = University
        fields = ['id', 'name', 'standard_guide_image', 'standard_guide_text', 'departments']