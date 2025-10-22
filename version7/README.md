# AI 기반 수소 뉴스 자동 요약 및 이메일 발송 프로젝트 (v7.0)

## 🎯 프로젝트 개요

본 프로젝트는 여러 수소 전문 뉴스 사이트에서 최신 기사를 자동으로 수집하고, Google Gemini AI를 이용해 핵심 내용을 요약한 뒤, 지정된 수신자들에게 매일 아침 HTML 형식의 뉴스 브리핑 이메일을 발송하는 파이썬 자동화 시스템입니다.

### 🆕 v7.0 주요 업데이트

- ✅ **모듈화된 아키텍처**: source_fetcher 모듈을 완전히 재구성하여 확장성과 유지보수성 향상
- ✅ **팩토리 패턴**: 새로운 뉴스 소스 추가 시 최소한의 코드 수정으로 가능
- ✅ **통합 NEWS_SOURCES**: 모든 뉴스 소스(RSS, 웹, 네이버, 구글)를 하나의 설정에서 관리
- ✅ **향상된 에러 처리**: 실패한 소스를 로그 파일에 자동 기록
- ✅ **Target 키워드 시스템**: 기술 및 회사 키워드 중심의 스마트 요약

## 📋 주요 기능

- **다중 소스 통합**: RSS 피드, 웹 크롤링, 네이버/구글 뉴스 검색 통합
- **AI 기반 자동 요약**: Google Gemini 2.0 Flash를 사용한 정확한 요약
- **Target 키워드 시스템**: 관심 기업 및 핵심 기술 키워드 자동 추출
- **모듈화된 설계**: 각 기능이 독립적인 모듈로 분리되어 확장 용이
- **맞춤형 HTML 이메일**: 관련도 순으로 정렬된 가독성 높은 브리핑
- **PDF 브리핑 통합**: 월간수소경제 PDF 파일 자동 분석 및 요약

## 🏗️ 시스템 아키텍처

```
version7/
├── source_fetcher/          # 뉴스 수집 모듈 (v7.0 신규 구조)
│   ├── __init__.py         # 모듈 초기화
│   ├── base_fetcher.py     # 추상 베이스 클래스
│   ├── rss_fetcher.py      # RSS 피드 전용
│   ├── web_scraper_fetcher.py  # 웹 크롤링 전용
│   ├── api_fetcher.py      # API 기반 Fetcher 부모 클래스
│   ├── naver_fetcher.py    # 네이버 뉴스 검색
│   ├── google_fetcher.py   # 구글 뉴스 검색
│   └── factory.py          # Fetcher 생성 팩토리
│
├── pdf/                    # PDF 파일 저장 디렉토리
├── logs/                   # 로그 파일 저장 디렉토리
│
├── config.py               # 설정 파일 (API 키, 키워드 등)
├── main.py                 # 메인 실행 스크립트
├── content_scraper.py      # 기사 본문 추출
├── summarizer.py           # AI 요약 및 키워드 추출
├── notifier.py             # 이메일 발송
├── pdf_reader.py           # PDF 파일 처리
├── requirements.txt        # 의존성 패키지
└── README.md               # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1️⃣ 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd version7

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/WSL
# venv\Scripts\activate   # Windows

# 라이브러리 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 2️⃣ 설정 파일 수정

`config.py` 파일을 열어 다음 정보를 입력하세요:

```python
# Google Gemini AI API 키
GOOGLE_API_KEY = "your-gemini-api-key"

# Gmail 발송 정보
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Gmail 앱 비밀번호

# 수신자 목록
RECEIVER_EMAIL = [
    "recipient1@example.com",
    "recipient2@example.com"
]
```

> **⚠️ 중요**: `config.py`에 민감한 정보가 포함되므로 `.gitignore`에 추가하세요!

### 3️⃣ 실행

```bash
python main.py
```

## 📊 워크플로우

1. **PDF 브리핑 처리** - pdf/ 디렉토리의 PDF 파일 분석
2. **기사 수집** - 모든 활성화된 소스에서 기사 수집
3. **본문 추출** - 각 기사 URL에서 본문 텍스트 추출
4. **AI 요약** - Gemini AI를 통한 핵심 내용 요약
5. **이메일 발송** - 관련도 순으로 정렬된 HTML 이메일 발송

## 🆕 새로운 뉴스 소스 추가 방법 (v7.0)

### ✅ 방법 1: RSS 피드 (가장 간단!)

`config.py`의 `NEWS_SOURCES`에 추가:

```python
NEWS_SOURCES = {
    # 기존 소스들...
    
    "Hydrogen Europe": {
        "url": "https://hydrogeneurope.eu/feed/",
        "type": "rss",
        "status": "active"
    }
}
```

### ✅ 방법 2: 웹 크롤링

CSS 선택자를 찾아서 추가:

```python
NEWS_SOURCES = {
    # 기존 소스들...
    
    "새로운 사이트": {
        "url": "https://example.com/news/",
        "type": "web",
        "article_selector": "article.post",
        "title_selector": "h2.title",
        "link_selector": "a",
        "status": "active"
    }
}
```

### ✅ 방법 3: 커스텀 Fetcher

특수한 처리가 필요한 경우 새 Fetcher 클래스 작성:

```python
# source_fetcher/custom_fetcher.py
from .base_fetcher import BaseSourceFetcher

class CustomFetcher(BaseSourceFetcher):
    def fetch_articles(self, max_articles=5):
        # 커스텀 로직 구현
        pass
```

## 📦 기술 스택

- **언어**: Python 3.9+
- **핵심 라이브러리**:
  - `google-generativeai` - Gemini AI API
  - `feedparser` - RSS 피드 파싱
  - `beautifulsoup4` - HTML 파싱
  - `requests` - HTTP 요청
  - `PyPDF2` - PDF 처리

## 🔧 주요 설정

### Target 키워드 시스템

```python
# 기술 키워드 (config.py)
TARGET_KEYWORDS_TECH = [
    "PEM 수전해", "AEM 수전해", "연료전지", 
    "촉매", "전해질막", "그린수소", ...
]

# 관심 기업 (config.py)
TARGET_COMPANIES = [
    "Electric Hydrogen", "Ohmium", "Hysata",
    "삼성중공업", "현대건설", "두산에너빌리티", ...
]
```

### 수집 제한

```python
MAX_ARTICLES_PER_SOURCE = 5   # 소스당 최대 5개
MAX_TOTAL_ARTICLES = 15       # 전체 최대 15개
MAX_NAVER_PER_KEYWORD = 3     # 네이버 키워드당 3개
MAX_GOOGLE_PER_KEYWORD = 3    # 구글 키워드당 3개
```

## 🔄 자동화 (Cron)

매일 오전 8시 자동 실행:

```bash
# crontab 편집
crontab -e

# 추가
0 8 * * * cd /path/to/version7 && /path/to/version7/venv/bin/python /path/to/version7/main.py
```

## 📝 로그 및 디버깅

- **실패한 소스**: `logs/failed_sources.txt`
- **개별 Fetcher 테스트**:
  ```bash
  python source_fetcher/rss_fetcher.py
  python source_fetcher/naver_fetcher.py
  ```

## 🎯 향후 개발 계획

- [ ] **Phase 2**: 노션 API 연동 (연도별 이슈 정리)
- [ ] **Phase 3**: 추가 해외 소스 확장
- [ ] **Phase 4**: 테스트 코드 작성 및 CI/CD 구축
- [ ] 웹 대시보드 개발
- [ ] 데이터베이스 연동 (중복 방지)

## 📄 라이선스

MIT License

---

## 💡 문제 해결 (Troubleshooting)

### Q: "ModuleNotFoundError: No module named 'source_fetcher'" 오류

**A**: 가상환경이 활성화되어 있는지 확인하고, `pip install -r requirements.txt` 재실행

### Q: 특정 소스에서 기사를 가져오지 못함

**A**: `logs/failed_sources.txt` 파일 확인 후 해당 소스의 status를 "testing"으로 변경하여 테스트

### Q: Gemini API 요금이 걱정됨

**A**: `MAX_TOTAL_ARTICLES`를 줄이거나, Gemini 2.0 Flash 모델 사용 (무료 한도 높음)

### Q: 네이버/구글 검색 결과가 없음

**A**: 검색 키워드를 조정하거나, 헤더 설정 확인

---

**제작자**: Hyscape 인턴십 프로젝트  
**버전**: 7.0 (모듈화 아키텍처)  
**최종 업데이트**: 2025-10-22