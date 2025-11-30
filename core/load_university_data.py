# core/load_university_data.py (최종 수정)

import os
import django
import sys 
import json
from pathlib import Path

# --- BASE_DIR 및 Python Path 설정 ---
BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kimi_no_daigaku.settings')
django.setup()

# -------------------------------------------------------------------------
# 🚨 모델 임포트 및 유효성 검사
# -------------------------------------------------------------------------

# core/models.py에 정의된 모델 임포트
from core.models import DepartmentAdmission, AdmissionResult 

try:
    from universities.models import University, UniversityDivision, UniversityDepartment 
except ImportError as e:
    print("\n======================================================================")
    print("❌ 치명적인 오류: 필수 대학 모델 임포트 실패!")
    print(f"오류 메시지: {e}")
    print("======================================================================\n")
    sys.exit(1)

# 03_admission.json 파일 경로 설정
DATA_FILE = BASE_DIR / '03_admission.json'


def load_university_data_script():
    """
    03_admission.json (AdmissionResult Fixture 형식)을 읽어 DB에 저장하는 메인 함수
    """
    if not DATA_FILE.exists():
        print(f"❌ JSON 파일이 경로에 없습니다: {DATA_FILE}")
        return 0

    print("📄 대학 입시 결과 데이터 로드 중...")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ JSON 파일 읽기 실패: {e}")
        return 0

    count = 0
    total_items = len(data)

    for i, item in enumerate(data):
        
        fields = item.get('fields', {}) 
        department_pk = fields.get('department')
        item_info = f"PKs: D({department_pk})" 

        try:
            if not department_pk:
                raise KeyError("'department' 키가 누락되었거나 None입니다.")
            
            # 1. UniversityDepartment 객체 조회
            department_obj = UniversityDepartment.objects.get(pk=department_pk)
            
            # ⭐️⭐️⭐️ UniversityDivision을 경유하여 University 정보를 가져옵니다. ⭐️⭐️⭐️
            university_name = department_obj.division.university.name 
            division_name = department_obj.division.name 
            department_name = department_obj.name
            
            # 2. DepartmentAdmission 객체 생성/가져오기
            dept_obj, created = DepartmentAdmission.objects.get_or_create(
                university=university_name, 
                department=department_name, 
                division=division_name, 
                defaults={
                    'recruitment_group': department_obj.recruitment_group, # UniversityDepartment의 모집군 사용
                    'standards_json': department_obj.get_final_info['standards'],
                    'scoring_json': department_obj.get_final_info['scores'], # 예시로 get_final_info를 사용해봅니다.
                }
            )
            
            # 3. AdmissionResult 객체 생성 및 저장
            fields.pop('pk', None)
            fields['department'] = dept_obj 

            # ⭐️⭐️⭐️ 이 부분을 아래와 같이 수정합니다. ⭐️⭐️⭐️
            recruit_count_value = fields.pop('recruit_count', 0)

            # 값이 None인 경우 0으로 강제 변환합니다.
            fields['quota'] = recruit_count_value if recruit_count_value is not None else 0
            
            AdmissionResult.objects.create(**fields)
            
            count += 1
            if (i + 1) % 10 == 0 or (i + 1) == total_items:
                print(f"    ... 진행률: {i + 1}/{total_items} 처리 완료.")

        except UniversityDepartment.DoesNotExist:
            print(f"❌ 데이터 저장 실패 ({item_info}): 'UniversityDepartment' PK {department_pk} 가 DB에 없습니다. ⚠️ 선행 데이터 로드를 확인하세요.")
        except AttributeError as e:
            # UniversityDepartment.objects.get(pk=department_pk) 객체는 찾았으나, 
            # .division 이나 .university 필드에 접근 실패 시
            print(f"❌ 데이터 저장 실패 ({item_info}): 모델 연결 오류: {e} ⚠️ UniversityDepartment 모델의 FK 필드 경로를 확인하세요.")
        except KeyError as e:
            print(f"❌ 데이터 저장 실패 ({item_info}): JSON 키 오류: {e}")
        except Exception as e:
            print(f"⚠️ 데이터 저장 중 일반 오류 발생 ({item_info}): {e}")
            
    print(f"✅ 대학 데이터 로드 완료. 총 {count}개 학과 처리.")
    return count

# 이 파일이 직접 실행될 때만 함수를 호출합니다.
if __name__ == '__main__':
    load_university_data_script()