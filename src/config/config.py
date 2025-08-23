# config.py
"""
설정 관리 모듈
환경변수, 상수, 기본 설정값들을 관리
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # Azure OpenAI 설정
    AZURE_OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')
    AZURE_OPENAI_KEY = os.getenv('OPENAI_KEY')
    AZURE_DEPLOYMENT_NAME = os.getenv('CHAT_MODEL3')
    AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # 애플리케이션 설정
    DEFAULT_QUESTION_COUNT = int(os.getenv('DEFAULT_QUESTION_COUNT', 50))
    DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 문제 유형별 기본 비율
    DEFAULT_RATIOS = {
        'multiple_choice': 60,
        'short_answer': 25,
        'essay': 15
    }
    
    # 난이도별 기본 비율
    DEFAULT_DIFFICULTY_RATIOS = {
        'easy': 50,
        'medium': 35,
        'hard': 15
    }
    
    # 시각적 문제 기본 비율
    DEFAULT_VISUAL_RATIO = 30
    
    # 과목 영역 리스트
    SUBJECT_AREAS = [
        "프로세스 모델링 – 설계 > 단위테스트 케이스 설계",
        "프로세스 모델링 – 분석 > 요구사항 정의",
        "프로세스 모델링 – 분석 > 인터페이스 정의",
        "프로세스 모델링 – 분석 > 개발방법론",
        "프로세스 모델링 – 설계 > 인터페이스 설계",
        "프로세스 모델링 – 설계 > MSA 서비스 설계",
        "프로세스 모델링 – 분석 > 화면정의",
        "데이터 모델링 – 데이터 모델링 > 물리데이터 모델링",
        "데이터 모델링 – 데이터 모델링 > 논리데이터 모델링",
        "데이터 모델링 – 데이터 표준화 > 데이터 표준관리",
        "데이터 모델링 – 데이터 표준화 > 데이터 표준화"
    ]
    
    @classmethod
    def is_azure_configured(cls) -> bool:
        """Azure OpenAI 설정 여부 확인"""
        return all([
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_KEY,
            cls.AZURE_DEPLOYMENT_NAME
        ])
    
    @classmethod
    def get_env_template(cls) -> str:
        """환경 설정 파일 템플릿 반환"""
        return """# Azure OpenAI 설정
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-azure-openai-api-key-here
CHAT_MODEL3=your-deployment-name

# API 버전 (선택사항)
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 기타 설정 (선택사항)
DEFAULT_QUESTION_COUNT=100

# 디버그 모드 (개발용)
DEBUG=False
"""