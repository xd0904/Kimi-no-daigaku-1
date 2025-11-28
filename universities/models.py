from django.db import models
from highschools.models import StandardDepartment

class University(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="대학명")
    
    # [신규] 대학 로고 이미지
    logo_image = models.ImageField(
        upload_to='university_logos/', 
        null=True, blank=True, 
        verbose_name="대학 로고"
    )

    def __str__(self):
        return self.name

class UniversityDivision(models.Model):
    """
    모집 계열
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='divisions', verbose_name="소속 대학")
    name = models.CharField(max_length=100, verbose_name="계열명 (예: 인문계열)")

    # 1. 지원 가능 기준학과 (기본)
    eligible_standard_departments = models.ManyToManyField(
        StandardDepartment,
        related_name='eligible_divisions',
        verbose_name="지원 가능 기준학과",
        blank=True
    )

    # 2. 수능 반영 점수
    korean_score = models.FloatField(default=0, verbose_name="국어 반영 점수")
    math_score = models.FloatField(default=0, verbose_name="수학 반영 점수")
    inquiry_score = models.FloatField(default=0, verbose_name="탐구 반영 점수")

    # 3. 영어 반영 정보
    ENGLISH_METHOD_CHOICES = [('ADD', '가산점'), ('SUB', '감점')]
    english_method = models.CharField(max_length=10, choices=ENGLISH_METHOD_CHOICES, default='ADD', verbose_name="영어 반영방식")
    english_grade_points = models.JSONField(null=True, blank=True, verbose_name="영어 등급별 점수표")

    # 4. 내신 반영 정보
    naesin_reflection_score = models.FloatField(default=0, verbose_name="내신 반영 점수")

    class Meta:
        unique_together = ('university', 'name')
        verbose_name = "모집 계열"
        verbose_name_plural = "모집 계열 목록"

    def __str__(self):
        return f"{self.university.name} - {self.name}"


class UniversityDepartment(models.Model):
    """
    학과 모델
    """
    division = models.ForeignKey(UniversityDivision, on_delete=models.CASCADE, related_name='departments', verbose_name="소속 계열")
    name = models.CharField(max_length=100, verbose_name="학과명")

    # --- [신규] 모집군 정보 ---
    GROUP_CHOICES = [
        ('가군', '가군'),
        ('나군', '나군'),
        ('다군', '다군'),
        ('군외', '군외'),
    ]
    recruitment_group = models.CharField(
        max_length=10, 
        choices=GROUP_CHOICES, 
        default='가군',
        verbose_name="모집군"
    )

    # --- 예외 설정 (비워두면 계열 설정 사용) ---
    
    # 1. 기준학과 예외 (입력 안 하면 계열 것 사용)
    eligible_standard_departments = models.ManyToManyField(
        StandardDepartment,
        related_name='eligible_departments',
        verbose_name="지원 가능 기준학과 (예외)",
        blank=True
    )

    # 2. 수능 점수 예외
    korean_score = models.FloatField(null=True, blank=True, verbose_name="국어 점수(예외)")
    math_score = models.FloatField(null=True, blank=True, verbose_name="수학 점수(예외)")
    inquiry_score = models.FloatField(null=True, blank=True, verbose_name="탐구 점수(예외)")

    # 3. 영어 예외
    english_method = models.CharField(max_length=10, choices=UniversityDivision.ENGLISH_METHOD_CHOICES, null=True, blank=True, verbose_name="영어 방식(예외)")
    english_grade_points = models.JSONField(null=True, blank=True, verbose_name="영어 점수표(예외)")

    # 4. 내신 예외
    naesin_reflection_score = models.FloatField(null=True, blank=True, verbose_name="내신 점수(예외)")

    class Meta:
        unique_together = ('division', 'name', 'recruitment_group') # 학과명이 같아도 군이 다르면 등록 가능

    def __str__(self):
        return f"{self.division.university.name} {self.name} ({self.recruitment_group})"

    # [핵심] 최종 정보 판단 로직
    @property
    def get_final_info(self):
        # 1. 수능 점수
        kor = self.korean_score if self.korean_score is not None else self.division.korean_score
        mat = self.math_score if self.math_score is not None else self.division.math_score
        inq = self.inquiry_score if self.inquiry_score is not None else self.division.inquiry_score
        
        # 2. 영어
        eng_m = self.english_method or self.division.english_method
        eng_p = self.english_grade_points if self.english_grade_points is not None else self.division.english_grade_points
        
        # 3. 내신
        nae = self.naesin_reflection_score if self.naesin_reflection_score is not None else self.division.naesin_reflection_score

        # 4. 기준학과 (내 설정이 하나라도 있으면 내 것 사용, 없으면 계열 것 사용)
        if self.eligible_standard_departments.exists():
            standards = [d.name for d in self.eligible_standard_departments.all()]
        else:
            standards = [d.name for d in self.division.eligible_standard_departments.all()]

        return {
            "group": self.recruitment_group,
            "standards": standards,
            "scores": {"korean": kor, "math": mat, "inquiry": inq},
            "english": {"method": eng_m, "points": eng_p},
            "naesin": nae
        }


class AdmissionResult(models.Model):
    department = models.ForeignKey(UniversityDepartment, on_delete=models.CASCADE, related_name='admission_results', verbose_name="학과")
    year = models.IntegerField(verbose_name="학년도")
    recruit_count = models.IntegerField(null=True, blank=True, verbose_name="모집인원")
    
    korean_grade = models.FloatField(null=True, blank=True, verbose_name="국어 등급")
    korean_percentile = models.FloatField(null=True, blank=True, verbose_name="국어 백분위")
    math_grade = models.FloatField(null=True, blank=True, verbose_name="수학 등급")
    math_percentile = models.FloatField(null=True, blank=True, verbose_name="수학 백분위")
    english_grade = models.FloatField(null=True, blank=True, verbose_name="영어 등급")
    inquiry_grade = models.FloatField(null=True, blank=True, verbose_name="탐구 등급")
    inquiry_percentile = models.FloatField(null=True, blank=True, verbose_name="탐구 백분위")

    class Meta:
        ordering = ['-year']
        unique_together = ('department', 'year')

    def __str__(self):
        return f"{self.department.name} ({self.year})"

    @property
    def average_percentile(self):
        scores = [self.korean_percentile, self.math_percentile, self.inquiry_percentile]
        valid_scores = [s for s in scores if s is not None]
        if not valid_scores: return None
        return round(sum(valid_scores) / len(valid_scores), 2)