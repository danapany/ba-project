# 📚 Business Application 모델링 문제 생성기

Azure OpenAI와 시각적 요소를 활용한 고품질 BA 문제 자동 생성 시스템

## ✨ 주요 기능

- 🤖 **Azure OpenAI 통합**: GPT-4를 활용한 고품질 문제 생성
- 🎨 **시각적 요소 지원**: ERD, UML, 플로우차트, UI 목업 등
- 📄 **PDF 학습자료 분석**: 업로드된 PDF 내용 기반 문제 생성
- 📊 **다양한 문제 유형**: 선다형, 단답형, 서술형 지원
- 💾 **다중 형식 출력**: PDF, JSON, Excel, ZIP 다운로드
- 📈 **실시간 통계**: 생성 현황 및 분포 시각화

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
프로젝트 루트에 `.env` 파일 생성:

```env
# Azure OpenAI 설정
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-azure-openai-api-key-here
CHAT_MODEL3=your-deployment-name

# API 버전 (선택사항)
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 기타 설정 (선택사항)
DEFAULT_QUESTION_COUNT=100
DEBUG=False
```

### 3. 애플리케이션 실행
```bash
streamlit run main_app.py
```

## 📁 프로젝트 구조

```
BA-Question-Generator/
├── main_app.py              # 메인 애플리케이션
├── config.py                # 설정 관리
├── utils.py                 # 유틸리티 함수
├── ui_components.py         # UI 컴포넌트
├── file_manager.py          # 파일 관리
├── pdf_generator.py         # PDF 생성
├── question_generator.py    # 문제 생성 엔진
├── visual_generator.py      # 시각적 요소 생성
├── requirements.txt         # 의존성
├── .env                     # 환경 설정 (생성 필요)
└── README.md               # 프로젝트 설명
```

## 🎯 사용법

### 1. 기본 설정
- 사이드바에서 문제 수, 유형별 비율, 난이도 비율 설정
- 시각적 문제 비율 조정 (0-100%)

### 2. PDF 업로드
- Business Application 모델링 관련 학습자료 PDF 업로드
- 자동으로 내용 추출 및 분석

### 3. 문제 생성
- "문제 생성 시작" 버튼 클릭
- 실시간 진행률 확인
- 생성 완료 후 통계 및 미리보기 제공

### 4. 결과 다운로드
- **ZIP 파일**: 모든 형식 포함 (PDF, JSON, Excel, 통계)
- **PDF 문제집**: 시각적 요소가 포함된 출력용 문서
- **JSON 데이터**: 데이터 처리용 원본 데이터

## 🎨 시각적 문제 유형

### ERD (Entity Relationship Diagram)
- 데이터베이스 설계 관련 문제
- 엔티티간 관계 분석
- 정규화 수준 평가

### UML 클래스 다이어그램
- 객체지향 설계 문제
- 클래스 관계 분석
- 설계 패턴 적용

### 플로우차트
- 업무 프로세스 분석
- 의사결정 포인트 식별
- 프로세스 개선 방안

### UI 목업
- 사용자 인터페이스 설계
- 사용성 개선 방안
- 접근성 고려사항

## 📊 생성 통계

생성된 문제들에 대한 상세 통계 제공:
- 문제 유형별 분포
- 난이도별 분포
- 시각적 요소 비율
- 과목별 분포

## 🛠 기술 스택

- **Frontend**: Streamlit
- **AI Engine**: Azure OpenAI (GPT-4)
- **시각화**: Matplotlib, Plotly
- **문서 생성**: ReportLab
- **데이터 처리**: Pandas, NumPy
- **이미지 처리**: Pillow

## 🔧 트러블슈팅

### Azure OpenAI 연결 오류
1. `.env` 파일의 설정값 확인
2. Azure Portal에서 API 키 및 엔드포인트 재확인
3. 배포된 모델명 정확성 검증

### 한글 폰트 문제
- Windows: 맑은 고딕 자동 감지
- macOS: Apple SD Gothic Neo 자동 감지
- Linux: 나눔 고딕 온라인 다운로드

### PDF 생성 실패
1. 임시 디렉토리 권한 확인
2. 시스템 메모리 부족 여부 확인
3. 이미지 크기 최적화 설정 조정

## 📝 라이선스

MIT License

## 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제나 제안사항이 있으시면 Issues 탭을 이용해주세요.