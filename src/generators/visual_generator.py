# visual_generator.py
"""
시각적 요소 생성 모듈
matplotlib를 활용한 ERD, UML, 플로우차트 등 생성
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import random
from datetime import datetime
from typing import List, Dict, Any

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'AppleGothic', 'Noto Sans CJK KR', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class VisualQuestionGenerator:
    """시각적 문제 생성기"""
    
    def __init__(self):
        self.dpi = 150
        self.figsize = (10, 8)
    
    def generate_erd_diagram(self, entities: List[Dict]) -> str:
        """ERD 다이어그램 생성"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # 엔티티 배치
        positions = [(2, 6), (8, 6), (2, 2), (8, 2)]
        
        for i, entity in enumerate(entities[:4]):
            if i < len(positions):
                x, y = positions[i]
                
                # 엔티티 박스 그리기
                rect = FancyBboxPatch(
                    (x-1, y-1), 2, 1.5,
                    boxstyle="round,pad=0.1",
                    facecolor='lightblue',
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
                
                # 엔티티 이름
                ax.text(x, y+0.3, entity['name'], 
                       ha='center', va='center', fontsize=12, fontweight='bold')
                
                # 속성들
                attrs = entity.get('attributes', [])[:3]  # 최대 3개만
                for j, attr in enumerate(attrs):
                    ax.text(x, y-0.2-j*0.2, f"• {attr}", 
                           ha='center', va='center', fontsize=9)
        
        # 관계선 그리기 (간단한 예시)
        if len(entities) >= 2:
            ax.annotate('', xy=(7, 6.5), xytext=(3, 6.5),
                       arrowprops=dict(arrowstyle='-', lw=2, color='red'))
            ax.text(5, 6.8, '1:N', ha='center', va='center', 
                   fontsize=10, color='red', fontweight='bold')
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Entity Relationship Diagram', fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_table_diagram(self, table_data: Dict) -> str:
        """테이블 정규화 다이어그램 생성"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # 테이블 헤더
        title = table_data.get('title', '데이터 테이블')
        columns = table_data.get('columns', [])
        rows = table_data.get('rows', [])
        
        # 테이블 그리기
        table_height = len(rows) + 1
        table_width = len(columns)
        
        # 헤더 행
        for i, col in enumerate(columns):
            rect = Rectangle((i, table_height-1), 1, 1, 
                           facecolor='lightgray', edgecolor='black')
            ax.add_patch(rect)
            ax.text(i+0.5, table_height-0.5, col, 
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        # 데이터 행
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                if col_idx < len(columns):
                    rect = Rectangle((col_idx, table_height-2-row_idx), 1, 1,
                                   facecolor='white', edgecolor='black')
                    ax.add_patch(rect)
                    ax.text(col_idx+0.5, table_height-1.5-row_idx, str(cell), 
                           ha='center', va='center', fontsize=9)
        
        ax.set_xlim(-0.5, table_width+0.5)
        ax.set_ylim(-0.5, table_height+0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_uml_diagram(self, classes: List[Dict]) -> str:
        """UML 클래스 다이어그램 생성"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        positions = [(2, 6), (8, 6), (2, 2), (8, 2)]
        
        for i, cls in enumerate(classes[:4]):
            if i < len(positions):
                x, y = positions[i]
                
                # 클래스 박스
                rect = FancyBboxPatch(
                    (x-1.5, y-1.5), 3, 2.5,
                    boxstyle="round,pad=0.1",
                    facecolor='lightyellow',
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
                
                # 클래스 이름
                ax.text(x, y+0.8, cls['name'], 
                       ha='center', va='center', fontsize=11, fontweight='bold')
                
                # 구분선
                ax.plot([x-1.4, x+1.4], [y+0.4, y+0.4], 'k-', linewidth=1)
                
                # 속성
                attrs = cls.get('attributes', [])[:2]
                for j, attr in enumerate(attrs):
                    ax.text(x, y+0.1-j*0.2, f"- {attr}", 
                           ha='center', va='center', fontsize=9)
                
                # 구분선
                if attrs:
                    ax.plot([x-1.4, x+1.4], [y-0.2, y-0.2], 'k-', linewidth=1)
                
                # 메소드
                methods = cls.get('methods', [])[:2]
                for j, method in enumerate(methods):
                    ax.text(x, y-0.5-j*0.2, f"+ {method}", 
                           ha='center', va='center', fontsize=9)
        
        # 상속/연관 관계 (예시)
        if len(classes) >= 2:
            ax.annotate('', xy=(7, 6), xytext=(3, 6),
                       arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('UML Class Diagram', fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_flowchart(self, steps: List[Dict]) -> str:
        """플로우차트 생성"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        y_positions = np.linspace(7, 1, len(steps))
        
        for i, step in enumerate(steps):
            y = y_positions[i]
            step_type = step.get('type', 'process')
            text = step.get('text', f'Step {i+1}')
            
            if step_type == 'start' or step_type == 'end':
                # 원형 (시작/끝)
                circle = plt.Circle((5, y), 0.5, facecolor='lightgreen', 
                                  edgecolor='black', linewidth=2)
                ax.add_patch(circle)
            elif step_type == 'decision':
                # 다이아몬드 (판단)
                diamond = patches.RegularPolygon((5, y), 4, radius=0.6, 
                                               orientation=np.pi/4,
                                               facecolor='lightcoral', 
                                               edgecolor='black', linewidth=2)
                ax.add_patch(diamond)
            else:
                # 사각형 (처리)
                rect = FancyBboxPatch(
                    (4, y-0.3), 2, 0.6,
                    boxstyle="round,pad=0.05",
                    facecolor='lightblue',
                    edgecolor='black',
                    linewidth=2
                )
                ax.add_patch(rect)
            
            # 텍스트
            ax.text(5, y, text, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
            
            # 화살표 (마지막 단계가 아닌 경우)
            if i < len(steps) - 1:
                ax.annotate('', xy=(5, y_positions[i+1]+0.5), xytext=(5, y-0.5),
                           arrowprops=dict(arrowstyle='->', lw=2, color='black'))
        
        ax.set_xlim(2, 8)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Process Flowchart', fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_ui_mockup(self, components: List[Dict]) -> str:
        """UI 목업 생성"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # 배경 (디바이스 화면)
        bg_rect = Rectangle((1, 1), 8, 6, facecolor='white', 
                          edgecolor='black', linewidth=3)
        ax.add_patch(bg_rect)
        
        for comp in components:
            x = comp.get('x', 1)
            y = comp.get('y', 1)
            width = comp.get('width', 1)
            height = comp.get('height', 0.5)
            comp_type = comp.get('type', 'button')
            text = comp.get('text', '')
            
            if comp_type == 'button':
                rect = FancyBboxPatch(
                    (x, y), width, height,
                    boxstyle="round,pad=0.02",
                    facecolor='lightblue',
                    edgecolor='darkblue',
                    linewidth=1
                )
                ax.add_patch(rect)
            elif comp_type == 'input':
                rect = Rectangle((x, y), width, height, 
                               facecolor='white', edgecolor='gray', linewidth=1)
                ax.add_patch(rect)
            elif comp_type == 'label':
                # 라벨은 텍스트만
                pass
            elif comp_type == 'table':
                rect = Rectangle((x, y), width, height, 
                               facecolor='lightgray', edgecolor='black', linewidth=1)
                ax.add_patch(rect)
            
            # 텍스트 추가
            if text:
                ax.text(x + width/2, y + height/2, text, 
                       ha='center', va='center', fontsize=10)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('UI Mockup', fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """matplotlib figure를 base64 문자열로 변환"""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64


class EnhancedBAQuestionGenerator:
    """향상된 BA 문제 생성기 - 시각적 요소 포함"""
    
    def __init__(self):
        self.visual_gen = VisualQuestionGenerator()
        
        # 템플릿 시나리오들
        self.erd_scenarios = [
            {
                'domain': '도서관 관리 시스템',
                'entities': [
                    {'name': '회원', 'attributes': ['회원ID', '이름', '이메일']},
                    {'name': '도서', 'attributes': ['도서ID', '제목', '저자']},
                    {'name': '대출', 'attributes': ['대출ID', '대출일', '반납일']},
                    {'name': '카테고리', 'attributes': ['카테고리ID', '분류명']}
                ]
            },
            {
                'domain': '병원 관리 시스템',
                'entities': [
                    {'name': '환자', 'attributes': ['환자ID', '이름', '주민번호']},
                    {'name': '의사', 'attributes': ['의사ID', '이름', '전문과목']},
                    {'name': '진료', 'attributes': ['진료ID', '진료일시', '증상']},
                    {'name': '처방전', 'attributes': ['처방전ID', '약품명', '용량']}
                ]
            }
        ]
        
        self.table_scenarios = [
            {
                'title': '직원 정보 테이블',
                'columns': ['직원ID', '이름', '부서코드', '부서명', '프로젝트코드', '프로젝트명'],
                'rows': [
                    ['E001', '김철수', 'D01', 'IT개발팀', 'P001,P002', '웹사이트개발,모바일앱'],
                    ['E002', '이영희', 'D02', '마케팅팀', 'P003', '광고캠페인'],
                    ['E003', '박민수', 'D01', 'IT개발팀', 'P001', '웹사이트개발']
                ],
                'violation_type': '1NF'
            }
        ]
        
        self.uml_scenarios = [
            {
                'domain': '결제 시스템',
                'classes': [
                    {
                        'name': 'PaymentProcessor',
                        'attributes': ['amount', 'currency'],
                        'methods': ['processPayment()', 'validatePayment()']
                    },
                    {
                        'name': 'CreditCardPayment',
                        'attributes': ['cardNumber', 'expiryDate'],
                        'methods': ['authorize()', 'charge()']
                    }
                ]
            }
        ]
    
    def generate_visual_question(self, template_type: str, difficulty: str) -> Dict[str, Any]:
        """시각적 요소가 포함된 문제 생성"""
        
        if template_type == 'erd_analysis':
            return self._generate_erd_question(difficulty)
        elif template_type == 'table_normalization':
            return self._generate_table_question(difficulty)
        elif template_type == 'uml_design':
            return self._generate_uml_question(difficulty)
        else:
            return self._generate_erd_question(difficulty)
    
    def _generate_erd_question(self, difficulty: str) -> Dict[str, Any]:
        """ERD 분석 문제 생성"""
        scenario = random.choice(self.erd_scenarios)
        
        # ERD 이미지 생성
        image_base64 = self.visual_gen.generate_erd_diagram(scenario['entities'])
        
        # 문제 생성
        question_data = {
            'question_id': f"ERD_{random.randint(1000, 9999)}",
            'title': f"{scenario['domain']} ERD 분석",
            'scenario': f"다음은 {scenario['domain']}의 ERD입니다.",
            'question_type': '선다형',
            'question': '이 ERD에서 엔티티 간의 관계를 올바르게 설명한 것은?',
            'choices': [
                '① 모든 엔티티가 1:1 관계로 연결됨',
                '② 중심 엔티티를 통한 간접 관계 구조',
                '③ 모든 엔티티가 독립적으로 존재',
                '④ 순환 참조 구조로 설계됨',
                '⑤ 계층적 상속 구조로 구성됨'
            ],
            'correct_answer': '②',
            'explanation': 'ERD에서 중심이 되는 엔티티(대출, 진료 등)를 통해 다른 엔티티들이 간접적으로 연결되는 구조입니다.',
            'difficulty': difficulty,
            'subject_area': "데이터 모델링 – 데이터 모델링 > 논리데이터 모델링",
            'visual_type': 'erd',
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '4' if difficulty == '중' else '3' if difficulty == '하' else '5'
        }
        
        return question_data
    
    def _generate_table_question(self, difficulty: str) -> Dict[str, Any]:
        """테이블 정규화 문제 생성"""
        scenario = random.choice(self.table_scenarios)
        
        # 테이블 이미지 생성
        image_base64 = self.visual_gen.generate_table_diagram(scenario)
        
        question_data = {
            'question_id': f"TABLE_{random.randint(1000, 9999)}",
            'title': f"{scenario['title']} 정규화",
            'scenario': f"다음은 정규화가 필요한 {scenario['title']}입니다.",
            'question_type': '서술형',
            'question': '이 테이블이 위반하는 정규형을 식별하고 정규화 방안을 제시하세요.',
            'model_answer': f"{scenario['violation_type']} 위반. 복수 값을 가진 컬럼을 별도 테이블로 분리하여 정규화 필요.",
            'grading_criteria': ['정규형 위반 정확히 식별', '정규화 방안 제시', '분리된 테이블 구조 설명'],
            'explanation': '정규화를 통해 데이터 중복을 제거하고 무결성을 확보할 수 있습니다.',
            'difficulty': difficulty,
            'subject_area': "데이터 모델링 – 데이터 모델링 > 물리데이터 모델링",
            'visual_type': 'table',
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '5' if difficulty == '상' else '4' if difficulty == '중' else '3'
        }
        
        return question_data
    
    def _generate_uml_question(self, difficulty: str) -> Dict[str, Any]:
        """UML 클래스 설계 문제 생성"""
        scenario = random.choice(self.uml_scenarios)
        
        # UML 이미지 생성
        image_base64 = self.visual_gen.generate_uml_diagram(scenario['classes'])
        
        question_data = {
            'question_id': f"UML_{random.randint(1000, 9999)}",
            'title': f"{scenario['domain']} UML 설계",
            'scenario': f"다음은 {scenario['domain']}의 UML 클래스 다이어그램입니다.",
            'question_type': '단답형',
            'question': '이 UML 다이어그램에서 사용된 디자인 패턴은?',
            'correct_answer': 'Strategy',
            'alternative_answers': ['Strategy Pattern', '전략 패턴'],
            'explanation': 'Strategy 패턴을 사용하여 결제 방식을 동적으로 변경할 수 있도록 설계되었습니다.',
            'difficulty': difficulty,
            'subject_area': "프로세스 모델링 – 설계 > MSA 서비스 설계",
            'visual_type': 'uml',
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '4' if difficulty == '중' else '3' if difficulty == '하' else '5'
        }
        
        return question_data