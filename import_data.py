import os
import django
import pandas as pd
import glob
import unicodedata  # [추가] 유니코드 정규화용

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kimi_no_daigaku.settings')
django.setup()

from highschools.models import HighSchool, HighSchoolDepartment, StandardDepartment

def clean_region_name(raw_text):
    """지역명 전처리"""
    if pd.isna(raw_text) or raw_text == '':
        return None
    # 유니코드 정규화 (NFC)
    text = unicodedata.normalize('NFC', str(raw_text))
    text = text.replace('\n', '').replace(' ', '').strip()
    if not text.endswith('교육청'):
        text += '교육청'
    return text

def clean_standard_name(name):
    """
    [최종 수정] 기준학과명 강력 전처리
    1. 유니코드 정규화 (NFC)
    2. 모든 공백 제거 (특수 공백 포함)
    3. 모든 종류의 점(·) 통일
    """
    if not name:
        return None
    
    # 1. 문자열 변환 및 유니코드 정규화 (자모 분리 현상 해결)
    name = str(name)
    name = unicodedata.normalize('NFC', name)
    
    # 2. 모든 종류의 공백 제거 (일반 공백 + 특수 공백 \xa0 등)
    name = "".join(name.split())
    
    # 3. 쓰레기 데이터 필터링
    if name in ['-', 'ￚ', '–', '.', '', 'nan']:
        return None
        
    # 4. 모든 종류의 점을 표준 가운데 점(·)으로 치환
    # U+00B7(·), U+318D(ㆍ), U+FF65(･), U+2022(•), U+22C5(⋅)
    name = name.replace('･', '·').replace('•', '·').replace('ㆍ', '·').replace('.', '·').replace('⋅', '·')
    
    # 5. 매핑 테이블 (오타 및 관용적 표현 통일)
    mapping = {
        '경영사무과': '경영·사무과',
        '재무회계과': '재무·회계과',
        '방송통신과': '방송·통신과',
        '조리식음료과': '조리·식음료과',
        '관광레저과': '관광·레저과',
        '인쇄출판과': '인쇄·출판과',
        '건축촌목과': '건축·토목과',
        '조리･식음료과': '조리·식음료과', # 특수 점 케이스 명시
        '경영･사무과': '경영·사무과',
    }
    
    if name in mapping:
        name = mapping[name]
        
    return name

def run():
    xlsx_files = glob.glob('data/*.xlsx')
    if not xlsx_files:
        print("❌ data 폴더에 .xlsx 파일이 없습니다.")
        return

    target_file = xlsx_files[0]
    print(f"📂 파일 로드 중: {target_file}")

    try:
        all_sheets = pd.read_excel(target_file, sheet_name=None, header=4)
    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return
    
    collected_std_depts = set()

    print(f"총 {len(all_sheets)}개의 시트를 처리합니다.")

    for sheet_name, df in all_sheets.items():
        if '개요' in sheet_name:
            continue
            
        # 컬럼명 공백 제거
        df.columns = [str(c).strip() for c in df.columns]

        if '학교명' not in df.columns or '학과명' not in df.columns:
            continue

        df['학교명'] = df['학교명'].ffill()
        if '시 · 도 구분' in df.columns:
            df['시 · 도 구분'] = df['시 · 도 구분'].ffill()

        std_col_idx = -1
        for idx, col_name in enumerate(df.columns):
            if '기준학과' in col_name:
                std_col_idx = idx
                break
        
        for index, row in df.iterrows():
            school_name = row.get('학교명')
            dept_name = row.get('학과명')
            raw_region = row.get('시 · 도 구분')

            if pd.isna(school_name) or pd.isna(dept_name):
                continue
            
            if "특성화고등학교" in str(school_name) or "설립별" in str(school_name):
                continue

            region = clean_region_name(raw_region)
            if not region:
                region = clean_region_name(sheet_name)

            school, _ = HighSchool.objects.get_or_create(
                name=school_name,
                defaults={'region': region}
            )

            department, _ = HighSchoolDepartment.objects.get_or_create(
                school=school,
                name=dept_name
            )

            if std_col_idx != -1:
                val1 = row.iloc[std_col_idx]
                val2 = row.iloc[std_col_idx + 1] if (std_col_idx + 1) < len(df.columns) else None

                raw_stds = [val1, val2]

                for raw_val in raw_stds:
                    if pd.isna(raw_val):
                        continue
                    
                    # 1차 변환 (unicodedata 정규화 적용)
                    val_str = unicodedata.normalize('NFC', str(raw_val)).strip()
                    if val_str == '':
                        continue
                    
                    names = val_str.replace('\n', ',').split(',')
                    
                    for name in names:
                        clean_name = clean_standard_name(name)
                        
                        if not clean_name:
                            continue
                        
                        std_obj, _ = StandardDepartment.objects.get_or_create(name=clean_name)
                        department.standard_departments.add(std_obj)
                        
                        collected_std_depts.add(clean_name)

    print("\n" + "="*60)
    print("🎉 데이터 정제 완료!")
    print(f"📊 총 {len(collected_std_depts)}종류의 기준학과로 통합되었습니다.")
    print("="*60)
    
    sorted_depts = sorted(list(collected_std_depts))
    for i, name in enumerate(sorted_depts, 1):
        print(f"{i}. {name}")
    print("="*60)

if __name__ == '__main__':
    run()