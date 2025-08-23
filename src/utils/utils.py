# src/utils/utils.py
"""
유틸리티 함수 모듈
공통으로 사용되는 헬퍼 함수들
"""

import os
import platform
import urllib.request
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any
import json
from datetime import datetime

def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # 시스템별 기본 한글 폰트 경로
        system = platform.system()
        font_paths = []
        
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
                "C:/Windows/Fonts/gulim.ttc",   # 굴림
                "C:/Windows/Fonts/batang.ttc",  # 바탕
            ]
        elif system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/Library/Fonts/Arial Unicode MS.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/NanumGothic.ttf",
            ]
        
        # 폰트 파일 찾기 및 등록
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                    font_registered = True
                    print(f"한글 폰트 등록 성공: {font_path}")
                    break
                except Exception as e:
                    print(f"폰트 등록 실패 {font_path}: {e}")
                    continue
        
        if not font_registered:
            # 온라인에서 나눔고딕 다운로드 시도
            try:
                nanum_url = "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothic.ttf"
                font_data = urllib.request.urlopen(nanum_url).read()
                
                # 임시 파일로 저장
                temp_font_path = "temp_nanum.ttf"
                with open(temp_font_path, 'wb') as f:
                    f.write(font_data)
                
                pdfmetrics.registerFont(TTFont('KoreanFont', temp_font_path))
                font_registered = True
                print("나눔고딕 온라인 다운로드 및 등록 성공")
                
                # 임시 파일 삭제
                if os.path.exists(temp_font_path):
                    os.remove(temp_font_path)
                    
            except Exception as e:
                print(f"온라인 폰트 다운로드 실패: {e}")
        
        return font_registered
        
    except Exception as e:
        print(f"폰트 설정 중 오류 발생: {e}")
        return False

def safe_text_escape(text):
    """텍스트를 안전하게 HTML 이스케이프 처리"""
    if text is None:
        return 'N/A'
    
    # 다양한 데이터 타입을 문자열로 변환
    if isinstance(text, str):
        text_str = text
    elif isinstance(text, dict):
        # 딕셔너리인 경우 적절한 값 추출
        text_str = text.get('text', text.get('description', text.get('value', str(text))))
    elif isinstance(text, list):
        # 리스트인 경우 첫 번째 항목 사용 또는 전체를 문자열로
        text_str = str(text[0]) if text else ''
    else:
        text_str = str(text)
    
    # HTML 특수문자 이스케이프
    return text_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def check_azure_config() -> Dict[str, Any]:
    """Azure OpenAI 설정 확인"""
    # config 임포트를 함수 내부로 이동 (circular import 방지)
    from config.config import Config
    
    env_exists = os.path.exists('.env')
    
    required_vars = {
        'OPENAI_ENDPOINT': Config.AZURE_OPENAI_ENDPOINT,
        'OPENAI_KEY': Config.AZURE_OPENAI_KEY,
        'CHAT_MODEL3': Config.AZURE_DEPLOYMENT_NAME,
        'AZURE_OPENAI_API_VERSION': Config.AZURE_API_VERSION
    }
    
    configured_vars = {k: bool(v) for k, v in required_vars.items()}
    all_configured = all(configured_vars.values())
    
    return {
        'env_file_exists': env_exists,
        'azure_configured': all_configured,
        'configured_vars': configured_vars,
        'endpoint': Config.AZURE_OPENAI_ENDPOINT[:30] + '...' if Config.AZURE_OPENAI_ENDPOINT else None,
        'deployment_name': Config.AZURE_DEPLOYMENT_NAME
    }

def generate_statistics(questions: list) -> Dict[str, Any]:
    """문제 생성 통계"""
    stats = {
        "총_문제수": len(questions),
        "생성_일시": datetime.now().isoformat(),
        "문제_유형별_분포": {},
        "난이도별_분포": {},
        "과목별_분포": {},
        "시각적_요소_통계": {}
    }
    
    visual_count = 0
    visual_types = {}
    
    for question in questions:
        q_type = question.get('question_type', '미분류')
        stats["문제_유형별_분포"][q_type] = stats["문제_유형별_분포"].get(q_type, 0) + 1
        
        difficulty = question.get('difficulty', '미분류')
        stats["난이도별_분포"][difficulty] = stats["난이도별_분포"].get(difficulty, 0) + 1
        
        subject = question.get('subject_area', '미분류')
        subject_short = subject.split(' > ')[-1] if ' > ' in subject else subject
        stats["과목별_분포"][subject_short] = stats["과목별_분포"].get(subject_short, 0) + 1
        
        # 시각적 요소 통계
        if question.get('visual_image'):
            visual_count += 1
            visual_type = question.get('visual_type', '기타')
            visual_types[visual_type] = visual_types.get(visual_type, 0) + 1
    
    stats["시각적_요소_통계"] = {
        "시각적_문제수": visual_count,
        "텍스트_문제수": len(questions) - visual_count,
        "시각적_비율": round(visual_count / len(questions) * 100, 1) if questions else 0,
        "시각요소_유형별": visual_types
    }
    
    return stats

def cleanup_temp_files(temp_dir: str):
    """임시 파일들 정리"""
    try:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(temp_dir)
    except Exception as cleanup_error:
        print(f"임시 파일 정리 중 오류: {cleanup_error}")