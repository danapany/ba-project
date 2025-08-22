# file_manager.py
"""
파일 관리 모듈
다운로드 파일 생성, ZIP 압축, Excel 생성 등
"""

import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO
import pandas as pd

from pdf_generator import PDFGenerator
from utils import generate_statistics

class FileManager:
    """파일 생성 및 관리 클래스"""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
    
    def create_json_file(self, questions: List[Dict[str, Any]]) -> str:
        """JSON 파일 내용 생성"""
        return json.dumps(questions, ensure_ascii=False, indent=2)
    
    def create_excel_file(self, questions: List[Dict[str, Any]]) -> bytes:
        """Excel 파일 생성"""
        excel_buffer = BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # 문제 유형별로 시트 분리
            for q_type in ["선다형", "단답형", "서술형"]:
                type_questions = [q for q in questions if q.get('question_type') == q_type]
                if type_questions:
                    # 시각적 이미지 데이터는 제외하고 저장 (크기 때문에)
                    processed_questions = []
                    for q in type_questions:
                        q_copy = q.copy()
                        if 'visual_image' in q_copy:
                            q_copy['visual_image'] = '[이미지 데이터 - PDF 참조]'
                        processed_questions.append(q_copy)
                    
                    df = pd.json_normalize(processed_questions)
                    df.to_excel(writer, sheet_name=q_type, index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()
    
    def create_statistics_file(self, questions: List[Dict[str, Any]]) -> str:
        """통계 파일 생성"""
        stats = generate_statistics(questions)
        return json.dumps(stats, ensure_ascii=False, indent=2)
    
    def create_download_zip(self, questions: List[Dict[str, Any]]) -> bytes:
        """다운로드용 파일들을 ZIP으로 압축"""
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # JSON 파일 추가
            json_content = self.create_json_file(questions)
            zip_file.writestr(f"BA_questions_{timestamp}.json", json_content.encode('utf-8'))
            
            # PDF 파일 추가
            pdf_data = self.pdf_generator.create_pdf_document_with_images(questions)
            if pdf_data:  # PDF 생성이 성공한 경우만
                zip_file.writestr(f"BA_questions_{timestamp}.pdf", pdf_data)
            
            # Excel 파일 추가
            excel_data = self.create_excel_file(questions)
            zip_file.writestr(f"BA_questions_{timestamp}.xlsx", excel_data)
            
            # 통계 파일 추가
            stats_content = self.create_statistics_file(questions)
            zip_file.writestr(f"BA_question_stats_{timestamp}.json", stats_content.encode('utf-8'))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def get_timestamp_filename(self, base_name: str, extension: str) -> str:
        """타임스탬프가 포함된 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"