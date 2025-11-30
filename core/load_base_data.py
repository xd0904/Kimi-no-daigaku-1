import os
import sys
import json
from pathlib import Path  # 경로 처리를 위한 Path 객체
import django
from django.db import connection, transaction
from django.core.serializers import deserialize
from django.core.exceptions import ObjectDoesNotExist

# ------------------------------------
# 1. Python Path 설정: manage.py가 있는 루트 경로를 sys.path에 추가
# 현재 스크립트 위치 (core/)에서 두 단계 위로 이동하여 프로젝트 루트 폴더 (Kimi-no-daigaku)를 찾습니다.
# Path(__file__).resolve() -> core/load_base_data.py
# .parent -> core/
# .parent -> Kimi-no-daigaku/ (프로젝트 루트)
BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))
# ------------------------------------

# -----------------
# 2. Django 환경 설정
# -----------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kimi_no_daigaku.settings') 
django.setup()

# -----------------
# 3. 로드할 파일 경로 설정
# -----------------
# 데이터 파일이 프로젝트 루트 폴더 (Kimi-no-daigaku)에 있다고 가정
DATA_FILE = BASE_DIR / '01_base_data.json'

def load_base_data():
    global DATA_FILE

    if not DATA_FILE.exists():
        print(f"Error: Data file not found at {DATA_FILE}")
        # 파일을 찾을 수 없으면 'core' 폴더 내부를 한 번 더 확인합니다.
        alt_data_file = Path(__file__).resolve().parent / '01_base_data.json'
        if alt_data_file.exists():
            DATA_FILE = alt_data_file
            print(f"Using alternative path: {DATA_FILE}")
        else:
            print("Please ensure '01_base_data.json' is in the project root or the 'core' folder.")
            return

    print(f"Loading data from {DATA_FILE}...")
    
    # 외래 키 제약 조건 비활성화 (SQLite용)
    with connection.cursor() as cursor:
        # 외래 키 검사를 끄기 전에 DB가 커밋할 수 있도록 보장
        connection.commit()
        cursor.execute('PRAGMA foreign_keys = OFF;')
        
    objects_loaded = 0
    try:
        # Django의 트랜잭션 내에서 데이터 로드 시도
        with transaction.atomic():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # JSON 데이터를 Django 객체로 역직렬화 및 저장
            for obj in deserialize("json", json.dumps(data)):
                try:
                    obj.save()
                    objects_loaded += 1
                except Exception as e:
                    print(f"Failed to save object: {obj.object.__class__.__name__} (PK: {obj.object.pk}) - Error: {e}")

        print(f"Successfully loaded {objects_loaded} objects.")
            
    except Exception as e:
        print(f"An error occurred during transaction: {e}")
        
    finally:
        # 외래 키 제약 조건 다시 활성화
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = ON;')
        print("Foreign key constraints re-enabled.")

if __name__ == '__main__':
    load_base_data()