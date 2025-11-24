import os
import django
import pandas as pd
import glob

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kimi_no_daigaku.settings')
django.setup()

from highschools.models import HighSchool, HighSchoolDepartment, StandardDepartment

def clean_region_name(raw_text):
    """지역명 전처리 (줄바꿈/공백 제거, '교육청' 붙이기)"""
    if pd.isna(raw_text) or raw_text == '':
        return None
    text = str(raw_text).replace('\n', '').replace(' ', '').strip()
    if not text.endswith('교육청'):
        text += '교육청'
    return text

def run():
    xlsx_files = glob.glob('data/*.xlsx')
    if not xlsx_files:
        print("❌ data 폴더에 .xlsx 파일이 없습니다.")
        return

    target_file = xlsx_files[0]
    print(f"📂 파일 로드 중: {target_file}")

    try:
        # header=4: 5번째 줄을 헤더로 인식
        all_sheets = pd.read_excel(target_file, sheet_name=None, header=4)
    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return

    print(f"총 {len(all_sheets)}개의 시트를 처리합니다.")

    for sheet_name, df in all_sheets.items():
        if '개요' in sheet_name:
            continue
            
        # 컬럼명 앞뒤 공백 제거
        df.columns = [str(c).strip() for c in df.columns]

        # 필수 컬럼 확인
        if '학교명' not in df.columns or '학과명' not in df.columns:
            continue

        # [핵심 수정 1] 셀 병합 문제 해결: 위쪽 데이터로 빈 칸 채우기 (Forward Fill)
        # 학교명과 시도구분 컬럼의 NaN 값을 바로 위 행의 값으로 채웁니다.
        df['학교명'] = df['학교명'].ffill()
        if '시 · 도 구분' in df.columns:
            df['시 · 도 구분'] = df['시 · 도 구분'].ffill()

        # [핵심 수정 2] 기준학과 컬럼 위치 찾기 (인덱스로 접근)
        # '기준학과'가 포함된 첫 번째 컬럼의 위치(index)를 찾습니다.
        std_col_idx = -1
        for idx, col_name in enumerate(df.columns):
            if '기준학과' in col_name:
                std_col_idx = idx
                break
        
        for index, row in df.iterrows():
            school_name = row.get('학교명')
            dept_name = row.get('학과명')
            raw_region = row.get('시 · 도 구분')

            # ffill을 했으므로 이제 school_name이 비어있으면 진짜 데이터가 없는 행
            if pd.isna(school_name) or pd.isna(dept_name):
                continue
            
            # 중간 제목 행(예: '국립', '공립' 등) 스킵
            if "특성화고등학교" in str(school_name) or "설립별" in str(school_name):
                continue

            # 지역명 정제
            region = clean_region_name(raw_region)
            if not region:
                region = clean_region_name(sheet_name)

            # 학교 생성
            school, _ = HighSchool.objects.get_or_create(
                name=school_name,
                defaults={'region': region}
            )

            # 학과 생성
            department, _ = HighSchoolDepartment.objects.get_or_create(
                school=school,
                name=dept_name
            )

            # [핵심 수정 3] 기준학과 2개 열 모두 확인
            if std_col_idx != -1:
                # 기준학과 1 (원래 찾은 컬럼)
                val1 = row.iloc[std_col_idx]
                # 기준학과 2 (바로 오른쪽 옆 컬럼)
                # 인덱스 범위를 벗어나지 않는지 확인
                val2 = row.iloc[std_col_idx + 1] if (std_col_idx + 1) < len(df.columns) else None

                # 처리할 값 리스트
                raw_stds = [val1, val2]

                for raw_val in raw_stds:
                    if pd.isna(raw_val):
                        continue
                        
                    val_str = str(raw_val).strip()
                    if val_str == '':
                        continue
                    
                    # 혹시 모를 콤마/줄바꿈 분리 (대부분은 이제 1개씩 들어올 것임)
                    names = val_str.replace('\n', ',').split(',')
                    for name in names:
                        name = name.strip()
                        if not name:
                            continue
                        
                        # 기준학과 DB 연결
                        std_obj, _ = StandardDepartment.objects.get_or_create(name=name)
                        department.standard_departments.add(std_obj)

    print("✅ 데이터 입력 완료! 이제 빠진 학과와 기준학과가 모두 들어갔습니다. 🎉")

if __name__ == '__main__':
    run()