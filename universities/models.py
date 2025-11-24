from django.db import models

class University(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="대학명")
    
    # 기준학과 안내 (이미지 vs 텍스트)
    standard_guide_image = models.ImageField(
        upload_to='university_guides/', 
        null=True, blank=True, 
        verbose_name="기준학과 안내 이미지",
        help_text="기준학과 표가 있는 경우 이미지를 업로드하세요."
    )
    standard_guide_text = models.TextField(
        null=True, blank=True, 
        verbose_name="기준학과 안내 문구",
        default="본 대학은 모집단위와 관련된 전문교과를 이수한 경우 지원 가능합니다.\n(자세한 사항은 입학처 모집요강 참조)",
        help_text="이미지가 없을 경우 표시될 문구입니다."
    )

    # 국/수/탐 기본 반영비
    default_korean_ratio = models.IntegerField(default=0, verbose_name="기본 국어 반영비(%)")
    default_math_ratio = models.IntegerField(default=0, verbose_name="기본 수학 반영비(%)")
    default_inquiry_ratio = models.IntegerField(default=0, verbose_name="기본 탐구 반영비(%)")

    # 영어 반영 방식
    ENGLISH_METHOD_CHOICES = [
        ('RATIO', '비율 반영 (%)'),
        ('ADD', '가산점 (총점 + @)'),
        ('SUB', '감점 (총점 - @)'),
    ]
    default_english_method = models.CharField(
        max_length=10, 
        choices=ENGLISH_METHOD_CHOICES, 
        default='RATIO',
        verbose_name="기본 영어 반영방식"
    )
    default_english_ratio = models.IntegerField(default=0, verbose_name="기본 영어 반영비(%)")
    default_english_grade_points = models.JSONField(
        null=True, blank=True, 
        verbose_name="기본 영어 등급별 점수표",
        help_text='예: {"1": 100, "2": 95, ...}'
    )

    def __str__(self):
        return self.name


class UniversityDepartment(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='departments', verbose_name="소속 대학")
    name = models.CharField(max_length=100, verbose_name="학과명")
    
    # 예외 반영비율
    korean_ratio = models.IntegerField(null=True, blank=True, verbose_name="국어 반영비(예외)")
    math_ratio = models.IntegerField(null=True, blank=True, verbose_name="수학 반영비(예외)")
    inquiry_ratio = models.IntegerField(null=True, blank=True, verbose_name="탐구 반영비(예외)")

    english_method = models.CharField(
        max_length=10, 
        choices=University.ENGLISH_METHOD_CHOICES, 
        null=True, blank=True,
        verbose_name="영어 반영방식(예외)"
    )
    english_ratio = models.IntegerField(null=True, blank=True, verbose_name="영어 반영비(예외)")
    english_grade_points = models.JSONField(
        null=True, blank=True, 
        verbose_name="영어 등급별 점수표(예외)"
    )

    class Meta:
        unique_together = ('university', 'name')

    def __str__(self):
        return f"{self.university.name} {self.name}"

    # API 출력용 헬퍼
    @property
    def get_english_info(self):
        method = self.english_method or self.university.default_english_method
        if method == 'RATIO':
            ratio = self.english_ratio if self.english_ratio is not None else self.university.default_english_ratio
            return {"type": "RATIO", "value": ratio}
        else:
            points = self.english_grade_points if self.english_grade_points else self.university.default_english_grade_points
            return {"type": method, "table": points}


class AdmissionResult(models.Model):
    department = models.ForeignKey(UniversityDepartment, on_delete=models.CASCADE, related_name='admission_results', verbose_name="학과")
    year = models.IntegerField(verbose_name="학년도")
    recruit_count = models.IntegerField(null=True, blank=True, verbose_name="모집인원")
    
    # 과목별 상세 성적 (등급 / 백분위)
    korean_grade = models.FloatField(null=True, blank=True, verbose_name="국어 등급")
    korean_percentile = models.FloatField(null=True, blank=True, verbose_name="국어 백분위")
    
    math_grade = models.FloatField(null=True, blank=True, verbose_name="수학 등급")
    math_percentile = models.FloatField(null=True, blank=True, verbose_name="수학 백분위")
    
    english_grade = models.FloatField(null=True, blank=True, verbose_name="영어 등급")
    english_percentile = models.FloatField(null=True, blank=True, verbose_name="영어 백분위")
    
    inquiry_grade = models.FloatField(null=True, blank=True, verbose_name="탐구 등급")
    inquiry_percentile = models.FloatField(null=True, blank=True, verbose_name="탐구 백분위")

    total_average_grade = models.FloatField(null=True, blank=True, verbose_name="전체 평균 등급")

    class Meta:
        ordering = ['-year']
        unique_together = ('department', 'year')

    def __str__(self):
        return f"{self.department.name} ({self.year})"

    # 평균 백분위 자동 계산 로직
    @property
    def average_percentile(self):
        scores = [
            self.korean_percentile, 
            self.math_percentile, 
            self.english_percentile, 
            self.inquiry_percentile
        ]
        # None이 아닌 값만 필터링
        valid_scores = [s for s in scores if s is not None]
        
        if not valid_scores:
            return None
        
        # 평균 계산 및 반올림
        avg = sum(valid_scores) / len(valid_scores)
        return round(avg, 2)