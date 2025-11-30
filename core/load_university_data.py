# core/load_university_data.py

import os
import django
import sys 
import json
from pathlib import Path

# --- Django 환경 설정 경로 추가 ---
# 이 경로는 Django 환경 설정을 위해 필요합니다.
current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kimi_no_daigaku.settings')
django.setup()

# -------------------------------------------------------------------------
# 🚨 모델 임포트 및 유효성 검사
# -------------------------------------------------------------------------

# core/models.py에 정의된 모델 임포트
from core.models import DepartmentAdmission, AdmissionResult 

try:
    # 🌟 이 부분이 문제의 원인이었습니다. 이 경로가 실제 모델의 위치여야 합니다.
    from universities.models import University, UniversityDivision, Department 
except ImportError as e:
    # 임포트 오류가 발생하면 사용자에게 정확한 진단 메시지를 제공합니다.
    print("\n======================================================================")
    print("❌ 치명적인 오류: 필수 대학 모델 임포트 실패!")
    print(f"오류 메시지: {e}")
    print("----------------------------------------------------------------------")
    print("💡 해결 방법:")
    print("   1. **`universities/models.py`** 파일 안에 **`University`**, **`UniversityDivision`**,"
          " **`Department`** 세 모델이 모두 **오류 없이** 정의되어 있는지 확인하세요.")
    print("   2. 만약 모델들이 다른 앱에 있다면, **`from universities.models`** 대신 "
          "해당 앱 경로로 코드를 수정해야 합니다.")
    print("======================================================================\n")
    sys.exit(1)

# universities_data.json 파일 경로 설정
DATA_FILE = Path(__file__).resolve().parent.parent / 'universities_data.json' 


def load_university_data_script():
    """
    universities_data.json을 읽어 DB에 저장하는 메인 함수
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
        # 현재 처리 중인 항목의 PK를 이용해 로그 메시지를 명확히 합니다.
        # JSON 데이터가 PK(정수) 형태라고 가정합니다.
        item_info = f"PKs: U({item.get('university')}), D({item.get('department')}), V({item.get('division')})"
        
        try:
            # 1. PK 값으로 객체를 조회하여 '이름' 문자열을 가져옴
            # DepartmentAdmission 필드가 CharField이므로, 이름 문자열을 저장합니다.
            
            # 🚨 주의: 이 시점에서 해당 PK를 가진 데이터가 DB에 미리 로드되어 있어야 합니다.
            university_name = University.objects.get(pk=item['university']).name
            department_name = Department.objects.get(pk=item['department']).name 
            division_name = UniversityDivision.objects.get(pk=item['division']).name
            
            # 2. DepartmentAdmission 객체 생성 및 저장
            # university와 department 필드를 기준으로 고유성을 체크합니다.
            dept_obj, created = DepartmentAdmission.objects.get_or_create(
                university=university_name, 
                department=department_name, 
                defaults={
                    'division': division_name,
                    'recruitment_group': item['recruitment_group'],
                    'standards_json': item['standards'],
                    'scoring_json': item['scoring'],
                }
            )
            
            # 기존 데이터가 있으면 AdmissionResult만 삭제하고 새로 만듭니다.
            if not created:
                AdmissionResult.objects.filter(department=dept_obj).delete()

            # 3. AdmissionResult 객체들 생성 및 저장
            for result in item['results']:
                AdmissionResult.objects.create(
                    department=dept_obj,
                    year=result['year'],
                    quota=result['quota'],
                    korean_grade=result['korean_grade'],
                    korean_percentile=result['korean_percentile'],
                    math_grade=result['math_grade'],
                    math_percentile=result['math_percentile'],
                    english_grade=result['english_grade'],
                    inquiry_grade=result['inquiry_grade'],
                    inquiry_percentile=result['inquiry_percentile'],
                )
            
            count += 1
            if (i + 1) % 10 == 0 or (i + 1) == total_items:
                print(f"   ... 진행률: {i + 1}/{total_items} 처리 완료.")

        except University.DoesNotExist:
             print(f"❌ 데이터 저장 실패 ({item_info}): 'University' PK {item['university']} 가 DB에 없습니다.")
        except Department.DoesNotExist:
             print(f"❌ 데이터 저장 실패 ({item_info}): 'Department' PK {item['department']} 가 DB에 없습니다.")
        except UniversityDivision.DoesNotExist:
             print(f"❌ 데이터 저장 실패 ({item_info}): 'UniversityDivision' PK {item['division']} 가 DB에 없습니다.")
        except Exception as e:
             # 다른 유형의 오류 (예: 필드 길이 초과, 데이터 타입 불일치 등)
             print(f"⚠️ 데이터 저장 중 일반 오류 발생 ({item_info}): {e}")
            
    print(f"✅ 대학 데이터 로드 완료. 총 {count}개 학과 처리.")
    return count

# 이 파일이 직접 실행될 때만 함수를 호출합니다.
if __name__ == '__main__':
    load_university_data_script()