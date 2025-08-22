# question_generator.py
"""
최적화된 문제 생성 모듈
Azure OpenAI를 활용한 텍스트 문제 생성 + 시각적 문제 통합
"""

import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2
from openai import AzureOpenAI
import streamlit as st

from config import Config
from visual_generator import VisualQuestionGenerator, EnhancedBAQuestionGenerator

class BAQuestionGenerator:
    """Business Application 모델링 문제 생성기 (Azure OpenAI + 시각적 요소)"""
    
    def __init__(self, manual_config: Dict[str, str] = None):
        # Azure OpenAI 설정
        self._setup_azure_client(manual_config)
        
        # 시각적 요소 생성기 추가
        self.visual_gen = VisualQuestionGenerator()
        self.enhanced_gen = EnhancedBAQuestionGenerator()
        
        # 시각적 문제 비율 설정
        self.visual_question_ratio = 0.3  # 전체 문제의 30%를 시각적 문제로
        
        self.source_content = ""
        self.question_types = {
            "선다형": ["multiple_choice", 60],
            "단답형": ["short_answer", 25],
            "서술형": ["essay", 15]
        }
        self.difficulty_levels = ["하", "중", "상"]
    
    def _setup_azure_client(self, manual_config: Dict[str, str] = None):
        """Azure OpenAI 클라이언트 설정"""
        # 설정값 결정 (수동 입력 > 환경변수)
        if manual_config:
            azure_endpoint = manual_config.get('endpoint')
            api_key = manual_config.get('api_key')
            api_version = manual_config.get('api_version', Config.AZURE_API_VERSION)
            deployment_name = manual_config.get('deployment_name')
        else:
            azure_endpoint = Config.AZURE_OPENAI_ENDPOINT
            api_key = Config.AZURE_OPENAI_KEY
            api_version = Config.AZURE_API_VERSION
            deployment_name = Config.AZURE_DEPLOYMENT_NAME
        
        if azure_endpoint and api_key and deployment_name:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=api_key,
                    api_version=api_version
                )
                self.deployment_name = deployment_name
                self.api_configured = True
                
                # 연결 테스트
                self._test_connection()
                
            except Exception as e:
                st.error(f"Azure OpenAI 초기화 오류: {e}")
                self.client = None
                self.api_configured = False
        else:
            self.client = None
            self.api_configured = False
    
    def _test_connection(self):
        """Azure OpenAI 연결 테스트"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            st.warning(f"Azure OpenAI 연결 테스트 실패: {e}")
            return False
    
    def should_generate_visual_question(self, subject_area: str) -> bool:
        """특정 과목 영역에서 시각적 문제를 생성할지 결정"""
        visual_subjects = [
            "데이터 모델링",
            "프로세스 모델링 – 설계",
            "인터페이스 설계",
            "MSA 서비스 설계",
            "화면정의"
        ]
        
        # 해당 과목이 시각적 요소가 필요한 영역인지 확인
        for visual_subject in visual_subjects:
            if visual_subject in subject_area:
                return random.random() < self.visual_question_ratio
        
        return False
    
    def extract_pdf_content(self, uploaded_file) -> str:
        """업로드된 PDF에서 텍스트 추출"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            self.source_content = content
            return content
        except Exception as e:
            st.error(f"PDF 읽기 오류: {e}")
            return ""
    
    def create_question_prompt(self, question_type: str, subject_area: str, difficulty: str) -> str:
        """문제 생성을 위한 프롬프트 생성"""
        
        base_prompt = f"""
당신은 Business Application 모델링 분야의 전문 출제자입니다.
다음 학습자료를 바탕으로 실무에 적용 가능한 고품질 문제를 생성해주세요.

**학습자료:**
{self.source_content[:4000]}

**문제 요구사항:**
- 문제유형: {question_type}
- 출제영역: {subject_area}
- 난이도: {difficulty}
- 실무 적용 가능한 현실적 시나리오 기반
- 명확하고 정확한 정답과 해설 제공

"""
        
        if question_type == "선다형":
            specific_prompt = """
**선다형 문제 형식:**
- 5개의 선택지(① ~⑤) 제공
- 정답은 1개만 존재
- 각 선택지는 명확하게 구분되는 내용
- 헷갈리기 쉬운 오답 포함

**출력 형식 (JSON):**
{
    "question_type": "선다형",
    "subject_area": "출제영역",
    "difficulty": "난이도",
    "title": "문제 제목",
    "scenario": "문제 시나리오/배경",
    "question": "질문 내용",
    "choices": ["① 선택지1", "② 선택지2", "③ 선택지3", "④ 선택지4", "⑤ 선택지5"],
    "correct_answer": "정답 번호",
    "explanation": "정답 해설",
    "points": "배점"
}
"""
        elif question_type == "단답형":
            specific_prompt = """
**단답형 문제 형식:**
- 간단명료한 답안 요구
- 여러 정답 가능한 경우 모두 명시
- 채점 기준 명확히 제시

**출력 형식 (JSON):**
{
    "question_type": "단답형",
    "subject_area": "출제영역",
    "difficulty": "난이도",
    "title": "문제 제목",
    "scenario": "문제 시나리오/배경",
    "question": "질문 내용",
    "correct_answer": "정답",
    "alternative_answers": ["대안 정답1", "대안 정답2"],
    "explanation": "정답 해설",
    "points": "배점"
}
"""
        else:
            specific_prompt = """
**서술형 문제 형식:**
- 깊이 있는 이해와 분석 능력 평가
- 논리적 설명과 실무 적용 방안 요구
- 채점 기준과 모범답안 제시

**출력 형식 (JSON):**
{
    "question_type": "서술형",
    "subject_area": "출제영역",
    "difficulty": "난이도",
    "title": "문제 제목",
    "scenario": "문제 시나리오/배경",
    "question": "질문 내용",
    "model_answer": "모범 답안",
    "grading_criteria": ["채점 기준1", "채점 기준2", "채점 기준3"],
    "explanation": "문제 의도 및 해설",
    "points": "배점"
}
"""
        
        return base_prompt + specific_prompt
    
    def generate_single_question(self, question_type: str, subject_area: str, difficulty: str) -> Dict[str, Any]:
        """단일 문제 생성 (기존 텍스트 문제)"""
        if not self.client:
            return self.generate_fallback_question(question_type, subject_area, difficulty)
            
        prompt = self.create_question_prompt(question_type, subject_area, difficulty)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "당신은 IT 교육 전문가이며 고품질 시험문제 출제 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # JSON 부분만 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                question_data = json.loads(json_text)
                
                # 메타데이터 추가
                question_data["generated_at"] = datetime.now().isoformat()
                question_data["question_id"] = f"BA_{random.randint(1000, 9999)}"
                
                return question_data
            else:
                raise ValueError("JSON 형식이 아닌 응답")
                
        except Exception as e:
            st.warning(f"문제 생성 오류: {e}")
            return self.generate_fallback_question(question_type, subject_area, difficulty)
    
    def generate_single_question_enhanced(self, question_type: str, subject_area: str, difficulty: str) -> Dict[str, Any]:
        """시각적 요소를 포함할 수 있는 문제 생성"""
        
        # 시각적 문제를 생성할지 결정
        if self.should_generate_visual_question(subject_area):
            return self.generate_visual_question_by_subject(question_type, subject_area, difficulty)
        else:
            # 기존 텍스트 문제 생성
            return self.generate_single_question(question_type, subject_area, difficulty)
    
    def generate_visual_question_by_subject(self, question_type: str, subject_area: str, difficulty: str) -> Dict[str, Any]:
        """과목 영역에 따른 시각적 문제 생성"""
        
        if "데이터 모델링" in subject_area:
            if "논리데이터" in subject_area:
                return self.enhanced_gen.generate_visual_question('erd_analysis', difficulty)
            elif "물리데이터" in subject_area:
                return self.enhanced_gen.generate_visual_question('table_normalization', difficulty)
            else:
                # 랜덤하게 ERD 또는 테이블 문제
                template = random.choice(['erd_analysis', 'table_normalization'])
                return self.enhanced_gen.generate_visual_question(template, difficulty)
        
        elif "프로세스 모델링" in subject_area:
            if "설계" in subject_area:
                return self.enhanced_gen.generate_visual_question('uml_design', difficulty)
            else:
                # 플로우차트 기반 문제 생성
                return self._generate_process_flow_question(question_type, difficulty)
        
        elif "인터페이스" in subject_area or "화면정의" in subject_area:
            return self._generate_ui_design_question(question_type, difficulty)
        
        else:
            # 기본 텍스트 문제로 폴백
            return self.generate_single_question(question_type, subject_area, difficulty)
    
    def _generate_process_flow_question(self, question_type: str, difficulty: str) -> Dict[str, Any]:
        """프로세스 플로우 기반 문제 생성 (간소화된 버전)"""
        # 기본적인 프로세스 시나리오
        scenario = {
            'title': '주문 처리 프로세스',
            'steps': [
                {'type': 'start', 'text': '주문 접수'},
                {'type': 'process', 'text': '재고 확인'},
                {'type': 'decision', 'text': '재고 충분?'},
                {'type': 'process', 'text': '결제 처리'},
                {'type': 'end', 'text': '주문 완료'}
            ]
        }
        
        # 플로우차트 이미지 생성
        image_base64 = self.visual_gen.generate_flowchart(scenario['steps'])
        
        # 기본 문제 데이터
        question_data = {
            'question_id': f"FLOW_{random.randint(1000, 9999)}",
            'title': scenario['title'],
            'scenario': f"다음은 {scenario['title']} 플로우차트입니다.",
            'question_type': question_type,
            'question': '이 프로세스에서 첫 번째 의사결정 단계는?',
            'difficulty': difficulty,
            'subject_area': "프로세스 모델링 – 설계 > 업무 프로세스 설계",
            'visual_type': 'flowchart',
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '4' if difficulty == '중' else '3' if difficulty == '하' else '5'
        }
        
        # 문제 유형에 따른 답안 설정
        if question_type == '선다형':
            question_data.update({
                'choices': ['① 주문 접수', '② 재고 확인', '③ 재고 충분?', '④ 결제 처리', '⑤ 주문 완료'],
                'correct_answer': '③',
                'explanation': '의사결정 단계는 다이아몬드 모양으로 표시되며, 이 프로세스에서는 "재고 충분?" 단계가 첫 번째 의사결정 포인트입니다.'
            })
        
        return question_data
    
    def _generate_ui_design_question(self, question_type: str, difficulty: str) -> Dict[str, Any]:
        """UI 설계 문제 생성 (간소화된 버전)"""
        # 기본 UI 컴포넌트
        components = [
            {'type': 'label', 'x': 2, 'y': 5.5, 'width': 1, 'height': 0.3, 'text': '사용자 등록'},
            {'type': 'input', 'x': 3, 'y': 4.8, 'width': 3, 'height': 0.5, 'placeholder': '이름을 입력하세요'},
            {'type': 'button', 'x': 3, 'y': 2.5, 'width': 1.5, 'height': 0.5, 'text': '등록'}
        ]
        
        # UI 목업 이미지 생성
        image_base64 = self.visual_gen.generate_ui_mockup(components)
        
        # 문제 데이터 구성
        question_data = {
            'question_id': f"UI_{random.randint(1000, 9999)}",
            'title': '사용자 등록 화면 설계',
            'scenario': "다음은 사용자 등록 화면 목업입니다.",
            'question_type': question_type,
            'question': '이 화면에서 개선이 필요한 UI 요소는?',
            'difficulty': difficulty,
            'subject_area': "프로세스 모델링 – 분석 > 화면정의",
            'visual_type': 'ui_mockup',
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '4' if difficulty == '중' else '3' if difficulty == '하' else '5'
        }
        
        # 문제 유형에 따른 답안 설정
        if question_type == '선다형':
            question_data.update({
                'choices': [
                    '① 이름 입력 필드가 너무 작음',
                    '② 비밀번호 확인 필드 누락',
                    '③ 등록 버튼이 너무 작음',
                    '④ 이메일 형식 검증 표시 없음',
                    '⑤ 모든 요소가 적절함'
                ],
                'correct_answer': '②',
                'explanation': '사용자 등록 화면에서는 비밀번호 확인 필드가 반드시 필요합니다. 비밀번호 입력 실수를 방지하기 위한 필수 요소입니다.'
            })
        
        return question_data
    
    def generate_fallback_question(self, question_type: str, subject_area: str, difficulty: str) -> Dict[str, Any]:
        """오류 시 대체 문제 생성"""
        fallback_questions = {
            "선다형": {
                "question": "다음 중 소프트웨어 개발 생명주기 모델이 아닌 것은?",
                "choices": ["① 폭포수 모델", "② 나선형 모델", "③ 애자일 모델", "④ V 모델", "⑤ 관계형 모델"],
                "correct_answer": "⑤",
                "explanation": "관계형 모델은 데이터베이스 설계 모델이며, 소프트웨어 개발 생명주기 모델이 아닙니다."
            },
            "단답형": {
                "question": "요구사항 분석 단계에서 이해관계자의 요구사항을 수집하고 분석하는 과정을 무엇이라고 하는가?",
                "correct_answer": "요구사항 도출",
                "explanation": "요구사항 도출(Requirements Elicitation)은 이해관계자로부터 요구사항을 수집하고 명확화하는 과정입니다."
            },
            "서술형": {
                "question": "애자일 개발방법론의 특징과 장단점에 대해 서술하시오.",
                "model_answer": "애자일 개발방법론은 빠른 반복과 지속적인 피드백을 통해 소프트웨어를 개발하는 방법론입니다...",
                "grading_criteria": ["애자일의 핵심 특징 설명", "장점 2개 이상 서술", "단점 1개 이상 서술"]
            }
        }
        
        base_data = fallback_questions.get(question_type, fallback_questions["선다형"])
        
        return {
            "question_type": question_type,
            "subject_area": subject_area,
            "difficulty": difficulty,
            "title": f"{question_type} 문제",
            "scenario": "일반적인 업무 상황",
            "question_id": f"FALLBACK_{random.randint(1000, 9999)}",
            "generated_at": datetime.now().isoformat(),
            "points": "3" if difficulty == "하" else "4" if difficulty == "중" else "5",
            **base_data
        }