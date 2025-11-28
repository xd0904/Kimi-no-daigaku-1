from rest_framework import serializers
from .models import University, UniversityDivision, UniversityDepartment, AdmissionResult

class AdmissionResultSerializer(serializers.ModelSerializer):
    average_percentile = serializers.FloatField(read_only=True)
    class Meta:
        model = AdmissionResult
        fields = ['year', 'recruit_count', 'average_percentile', 'korean_grade', 'korean_percentile', 'math_grade', 'math_percentile', 'english_grade', 'inquiry_grade', 'inquiry_percentile']

class UniversityDepartmentSerializer(serializers.ModelSerializer):
    admission_history = AdmissionResultSerializer(many=True, source='admission_results', read_only=True)
    final_recruitment_info = serializers.ReadOnlyField(source='get_final_info')
    class Meta:
        model = UniversityDepartment
        fields = ['id', 'name', 'recruitment_group', 'final_recruitment_info', 'admission_history']

class UniversityDivisionSerializer(serializers.ModelSerializer):
    departments = UniversityDepartmentSerializer(many=True, read_only=True)
    eligible_standard_departments = serializers.StringRelatedField(many=True)
    class Meta:
        model = UniversityDivision
        fields = ['id', 'name', 'eligible_standard_departments', 'korean_score', 'math_score', 'inquiry_score', 'english_method', 'english_grade_points', 'naesin_reflection_score', 'departments']

class UniversitySerializer(serializers.ModelSerializer):
    divisions = UniversityDivisionSerializer(many=True, read_only=True)
    
    # [신규] 로고 이미지 URL 처리
    logo_image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = University
        fields = ['id', 'name', 'logo_image', 'divisions']