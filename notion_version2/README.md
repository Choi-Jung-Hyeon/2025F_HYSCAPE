# 한국수소연합(H2HUB) 브리핑 자동화 시스템 (Gemini 버전)

## 📋 프로젝트 개요

한국수소연합(H2HUB)의 **일간 수소 이슈 브리핑 PDF**를 자동으로 수집, 분석하여 Notion 데이터베이스에 업로드하는 자동화 시스템입니다.

### 주요 기능

- **자동 수집**: H2HUB 웹사이트에서 "브리핑" 키워드가 포함된 게시글의 PDF 자동 다운로드
- **AI 분석**: Google Gemini 2.0을 사용한 핵심 요약 및 감성 분석
- **Notion 연동**: 분석 결과를 Notion 데이터베이스에 자동 업로드

---

## 🏗️ 시스템 구조

```
h2hub_automation/
├── config.py                # 환경변수 및 설정 (✅ API 키 이미 설정됨)
├── article_collector.py     # PDF 브리핑 수집 모듈
├── article_analyzer.py      # PDF 분석 모듈 (Gemini 사용)
├── notion_uploader.py       # Notion 업로드 모듈
├── main.py                  # 메인 실행 스크립트
├── requirements.txt         # 의존성 패키지
├── downloads/               # PDF 다운로드 디렉토리
└── README.md
```

### 워크플로우

```
1. 수집 (Collector)
   ↓ H2HUB 게시판 크롤링 → PDF 다운로드
   
2. 분석 (Analyzer)
   ↓ pdfplumber로 텍스트 추출 → Gemini로 요약/감성 분석
   
3. 업로드 (Uploader)
   ↓ Notion API로 데이터베이스에 페이지 생성
```

---

## 🚀 설치 및 설정

### 1. 필수 요구사항

- Python 3.8 이상
- Google Gemini API 키 ✅ **(이미 설정됨)**
- Notion API 키 및 데이터베이스 ID ✅ **(이미 설정됨)**

### 2. 설치

```bash
# 프로젝트 디렉토리로 이동
cd h2hub_automation

# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 설정 확인

`config.py` 파일을 열어 다음 정보가 올바른지 확인하세요:

> **⚠️ 참고**: API 키가 이미 설정되어 있으므로 별도 입력 불필요!

### 4. Notion 데이터베이스 설정

기존 Notion 데이터베이스 (`2a17cf0a...`)에 다음 속성이 있는지 확인하세요:

| 속성 이름 | 타입 | 설명 |
|----------|------|------|
| 제목 | Title | 브리핑 제목 |
| 날짜 | Date | 발행일 |
| 요약 | Rich Text | AI 요약 내용 |
| 링크 | URL | 원문 URL |
| 기술전망 | Select | 감성 분석 결과 |

**기술전망 Select 옵션이 없다면 추가:**
- 🟢 긍정적
- 🔴 부정적
- 🟡 중립

---

## 💻 사용 방법

### 기본 실행 (웹 크롤링 + 분석 + 업로드)

```bash
python main.py
```

### 옵션

```bash
# 5페이지까지 수집
python main.py --pages 5

# Notion 업로드 없이 분석만 수행
python main.py --no-upload

# 기존 PDF 파일 처리 (웹 크롤링 없이)
python main.py --existing-pdfs ./downloads

# 프로젝트 폴더의 PDF 처리
python main.py --existing-pdfs /mnt/project

# Notion 연결 테스트
python main.py --test-notion
```

### 개별 모듈 테스트

```bash
# 수집기 테스트
python article_collector.py

# 분석기 테스트 (Gemini)
python article_analyzer.py

# 업로더 테스트
python notion_uploader.py
```

---

## 📊 실행 예시

```
======================================================================
한국수소연합 브리핑 자동화 시스템 시작
======================================================================
✅ 모든 컴포넌트 초기화 완료

======================================================================
STEP 1: 브리핑 PDF 수집
======================================================================

📄 1페이지 수집 중...
  ➜ 10개의 게시글 발견
✅ 브리핑 발견: 일간 수소 이슈 브리핑 (2024.11.25)
  ✅ 다운로드 완료: 20241125_일간_수소_이슈_브리핑.pdf (1250.5 KB)

✅ 1개의 브리핑 수집 완료

======================================================================
STEP 2: PDF 분석 및 STEP 3: Notion 업로드
======================================================================

[1/1] 일간 수소 이슈 브리핑 (2024.11.25)

📊 분석 시작: 20241125_일간_수소_이슈_브리핑.pdf
  ✅ 텍스트 추출 완료 (5234 자)
  ✅ 분석 완료
     감성: Positive
     요약: 정부가 수소 산업 지원 예산을 확대하고...

📤 Notion 업로드: 일간 수소 이슈 브리핑 (2024.11.25)
  ✅ 업로드 성공 (페이지 ID: 1a2b3c4d...)

======================================================================
작업 완료
======================================================================
✅ 성공: 1개
❌ 실패: 0개
📊 총 처리: 1개
======================================================================
```

---

## 🔧 트러블슈팅

### 1. PDF 다운로드 실패

**증상:** "PDF 링크를 찾을 수 없음" 오류

**해결 방법:**
- H2HUB 웹사이트의 HTML 구조가 변경되었을 수 있습니다
- `article_collector.py`의 `_find_pdf_link()` 메서드에서 CSS 선택자를 수정하세요
- 또는 기존 PDF 모드 사용: `python main.py --existing-pdfs /mnt/project`

### 2. Gemini API 오류

**증상:** "API key not valid" 또는 "Rate limit exceeded"

**해결 방법:**
- API 키가 올바른지 확인: https://aistudio.google.com/app/apikey
- Gemini API 무료 할당량 확인 (분당 15회 요청)
- 오류가 지속되면 요청 간 딜레이 추가

### 3. Notion 업로드 실패

**증상:** "date is not a property that exists" 오류

**해결 방법:**
- Notion 데이터베이스의 속성 이름이 정확히 일치하는지 확인
  - `제목` (Title)
  - `날짜` (Date)
  - `요약` (Text)
  - `링크` (URL)
  - `기술전망` (Select)
- Integration이 데이터베이스에 연결되어 있는지 확인
- 기술전망 Select에 3개 옵션 (🟢긍정적, 🔴부정적, 🟡중립) 추가 확인

### 4. 웹사이트 접근 차단

**증상:** "Connection refused" 또는 "403 Forbidden"

**해결 방법:**
- 요청 간 딜레이를 늘려보세요
- 기존 PDF 모드를 사용하세요: `python main.py --existing-pdfs ./downloads`

---

## 💡 추천 사용 방법

### 방법 1: 프로젝트 폴더의 PDF 즉시 분석

```bash
# 프로젝트에 이미 있는 PDF 파일들을 분석
python main.py --existing-pdfs /mnt/project
```

### 방법 2: 웹 크롤링으로 최신 브리핑 수집

```bash
# H2HUB에서 최신 브리핑 다운로드 + 분석 + 업로드
python main.py --pages 2
```

### 방법 3: 테스트 실행 (업로드 없이)

```bash
# 분석 결과만 확인하고 Notion에는 업로드 안 함
python main.py --existing-pdfs /mnt/project --no-upload
```

---

## 📚 참고 자료

- [pdfplumber 문서](https://github.com/jsvine/pdfplumber)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- [Notion API 문서](https://developers.notion.com/)
- [BeautifulSoup 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

## 📝 버전 정보

- **AI 모델**: Google Gemini 2.0 Flash Exp
- **PDF 처리**: pdfplumber 0.10+
- **Notion API**: notion-client 2.2+
- **Python**: 3.8+

---

## ✨ 특징

- ✅ **API 키 설정 완료**: 별도 입력 불필요
- ✅ **Gemini 사용**: 긴 컨텍스트 지원 (30,000자)
- ✅ **유연한 실행**: 웹 크롤링 or 기존 PDF 선택 가능
- ✅ **에러 핸들링**: 실패한 파일 건너뛰고 계속 진행
