# AI 기반 수소 뉴스 자동 요약 및 이메일 발송 프로젝트 (v2.0)

## 1\. 프로젝트 개요

본 프로젝트는 여러 수소 전문 뉴스 사이트에서 최신 기사를 자동으로 수집하고, Google Gemini AI를 이용해 핵심 내용을 요약한 뒤, 지정된 수신자들에게 매일 아침 HTML 형식의 뉴스 브리핑 이메일을 발송하는 파이썬 자동화 시스템입니다.

## 2\. 주요 기능

  - **다중 소스 통합**: 여러 뉴스 매체의 RSS 피드를 동시에 수집하고 통합하여 정보를 제공합니다.
  - **AI 기반 자동 요약**: Google의 강력한 `gemini-1.0-pro` 모델을 사용하여 각 기사의 핵심 내용을 정확하게 요약하고 관련 키워드를 추출합니다.
  - **안정적인 콘텐츠 추출**: `newspaper3k` 라이브러리를 통해 기사 페이지의 광고나 불필요한 요소를 제외한 본문 텍스트만을 안정적으로 추출합니다.
  - **맞춤형 HTML 이메일 발송**: 요약된 기사들을 가독성 좋은 HTML 형식으로 디자인하여 다수의 수신자에게 이메일로 발송합니다.
  - **모듈화된 설계**: 기능별(`설정`, `수집`, `추출`, `요약`, `발송`)로 코드가 분리되어 있어 유지보수와 기능 확장이 용이합니다.

## 3\. 시스템 아키텍처

프로젝트는 다음과 같은 순서로 작업을 자동 처리합니다.

1.  **설정 로드 (`config.py`)**: API 키, 이메일 계정 정보, 수집할 뉴스 소스 목록 등 모든 설정을 불러옵니다.
2.  **기사 수집 (`source_fetcher.py`)**: `config.py`에 정의된 모든 RSS 피드를 순회하며 최신 기사 목록(제목, URL, 출처 등)을 통합 수집합니다.
3.  **본문 추출 (`content_scraper.py`)**: 수집된 기사 목록의 URL에 하나씩 접속하여 기사 본문 텍스트를 추출하고 정제합니다.
4.  **AI 요약 및 키워드 추출 (`summarizer.py`)**: 추출된 본문을 Gemini AI API에 전송하여 3\~4줄의 핵심 요약과 키워드를 생성합니다.
5.  **이메일 발송 (`notifier.py`)**: 모든 요약 결과를 취합하여 하나의 HTML 이메일 본문을 생성하고, `main.py`의 제어에 따라 수신자들에게 발송합니다.

## 4\. 기술 스택

  - **언어**: Python 3.9+
  - **핵심 라이브러리**:
      - `google-generativeai`: Google Gemini AI API 연동
      - `feedparser`: RSS 피드 파싱
      - `newspaper3k`: 뉴스 기사 본문 크롤링 및 텍스트 추출
  - **개발 환경**: VS Code, WSL (Ubuntu), Python Virtual Environment (venv)

## 5\. 프로젝트 설정 (Installation & Setup)

#### 1\. 소스 코드 복제

```bash
git clone https://github.com/your-username/your-project-repo.git
cd your-project-repo
```

#### 2\. Python 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (Linux/macOS/WSL)
source venv/bin/activate

# 가상환경 활성화 (Windows)
# venv\Scripts\activate
```

#### 3\. 필요 라이브러리 설치

프로젝트 루트 디렉터리에 아래 내용으로 `requirements.txt` 파일을 생성하세요.

**`requirements.txt`**

```
google-generativeai
feedparser
newspaper3k
```

그 다음, 아래 명령어로 한 번에 설치합니다.

```bash
pip install -r requirements.txt
```

> **참고**: `newspaper3k` 라이브러리는 `lxml` 등 자연어 처리를 위한 내부 패키지를 다운로드해야 할 수 있습니다. `pip` 설치 후 첫 실행 시 자동으로 다운로드되거나, 오류 발생 시 다음 명령어를 실행해주세요: `python -m nltk.downloader all`

#### 4\. 환경 설정 (`config.py`)

`config.py` 파일을 열어 본인의 환경에 맞게 **필수 정보**들을 입력하세요.

**`config.py`**

```python
# Google Gemini AI 설정
# https://aistudio.google.com/app/apikey 에서 API 키를 발급받으세요.
GOOGLE_API_KEY = "여기에_본인의_GEMINI_API_키를_입력하세요"

# Gmail 발송 정보 설정
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "발송할_본인의_GMAIL_주소@gmail.com"
# 참고: Gmail 2단계 인증 사용 시 '앱 비밀번호'를 생성하여 사용해야 합니다.
SENDER_PASSWORD = "GMAIL_앱_비밀번호_또는_계정_비밀번호" 
RECEIVER_EMAILS = ["수신자1@example.com", "수신자2@example.com"]

# 스크랩할 정보 소스 (얼마든지 추가/삭제 가능)
NEWS_SOURCES = {
    "월간수소경제": "http://www.h2news.kr/rss/S1N1.xml",
    "Hydrogen Insight": "https://www.hydrogeninsight.com/rss",
    "H2 View": "https://www.h2-view.com/feed/",
    "Renewables Now": "https://renewablesnow.com/rss/"
}
```

> **⚠️ 중요**: `config.py` 파일에 API 키나 비밀번호와 같은 민감한 정보를 포함하고 있으므로, 이 파일을 **절대 Git에 커밋하지 마세요**. `.gitignore` 파일에 `config.py`를 추가하여 관리하는 것을 강력히 권장합니다.

## 6\. 실행 방법

모든 설정이 완료된 후, 터미널에서 아래 명령어를 실행하면 전체 워크플로우가 시작됩니다.

```bash
python main.py
```

스크립트가 실행되면 터미널에 각 단계별 진행 상황이 출력되고, 모든 작업이 완료되면 지정된 수신자에게 요약 뉴스 이메일이 발송됩니다.

#### 자동 실행 (Scheduling)

매일 특정 시간에 이 스크립트를 자동으로 실행하려면 Linux/WSL의 `cron`이나 Windows의 `작업 스케줄러`를 사용하세요.

**`cron` 등록 예시 (매일 오전 8시에 실행):**

```bash
# crontab 편집기 열기
crontab -e

# 아래 라인 추가 (경로는 실제 프로젝트 위치에 맞게 수정)
0 8 * * * /home/user/your-project-repo/venv/bin/python /home/user/your-project-repo/main.py
```

## 7\. 프로젝트 구조

```
.
├── venv/                   # Python 가상환경 폴더
├── main.py                 # 프로젝트 실행 메인 스크립트
├── config.py               # API 키, 이메일 정보 등 설정 파일
├── source_fetcher.py       # RSS 피드에서 기사 목록을 가져오는 모듈
├── content_scraper.py      # 기사 URL에서 본문 텍스트를 추출하는 모듈
├── summarizer.py           # Gemini AI를 이용해 텍스트를 요약하는 모듈
├── notifier.py             # 요약 결과를 HTML 이메일로 발송하는 모듈
├── requirements.txt        # 프로젝트 의존성 라이브러리 목록
└── README.md               # 프로젝트 설명서 (현재 파일)
```

## 8\. 향후 개선 과제

  - [ ] **데이터베이스 연동**: 이미 발송한 기사는 중복 발송하지 않도록 기사 URL을 데이터베이스(SQLite 등)에 기록 및 조회
  - [ ] **오류 처리 강화**: 특정 뉴스 소스 접속 실패 또는 AI 요약 실패 시 해당 기사만 건너뛰고 전체 프로세스는 중단되지 않도록 예외 처리 고도화
  - [ ] **비동기 처리**: `asyncio`, `httpx` 등을 사용하여 여러 기사의 본문 추출 및 AI 요약을 병렬로 처리하여 실행 시간 단축
  - [ ] **동적 스크래핑**: RSS를 제공하지 않는 사이트를 위해 Selenium 또는 Playwright를 이용한 동적 웹 스크래핑 기능 추가

## 9\. 라이선스

이 프로젝트는 [MIT License](https://www.google.com/search?q=LICENSE)에 따라 라이선스가 부여됩니다.