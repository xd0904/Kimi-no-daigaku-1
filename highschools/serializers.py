from rest_framework import serializers
from .models import HighSchool, HighSchoolDepartment, StandardDepartment

class HighSchoolDepartmentSerializer(serializers.ModelSerializer):
    # 기준학과는 이름만 리스트로 깔끔하게 나오도록 설정
    standard_departments = serializers.StringRelatedField(many=True)

    class Meta:
        model = HighSchoolDepartment
        fields = ['id', 'name', 'standard_departments']

class HighSchoolSerializer(serializers.ModelSerializer):
    # 학교 아래에 학과(departments) 목록을 중첩해서 보여줌
    departments = HighSchoolDepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = HighSchool
        fields = ['id', 'region', 'name', 'departments']