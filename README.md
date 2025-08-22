# 📚 BA 문제 생성기 (Business Application Question Generator)

Azure OpenAI와 시각적 요소를 활용한 Business Application 모델링 문제 자동 생성 도구

## ✨ 주요 기능

### 🎨 시각적 문제 생성
- **ERD (Entity Relationship Diagram)**: 데이터베이스 설계 분석 문제
- **UML 클래스 다이어그램**: 객체지향 설계 문제
- **데이터 테이블**: 정규화 분석 문제
- **플로우차트**: 업무 프로세스 설계 문제
- **UI 목업**: 화면 설계 및 사용성 분석 문제

### 🤖 AI 기반 텍스트 문제 생성
- **Azure OpenAI** 연동으로 고품질 문제 자동 생성
- **선다형/단답형/서술형** 문제 지원
- **실무 중심 시나리오** 기반 문제 출제
- **난이도별 문제 생성** (하/중/상)

### 📊 종합 관리 기능
- **PDF 문제집** 생성 (한글 폰트 지원)
- **Excel/JSON** 형태 데이터 출력
- **실시간 통계** 및 차트 분석
- **문제 미리보기** 및 편집

## 🚀 설치 및 실행

### 1. 필수 요구사항
- Python 3.8 이상
- Azure OpenAI 계정 및 API 키

### 2. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 설정
프로젝트 루트에 `.env` 파일 생성:
```env
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-azure-openai-api-key-here
CHAT_MODEL3=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
DEFAULT_QUESTION_COUNT=100
DEBUG=False
```

### 4. 애플리케이션 실행
```bash
streamlit run main_app.py
```

## 📁 프로젝트 구조

```
BA_Question_Generator/
├── .env                    # Azure OpenAI 설정 파일
├── visual_generator.py     # 시각적 요소 생성 모듈
├── question_generator.py   # 핵심 문제 생성 모듈
├── main_app.py            # 메인 Streamlit 애플리케이션
├── requirements.txt       # 필요 라이브러리 목록
└── README.md             # 프로젝트 문서
```

## 🎯 사용 방법

### 1. PDF 업로드
- BA 모델링 관련 학습자료 PDF를 업로드
- 자동으로 텍스트 추출 및 내용 분석

### 2. 문제 설정
- **총 문제 수**: 10~200개
- **문제 유형 비율**: 선다형/단답형/서술형 비율 조정
- **난이도 비율**: 하/중/상 난이도 비율 설정
- **시각적 비율**: 시각적 요소 포함 문제 비율 (0~100%)

### 3. 문제 생성
- Azure OpenAI가 학습자료를 분석하여 문제 자동 생성
- 과목 영역에 따라 적절한 시각적 요소 자동 선택
- 실시간 진행률 표시 및 중간 결과 확인

### 4. 결과 확인 및 다운로드
- **웹 미리보기**: 생성된 문제를 웹에서 바로 확인
- **PDF 다운로드**: 한글 폰트가 적용된 출력용 문제집
- **데이터 다운로드**: JSON, Excel 형태로 데이터 추출
- **통계 분석**: 문제 분포 및 시각적 요소 통계

## 🎨 시각적 문제 예시

### ERD 분석 문제
```
온라인 쇼핑몰 시스템의 ERD를 보고 다음 질문에 답하세요.
[ERD 다이어그램 표시]
Q: 이 ERD에서 잘못된 관계는?
① 고객과 주문의 1:N 관계
② 주문과 주문상세의 1:N 관계
③ 상품과 주문상세의 1:N 관계
④ 고객과 상품의 직접 관계 부재
⑤ 모두 올바른 관계
```

### 플로우차트 분석 문제
```
주문 처리 프로세스 플로우차트를 보고 답하세요.
[플로우차트 다이어그램 표시]
Q: 이 프로세스에서 첫 번째 의사결정 단계는?
A: 재고 충분?
```

## ⚙️ 주요 설정

### 시각적 문제 비율 조정
- **0%**: 텍스트 문제만 생성
- **30%** (권장): 균형잡힌 시각적/텍스트 문제 조합
- **100%**: 시각적 문제만 생성

### 과목별 시각적 요소 매핑
- **데이터 모델링** → ERD, 테이블 정규화
- **프로세스 모델링** → UML 클래스, 플로우차트
- **화면 설계** → UI 목업
- **시스템 설계** → 아키텍처 다이어그램

## 📋 요구사항 파일 (requirements.txt)

```txt
streamlit
openai
pandas
plotly
python-dotenv
reportlab
matplotlib
pillow
PyPDF2
openpyxl
```

## 🔧 문제 해결

### Azure OpenAI 연결 오류
```bash
# .env 파일 설정 확인
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-32-character-api-key
CHAT_MODEL3=gpt-4  # 또는 배포한 모델명
```

### 한글 폰트 문제
- Windows: 맑은 고딕 자동 탐지
- macOS: Apple SD Gothic Neo 자동 탐지
- Linux: 나눔고딕 온라인 다운로드

### 메모리 부족 오류
```bash
# 문제 수를 줄여서 실행
# 권장: 100개 이하로 설정
```

## 📈 성능 최적화

### 권장 설정
- **총 문제 수**: 50~100개
- **시각적 비율**: 20~40%
- **API 요청 간격**: 자동 조절

### 비용 최적화
- **모델 선택**: GPT-3.5-turbo 사용 권장
- **토큰 제한**: 문제당 최대 2000 토큰
- **배치 생성**: 10개씩 생성하여 중간 확인

## 🔄 업데이트 로그

### v1.0.0 (현재)
- ✅ Azure OpenAI 연동
- ✅ 시각적 문제 생성 (ERD, UML, 테이블, 플로우차트, UI)
- ✅ 한글 PDF 생성
- ✅ 다양한 출력 형식 지원
- ✅ 실시간 통계 및 미리보기

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 라이선스

이 프로젝트는 MIT 라이선스하에 있습니다.

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 Issues를 통해 문의해주세요.

---

🎉 **BA 모델링 시험 준비가 이제 더 쉬워집니다!**