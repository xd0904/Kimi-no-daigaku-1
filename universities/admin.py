from django.contrib import admin
from django.utils.html import format_html
from .models import University, UniversityDivision, UniversityDepartment, AdmissionResult

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo_preview']
    search_fields = ['name']  # [필수] 대학도 검색 가능하게 설정

    def logo_preview(self, obj):
        if obj.logo_image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.logo_image.url)
        return ""
    logo_preview.short_description = "로고"

@admin.register(UniversityDivision)
class UniversityDivisionAdmin(admin.ModelAdmin):
    list_display = ['university', 'name', 'naesin_reflection_score']
    list_filter = ['university']
    filter_horizontal = ('eligible_standard_departments',)
    
    # [핵심 1] 다른 곳(학과)에서 이 계열을 검색할 수 있도록 검색 기준 설정
    # 대학 이름이나 계열 이름으로 검색 가능
    search_fields = ['name', 'university__name']

    fieldsets = (
        (None, {'fields': ('university', 'name')}),
        ('지원 가능 기준학과', {'fields': ('eligible_standard_departments',)}),
        ('수능 반영 점수 (배점)', {'fields': ('korean_score', 'math_score', 'inquiry_score')}),
        ('영어 반영 정보', {'fields': ('english_method', 'english_grade_points')}),
        ('내신 반영 정보', {'fields': ('naesin_reflection_score',)}),
    )

class AdmissionResultInline(admin.StackedInline):
    model = AdmissionResult
    extra = 0
    fieldsets = (
        ('기본 정보', {'fields': (('year', 'recruit_count'),)}),
        ('국어 성적', {'fields': (('korean_grade', 'korean_percentile'),)}),
        ('수학 성적', {'fields': (('math_grade', 'math_percentile'),)}),
        ('영어 성적', {'fields': (('english_grade',),)}),
        ('탐구 성적', {'fields': (('inquiry_grade', 'inquiry_percentile'),)}),
    )

@admin.register(UniversityDepartment)
class UniversityDepartmentAdmin(admin.ModelAdmin):
    list_display = ['get_university', 'division', 'name', 'recruitment_group']
    list_filter = ['division__university', 'recruitment_group', 'division']
    search_fields = ['name', 'division__university__name']
    
    # [핵심 2] 계열 선택(division)을 긴 드롭다운 대신 '검색 상자'로 변경
    autocomplete_fields = ['division']

    filter_horizontal = ('eligible_standard_departments',)
    inlines = [AdmissionResultInline]

    fieldsets = (
        # division을 선택할 때 이제 검색이 가능합니다.
        (None, {'fields': ('division', 'name', 'recruitment_group')}),
        ('기준학과 예외 설정', {
            'fields': ('eligible_standard_departments',),
            'description': "📌 비워두면 상위 '계열'의 목록이 자동으로 적용됩니다.",
            'classes': ('collapse',)
        }),
        ('점수 예외 설정 (비워두면 계열 점수 적용)', {
            'fields': (
                ('korean_score', 'math_score', 'inquiry_score'),
                ('english_method', 'english_grade_points'),
                'naesin_reflection_score'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_university(self, obj):
        return obj.division.university.name
    get_university.short_description = "대학"