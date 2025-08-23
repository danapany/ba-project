# 📚 BA 문제 생성기

Business Application 모델링 문제를 자동으로 생성하는 AI 기반 도구입니다.

## 🌟 주요 기능

- **AI 기반 문제 생성**: Azure OpenAI를 활용한 고품질 문제 생성
- **시각적 요소 지원**: ERD, UML, 플로우차트 등 다이어그램 포함 문제
- **다양한 문제 유형**: 선다형, 단답형, 서술형 문제 지원
- **파일 출력**: PDF, JSON, Excel 형태로 결과 다운로드
- **통계 및 분석**: 생성된 문제의 통계 차트 및 분석

## 📁 프로젝트 구조

```
ba-project/
├── README.md
├── requirements.txt
├── .env.template
├── .env
├── streamlit.sh
└── src/
    ├── main_app.py                    # 메인 Streamlit 애플리케이션
    ├── config/
    │   ├── __init__.py
    │   └── config.py                  # 설정 관리
    ├── core/
    │   ├── __init__.py
    │   └── question_generator.py      # 핵심 문제 생성 로직
    ├── generators/
    │   ├── __init__.py
    │   └── visual_generator.py        # 시각적 요소 생성
    ├── ui/
    │   ├── __init__.py
    │   └── ui_components.py           # UI 컴포넌트
    ├── output/
    │   ├── __init__.py
    │   ├── file_manager.py            # 파일 관리
    │   └── pdf_generator.py           # PDF 생성
    ├── utils/
    │   ├── __init__.py
    │   └── utils.py                   # 유틸리티 함수
    └── temp/
        └── images/                    # 임시 이미지 저장소
```

## 🚀 설치 및 실행

### 1. 필수 요구사항

- Python 3.8 이상
- Azure OpenAI 계정 및 API 키

### 2. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd ba-project

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

1. `.env.template` 파일을 `.env`로 복사
2. Azure OpenAI 설정값 입력:

```bash
# Azure OpenAI 설정
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-azure-openai-api-key-here
CHAT_MODEL3=your-deployment-name

# API 버전 (선택사항)
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 기타 설정 (선택사항)
DEFAULT_QUESTION_COUNT=50

# 디버그 모드 (개발용)
DEBUG=False
```

### 4. 실행

```bash
# 스크립트를 통한 실행
./streamlit.sh

# 또는 직접 실행
cd src
streamlit run main_app.py
```

## 📊 사용 방법

### 1. 기본 설정
- 사이드바에서 문제 수, 유형별 비율, 난이도별 비율 설정
- 시각적 문제 비율 조정

### 2. PDF 업로드
- 학습자료 PDF 파일 업로드
- 내용 미리보기 확인

### 3. 문제 생성
- "문제 생성 시작" 버튼 클릭
- 진행률 확인 및 대기

### 4. 결과 확인
- 생성된 문제 통계 차트 확인
- 문제 미리보기
- 파일 다운로드 (ZIP, PDF, JSON)

## 🎨 시각적 문제 유형

- **ERD 분석**: 엔터티 관계 다이어그램 기반 문제
- **테이블 정규화**: 데이터베이스 정규화 문제
- **UML 설계**: 클래스 다이어그램 설계 문제
- **프로세스 플로우**: 업무 프로세스 플로우차트
- **UI 목업**: 화면 설계 및 사용자 인터페이스

## 🛠️ 개발 정보

### 주요 기술 스택
- **Frontend**: Streamlit
- **AI**: Azure OpenAI GPT
- **Visualization**: Matplotlib, Plotly
- **PDF Generation**: ReportLab
- **Data Processing**: Pandas

### 모듈 설명

#### `config/`
- 환경변수 및 설정 관리
- Azure OpenAI 연결 설정

#### `core/`
- 핵심 문제 생성 로직
- Azure OpenAI API 연동

#### `generators/`
- 시각적 요소 생성 (차트, 다이어그램)
- matplotlib 기반 이미지 생성

#### `ui/`
- Streamlit UI 컴포넌트
- 사용자 인터페이스 관리

#### `output/`
- 파일 생성 및 관리
- PDF, Excel, ZIP 파일 생성

#### `utils/`
- 공통 유틸리티 함수
- 폰트 설정, 텍스트 처리

## 🔧 설정 옵션

### 문제 생성 설정
- 총 문제 수: 10-200개
- 문제 유형 비율: 선다형, 단답형, 서술형
- 난이도 비율: 하, 중, 상
- 시각적 문제 비율: 0-100%

### 출력 옵션
- PDF: 시각적 요소 포함 출력용
- JSON: 데이터 처리용
- Excel: 문제 유형별 시트 분리
- ZIP: 전체 파일 패키지

## 🐛 트러블슈팅

### Azure OpenAI 연결 오류
- `.env` 파일의 설정값 확인
- API 키 및 엔드포인트 재확인
- 배포 모델명 확인

### PDF 생성 오류
- 한글 폰트 설치 확인
- 시스템별 폰트 경로 확인
- 메모리 부족 시 문제 수 조정

### 시각적 요소 표시 오류
- matplotlib 설치 확인
- PIL/Pillow 라이브러리 확인
- 임시 폴더 권한 확인

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제나 질문이 있으시면 이슈를 생성해 주세요.