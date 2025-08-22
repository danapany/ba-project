# visual_generator.py
"""
최적화된 시각적 요소 생성 모듈
ERD, UML, 테이블, 플로우차트, UI 목업 등을 고해상도로 생성
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
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
    """시각적 요소를 포함한 문제 생성기 - 고해상도 최적화 버전"""
    
    def __init__(self):
        self.dpi = 300  # 고해상도 설정
        self.figsize_multiplier = 1.3  # 기본 크기의 1.3배
    
    def _setup_figure(self, width: int = 12, height: int = 8):
        """고해상도 Figure 설정"""
        fig, ax = plt.subplots(
            1, 1, 
            figsize=(width * self.figsize_multiplier, height * self.figsize_multiplier)
        )
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        return fig, ax
    
    def _save_figure(self, fig) -> str:
        """Figure를 base64 문자열로 저장"""
        buffer = BytesIO()
        plt.savefig(
            buffer, 
            format='png', 
            bbox_inches='tight', 
            dpi=self.dpi,
            facecolor='white', 
            edgecolor='none'
        )
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64
    
    def generate_erd(self, entities: List[Dict], relationships: List[Dict]) -> str:
        """ERD 다이어그램 생성 - 고해상도"""
        fig, ax = self._setup_figure(16, 12)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # 엔티티 그리기
        entity_positions = {}
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink', 'lightcyan']
        
        for i, entity in enumerate(entities):
            x = (i % 3) * 3 + 1
            y = 6 - (i // 3) * 3
            entity_positions[entity['name']] = (x, y)
            
            # 엔티티 박스 그리기
            rect = FancyBboxPatch(
                (x-0.8, y-0.8), 1.6, 1.6,
                boxstyle="round,pad=0.1",
                facecolor=colors[i % len(colors)],
                edgecolor='black',
                linewidth=3
            )
            ax.add_patch(rect)
            
            # 엔티티 이름
            ax.text(x, y+0.3, entity['name'], ha='center', va='center', 
                   fontsize=16, fontweight='bold')
            
            # 속성 표시
            for j, attr in enumerate(entity.get('attributes', [])[:3]):
                ax.text(x, y-0.1-j*0.2, f"• {attr}", ha='center', va='center', 
                       fontsize=12)
        
        # 관계 그리기
        for rel in relationships:
            if rel['from'] in entity_positions and rel['to'] in entity_positions:
                from_pos = entity_positions[rel['from']]
                to_pos = entity_positions[rel['to']]
                
                # 관계선 그리기
                ax.annotate('', xy=to_pos, xytext=from_pos,
                           arrowprops=dict(arrowstyle='->', lw=4, color='red'))
                
                # 관계 이름
                mid_x = (from_pos[0] + to_pos[0]) / 2
                mid_y = (from_pos[1] + to_pos[1]) / 2
                ax.text(mid_x, mid_y+0.2, rel['type'], ha='center', va='center',
                       fontsize=14, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", 
                       facecolor='white', edgecolor='red', linewidth=3))
        
        plt.title('Entity Relationship Diagram', fontsize=20, fontweight='bold', pad=20)
        return self._save_figure(fig)
    
    def generate_table(self, data: Dict) -> str:
        """데이터 테이블 생성 - 고해상도"""
        df = pd.DataFrame(data['rows'], columns=data['columns'])
        
        fig, ax = self._setup_figure(14, 8)
        ax.axis('tight')
        ax.axis('off')
        
        # 테이블 생성
        table = ax.table(cellText=df.values, colLabels=df.columns,
                        cellLoc='center', loc='center')
        
        # 테이블 스타일링
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.5, 2.0)
        
        # 헤더 스타일
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 데이터 행 스타일 (교대로 색상 적용)
        for i in range(1, len(df) + 1):
            for j in range(len(df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f1f1f2')
                else:
                    table[(i, j)].set_facecolor('white')
        
        plt.title(data.get('title', '데이터 테이블'), fontsize=18, fontweight='bold', pad=20)
        return self._save_figure(fig)
    
    def generate_uml_class(self, classes: List[Dict]) -> str:
        """UML 클래스 다이어그램 생성 - 고해상도"""
        fig, ax = self._setup_figure(16, 12)
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        class_positions = {}
        
        for i, cls in enumerate(classes):
            x = (i % 3) * 4 + 2
            y = 6 - (i // 3) * 3
            class_positions[cls['name']] = (x, y)
            
            # 클래스 박스 높이 계산
            total_items = 1 + len(cls.get('attributes', [])) + len(cls.get('methods', []))
            box_height = max(1.5, total_items * 0.3)
            
            # 클래스 박스
            rect = Rectangle((x-1.5, y-box_height/2), 3, box_height,
                           facecolor='lightblue', edgecolor='black', linewidth=3)
            ax.add_patch(rect)
            
            # 클래스 이름
            current_y = y + box_height/2 - 0.3
            ax.text(x, current_y, cls['name'], ha='center', va='center',
                   fontsize=16, fontweight='bold')
            
            # 구분선
            current_y -= 0.4
            ax.plot([x-1.4, x+1.4], [current_y, current_y], 'k-', linewidth=2)
            
            # 속성들
            current_y -= 0.2
            for attr in cls.get('attributes', []):
                ax.text(x-1.3, current_y, f"- {attr}", ha='left', va='center', fontsize=11)
                current_y -= 0.3
            
            # 구분선
            if cls.get('methods'):
                ax.plot([x-1.4, x+1.4], [current_y+0.1, current_y+0.1], 'k-', linewidth=2)
                current_y -= 0.1
            
            # 메소드들
            for method in cls.get('methods', []):
                ax.text(x-1.3, current_y, f"+ {method}", ha='left', va='center', fontsize=11)
                current_y -= 0.3
        
        plt.title('UML Class Diagram', fontsize=20, fontweight='bold', pad=20)
        return self._save_figure(fig)
    
    def generate_flowchart(self, steps: List[Dict]) -> str:
        """플로우차트 생성 - 고해상도"""
        fig, ax = self._setup_figure(14, 16)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(steps) + 2)
        ax.axis('off')
        
        for i, step in enumerate(steps):
            y = len(steps) + 1 - i
            x = 5
            
            # 단계 타입에 따른 도형 선택
            if step['type'] == 'start' or step['type'] == 'end':
                # 타원
                ellipse = patches.Ellipse((x, y), 2.5, 0.8, facecolor='lightgreen',
                                        edgecolor='black', linewidth=3)
                ax.add_patch(ellipse)
            elif step['type'] == 'decision':
                # 다이아몬드
                diamond = patches.Polygon([(x, y+0.5), (x+1.2, y), (x, y-0.5), (x-1.2, y)],
                                        closed=True, facecolor='yellow', 
                                        edgecolor='black', linewidth=3)
                ax.add_patch(diamond)
            else:
                # 직사각형
                rect = Rectangle((x-1.2, y-0.4), 2.4, 0.8, facecolor='lightblue',
                               edgecolor='black', linewidth=3)
                ax.add_patch(rect)
            
            # 텍스트
            ax.text(x, y, step['text'], ha='center', va='center', fontsize=12, fontweight='bold')
            
            # 화살표 (마지막이 아닌 경우)
            if i < len(steps) - 1:
                ax.annotate('', xy=(x, y-0.6), xytext=(x, y-0.4),
                           arrowprops=dict(arrowstyle='->', lw=3, color='black'))
        
        plt.title('Process Flowchart', fontsize=20, fontweight='bold', pad=20)
        return self._save_figure(fig)
    
    def generate_ui_mockup(self, components: List[Dict]) -> str:
        """UI 목업 생성 - 고해상도"""
        fig, ax = self._setup_figure(14, 10)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # 브라우저 프레임
        browser_frame = Rectangle((1, 1), 8, 6, facecolor='white', 
                                edgecolor='gray', linewidth=3)
        ax.add_patch(browser_frame)
        
        # 브라우저 상단바
        top_bar = Rectangle((1, 6.5), 8, 0.5, facecolor='lightgray', 
                          edgecolor='gray', linewidth=2)
        ax.add_patch(top_bar)
        
        # URL 바
        url_bar = Rectangle((2, 6.6), 6, 0.3, facecolor='white', 
                          edgecolor='black', linewidth=2)
        ax.add_patch(url_bar)
        ax.text(2.2, 6.75, 'https://example.com', ha='left', va='center', fontsize=10)
        
        # UI 컴포넌트들
        for comp in components:
            x, y, w, h = comp['x'], comp['y'], comp['width'], comp['height']
            
            if comp['type'] == 'button':
                button = Rectangle((x, y), w, h, facecolor='lightblue', 
                                 edgecolor='blue', linewidth=2)
                ax.add_patch(button)
                ax.text(x + w/2, y + h/2, comp['text'], ha='center', va='center', 
                       fontsize=11, fontweight='bold')
            
            elif comp['type'] == 'input':
                input_box = Rectangle((x, y), w, h, facecolor='white', 
                                    edgecolor='gray', linewidth=2)
                ax.add_patch(input_box)
                ax.text(x + 0.1, y + h/2, comp.get('placeholder', ''), 
                       ha='left', va='center', fontsize=10, color='gray')
            
            elif comp['type'] == 'label':
                ax.text(x, y + h/2, comp['text'], ha='left', va='center', 
                       fontsize=12, fontweight='bold')
        
        plt.title('UI Mockup', fontsize=20, fontweight='bold', pad=20)
        return self._save_figure(fig)


class EnhancedBAQuestionGenerator:
    """시각적 요소를 포함한 BA 문제 생성기"""
    
    def __init__(self):
        self.visual_gen = VisualQuestionGenerator()
        
        # 시각적 문제 템플릿들
        self.visual_templates = {
            'erd_analysis': {
                'title': 'ERD 분석 문제',
                'scenario': '다음은 온라인 쇼핑몰 시스템의 ERD입니다.',
                'visual_data': {
                    'entities': [
                        {'name': '고객', 'attributes': ['고객ID', '이름', '이메일', '전화번호']},
                        {'name': '주문', 'attributes': ['주문ID', '주문일자', '총금액']},
                        {'name': '상품', 'attributes': ['상품ID', '상품명', '가격', '재고수량']},
                        {'name': '주문상세', 'attributes': ['수량', '단가']}
                    ],
                    'relationships': [
                        {'from': '고객', 'to': '주문', 'type': '1:N'},
                        {'from': '주문', 'to': '주문상세', 'type': '1:N'},
                        {'from': '상품', 'to': '주문상세', 'type': '1:N'}
                    ]
                },
                'questions': [
                    {
                        'type': '선다형',
                        'question': '이 ERD에서 잘못된 관계는?',
                        'choices': [
                            '① 고객과 주문의 1:N 관계',
                            '② 주문과 주문상세의 1:N 관계', 
                            '③ 상품과 주문상세의 1:N 관계',
                            '④ 고객과 상품의 직접 관계 부재',
                            '⑤ 모두 올바른 관계'
                        ],
                        'correct_answer': '⑤',
                        'explanation': '모든 관계가 올바르게 설정되어 있습니다. 고객-주문(1:N), 주문-주문상세(1:N), 상품-주문상세(1:N) 관계는 전형적인 쇼핑몰 시스템의 구조입니다.'
                    }
                ]
            },
            
            'table_normalization': {
                'title': '정규화 분석 문제',
                'scenario': '다음 테이블의 정규화 수준을 분석하세요.',
                'visual_data': {
                    'title': '학생 수강 정보',
                    'columns': ['학번', '학생명', '과목코드', '과목명', '교수명', '학점', '성적'],
                    'rows': [
                        ['2021001', '김철수', 'CS101', '프로그래밍', '이교수', '3', 'A'],
                        ['2021001', '김철수', 'CS102', '자료구조', '박교수', '3', 'B+'],
                        ['2021002', '이영희', 'CS101', '프로그래밍', '이교수', '3', 'A+'],
                        ['2021002', '이영희', 'CS103', '데이터베이스', '최교수', '3', 'A']
                    ]
                },
                'questions': [
                    {
                        'type': '서술형',
                        'question': '이 테이블이 위반하는 정규형과 그 이유를 설명하고, 정규화 방안을 제시하세요.',
                        'model_answer': '제2정규형을 위반합니다. 학생명이 학번에만 종속되어 부분적 함수 종속이 발생합니다. 또한 과목명, 교수명, 학점이 과목코드에만 종속되어 역시 부분적 함수 종속입니다. 정규화 방안: 학생 테이블(학번, 학생명), 과목 테이블(과목코드, 과목명, 교수명, 학점), 수강 테이블(학번, 과목코드, 성적)로 분리해야 합니다.',
                        'grading_criteria': ['정규형 위반 정확히 식별', '부분적 함수 종속 설명', '올바른 정규화 방안 제시'],
                        'explanation': '이 문제는 정규화 이론의 핵심인 함수 종속성을 이해하고 있는지 평가합니다.'
                    }
                ]
            },
            
            'uml_design': {
                'title': 'UML 클래스 설계 문제',
                'scenario': '도서관 시스템의 클래스 다이어그램입니다.',
                'visual_data': [
                    {
                        'name': 'Book',
                        'attributes': ['isbn', 'title', 'author', 'publishDate'],
                        'methods': ['getInfo()', 'isAvailable()']
                    },
                    {
                        'name': 'Member', 
                        'attributes': ['memberId', 'name', 'email'],
                        'methods': ['borrowBook()', 'returnBook()']
                    },
                    {
                        'name': 'Loan',
                        'attributes': ['loanDate', 'returnDate', 'status'],
                        'methods': ['extend()', 'complete()']
                    }
                ],
                'questions': [
                    {
                        'type': '단답형',
                        'question': 'Book과 Member 클래스 사이의 관계를 나타내는 클래스는?',
                        'correct_answer': 'Loan',
                        'alternative_answers': ['대출', 'Borrow'],
                        'explanation': 'Book과 Member 사이의 다대다 관계를 해결하기 위한 연관 클래스가 Loan입니다.'
                    }
                ]
            }
        }
    
    def generate_visual_question(self, template_key: str, difficulty: str = '중') -> Dict[str, Any]:
        """시각적 요소를 포함한 문제 생성"""
        template = self.visual_templates.get(template_key)
        if not template:
            return {}
        
        # 시각적 요소 생성
        visual_type = template_key.split('_')[0]  # erd, table, uml 등
        
        if visual_type == 'erd':
            image_base64 = self.visual_gen.generate_erd(
                template['visual_data']['entities'],
                template['visual_data']['relationships']
            )
        elif visual_type == 'table':
            image_base64 = self.visual_gen.generate_table(template['visual_data'])
        elif visual_type == 'uml':
            image_base64 = self.visual_gen.generate_uml_class(template['visual_data'])
        else:
            image_base64 = ""
        
        # 문제 데이터 구성
        question_data = template['questions'][0].copy()
        question_data.update({
            'question_id': f"VISUAL_{random.randint(1000, 9999)}",
            'title': template['title'],
            'scenario': template['scenario'],
            'difficulty': difficulty,
            'subject_area': f"데이터 모델링 – {visual_type.upper()} 분석",
            'visual_type': visual_type,
            'visual_image': image_base64,
            'generated_at': datetime.now().isoformat(),
            'points': '5'  # 시각적 문제는 높은 배점
        })
        
        return question_data