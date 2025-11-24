from django.contrib import admin
from .models import University, UniversityDepartment, AdmissionResult

# 가로형 입력 폼 (StackedInline)
class AdmissionResultInline(admin.StackedInline):
    model = AdmissionResult
    extra = 0
    
    fieldsets = (
        ('기본 정보', {
            'fields': (('year', 'recruit_count', 'total_average_grade'),)
        }),
        ('국어 성적', {
            'fields': (('korean_grade', 'korean_percentile'),)
        }),
        ('수학 성적', {
            'fields': (('math_grade', 'math_percentile'),)
        }),
        ('영어 성적', {
            'fields': (('english_grade', 'english_percentile'),)
        }),
        ('탐구 성적', {
            'fields': (('inquiry_grade', 'inquiry_percentile'),)
        }),
    )

@admin.register(UniversityDepartment)
class UniversityDepartmentAdmin(admin.ModelAdmin):
    list_display = ['university', 'name']
    list_filter = ['university']
    search_fields = ['name', 'university__name']
    
    inlines = [AdmissionResultInline]
    
    fieldsets = (
        (None, {'fields': ('university', 'name')}),
        ('예외 반영비율 (비워두면 대학 기본값 사용)', {
            'fields': ('korean_ratio', 'math_ratio', 'inquiry_ratio', 'english_method', 'english_ratio', 'english_grade_points'),
            'classes': ('collapse',)
        }),
    )

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'has_guide_image']
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('기준학과 안내 정보', {
            'fields': ('standard_guide_image', 'standard_guide_text'),
        }),
        ('국/수/탐 기본 비율', {'fields': ('default_korean_ratio', 'default_math_ratio', 'default_inquiry_ratio')}),
        ('영어 기본 반영 정보', {'fields': ('default_english_method', 'default_english_ratio', 'default_english_grade_points')}),
    )

    def has_guide_image(self, obj):
        return "📸 있음" if obj.standard_guide_image else "📝 텍스트"
    has_guide_image.short_description = "기준학과 안내"