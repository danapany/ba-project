#!/bin/bash
# streamlit.sh - BA 문제 생성기 실행 스크립트

echo "📚 BA 문제 생성기 설치 및 실행"
echo "=================================="

# 필요한 라이브러리 설치
echo "📦 필수 라이브러리 설치 중..."
pip install streamlit
pip install openai
pip install pandas
pip install plotly
pip install python-dotenv
pip install reportlab
pip install matplotlib
pip install pillow
pip install PyPDF2
pip install openpyxl

echo ""
echo "✅ 라이브러리 설치 완료"
echo ""

# src 디렉토리로 이동하여 실행
echo "🚀 Streamlit 애플리케이션 시작..."
cd src
python -m streamlit run src/main_app.py --server.port 8000 --server.address 0.0.0.0