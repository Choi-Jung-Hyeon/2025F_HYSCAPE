# 한국수소연합(H2HUB) 브리핑 자동화 시스템

## 📋 개요

한국수소연합의 일간 수소 이슈 브리핑 PDF를 자동으로 수집·분석하여 Notion에 업로드하는 시스템입니다.

**주요 기능:**
- H2HUB 웹사이트에서 브리핑 PDF 자동 수집
- Google Gemini를 사용한 AI 분석 (요약, 감성, 카테고리, 키워드)
- Notion 데이터베이스 자동 업로드

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config_template.py config.py
```

### 2. 설정

`config.py`에서 API 키를 설정하세요:

```python
GOOGLE_API_KEY = "your-google-api-key"
NOTION_API_KEY = "secret_your-notion-key"
NOTION_DATABASE_ID = "your-database-id"
```

### 3. Notion 데이터베이스 준비

다음 속성을 Notion 데이터베이스에 추가하세요:

| 속성 | 타입 |
|------|------|
| 제목 | Title |
| 날짜 | Date |
| 요약 | Rich Text |
| 링크 | URL |
| 기술전망 | Select (🟢 긍정적, 🔴 부정적, 🟡 중립) |
| category | Select (🏛️ 기관, 📜 정책, 🏙️ 지자체, 🏭 산업계, 🔬 연구계, 🌏 해외) |
| 키워드 | Multi-select |

---

## 💻 사용법

### 웹에서 브리핑 수집

```bash
# 1페이지 수집
python main.py --pages 1

# 3페이지까지 수집
python main.py --pages 3
```

### 기존 PDF 파일 분석

```bash
# 프로젝트 폴더의 PDF 분석
python main.py --existing-pdfs /mnt/project

# 다운로드 폴더의 PDF 분석
python main.py --existing-pdfs ./downloads
```

### 분석만 수행 (업로드 없이)

```bash
python main.py --existing-pdfs /mnt/project --no-upload
```

### Notion 연결 테스트

```bash
python main.py --test-notion
```

---

## 📊 시스템 구조

```
h2hub_automation/
├── config_template.py      # 설정 템플릿
├── article_collector.py    # PDF 수집 모듈
├── article_analyzer.py     # AI 분석 모듈
├── notion_uploader.py      # Notion 업로드 모듈
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성 패키지
├── downloads/              # PDF 다운로드 폴더
└── README.md
```

### 워크플로우

```
1. 수집 (Collector)
   ↓ H2HUB 웹사이트 크롤링 → PDF 다운로드

2. 분석 (Analyzer)
   ↓ PDF 텍스트 추출 → Gemini로 분석

3. 업로드 (Uploader)
   ↓ Notion API로 데이터베이스에 페이지 생성
```

---

## 🔧 트러블슈팅

### PDF 다운로드 실패

**해결:** 기존 PDF 모드 사용
```bash
python main.py --existing-pdfs /mnt/project
```

### Notion 업로드 실패

**해결:** 속성 이름 확인
- Notion 데이터베이스의 속성 이름이 `config.py`의 `NOTION_PROPERTIES`와 정확히 일치해야 합니다.
- Integration이 데이터베이스에 연결되어 있는지 확인하세요.

### Gemini API 오류

**해결:** API 키 및 할당량 확인
- API 키: https://aistudio.google.com/app/apikey
- Gemini API 무료 할당량: 분당 15회

---

## 📚 참고

- [Google Gemini API 문서](https://ai.google.dev/docs)
- [Notion API 문서](https://developers.notion.com/)
- [pdfplumber 문서](https://github.com/jsvine/pdfplumber)

---

## 📝 버전 정보

- **AI 모델**: Google Gemini 2.0 Flash Exp
- **Python**: 3.8+
- **주요 라이브러리**: pdfplumber, google-generativeai, notion-client