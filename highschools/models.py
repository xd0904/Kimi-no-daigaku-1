from django.db import models

class StandardDepartment(models.Model):
    """
    기준학과 (예: 정보컴퓨터, 회계세무, 디자인 등)
    - 엑셀의 '기준학과1', '기준학과2' 데이터를 이곳에 유니크하게 모읍니다.
    - 나중에 대학 학과(UniversityDepartment)와 연결되는 핵심 고리입니다.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="기준학과명")

    def __str__(self):
        return self.name


class HighSchool(models.Model):
    """
    특성화고 정보 (예: 서울공업고등학교)
    """
    region = models.CharField(max_length=50, verbose_name="시도교육청")  # 예: 서울특별시교육청
    name = models.CharField(max_length=100, unique=True, verbose_name="학교명")

    def __str__(self):
        return self.name


class HighSchoolDepartment(models.Model):
    """
    특성화고 개별 학과 (예: 서울공고 - AI소프트웨어과)
    """
    school = models.ForeignKey(HighSchool, on_delete=models.CASCADE, related_name='departments', verbose_name="소속 학교")
    name = models.CharField(max_length=100, verbose_name="학과명")
    
    # 한 학과는 최대 2개의 기준학과를 가질 수 있으므로 ManyToMany 관계 설정
    standard_departments = models.ManyToManyField(
        StandardDepartment, 
        related_name='high_school_departments',
        verbose_name="매핑된 기준학과"
    )

    class Meta:
        # 학교 내에서 학과명은 중복될 수 없으므로 유니크 제약 조건 추가
        unique_together = ('school', 'name')

    def __str__(self):
        return f"{self.school.name} - {self.name}"