# 🚀 수소 뉴스 자동 브리핑 시스템 v3.0

**Target 키워드 중심 + 구글 뉴스 추가 + PDF 키워드 요약**

---

## 📋 목차

1. [프로젝트 개요](#-프로젝트-개요)
2. [v3.0 주요 변경사항](#-v30-주요-변경사항)
3. [시스템 아키텍처](#-시스템-아키텍처)
4. [설치 및 설정](#-설치-및-설정)
5. [사용 방법](#-사용-방법)
6. [트러블슈팅](#-트러블슈팅)
7. [향후 계획](#-향후-계획)

---

## 🎯 프로젝트 개요

수소 산업 관련 뉴스를 자동으로 수집하고, AI(Gemini)로 요약하여 이메일로 발송하는 시스템입니다.

### 핵심 기능
- ✅ 다중 뉴스 소스 자동 수집 (웹 + RSS + 네이버 + 구글)
- ✅ **Target 키워드 중심 필터링** (기술 + 회사)
- ✅ **회사 키워드 강조** (관심 기업 ⭐)
- ✅ **PDF 브리핑 키워드 중심 요약**
- ✅ Gemini 2.0 Flash AI 요약
- ✅ 이메일 자동 발송
- ✅ 실패 소스 로깅

---

## 🆕 v3.0 주요 변경사항

### 1. **Target 키워드 추가** ⭐
```python
# 기술 키워드
PEM 수전해, AEM 수전해, PEM 연료전지, 연료전지,
촉매 사용량, 로딩량, 전해질막, 내구성, durability,
수전해 시스템, 태양광, 풍력, 지열, 수력, 재생에너지

# 회사 키워드 (2024년 투자받은 수소 스타트업)
Electric Hydrogen, EnerVenue, Koloma, Ohmium, ZeroAvia,
Energy Tree Solutions, HYSETCO, Hysata, LONGi, Verdagy,
+ 23개 더...
```

### 2. **구글 뉴스 추가** 🌍
```python
GOOGLE_KEYWORDS = [
    "green hydrogen",
    "hydrogen fuel cell",
    "PEM electrolyzer",
    "hydrogen economy",
    "hydrogen startup",
    "AEM electrolyzer"
]
```

### 3. **PDF 키워드 중심 요약**
- 전체 PDF가 아닌 **Target 키워드 포함 문단만 추출**
- 관련 없는 내용 제외하고 핵심만 요약

### 4. **회사 키워드 강조**
- 관심 기업이 언급되면 **빨간색 강조 ⭐**
- 관련도 점수 자동 계산

### 5. **실패 소스 로깅**
- `logs/failed_sources.txt`에 실패한 소스 자동 기록

---

## 🏗️ 시스템 아키텍처

```
project/
├── pdf/                          # PDF 파일 저장
│   └── 250925_일간수소브리핑.pdf
│
├── logs/                         # 로그 파일
│   └── failed_sources.txt
│
├── config.py                     # 설정 파일
├── source_fetcher.py            # 뉴스 수집 (구글 뉴스 추가!)
├── content_scraper.py           # 본문 추출
├── summarizer.py                # AI 요약 (회사 키워드 강조!)
├── notifier.py                  # 이메일 발송
├── pdf_reader.py                # PDF 키워드 중심 요약
├── main.py                      # 메인 실행
│
├── requirements.txt             # 의존성
└── README.md                    # 이 파일
```

### 데이터 흐름

```
1. 뉴스 수집
   ├── 월간수소경제 (웹 크롤링)
   ├── Hydrogen Central (RSS)
   ├── 네이버 뉴스 (4개 키워드)
   └── 구글 뉴스 (6개 키워드) ⭐
   
2. PDF 처리
   ├── pdf/ 디렉토리에서 파일 탐색
   ├── Target 키워드 포함 문단 추출
   └── Gemini로 요약
   
3. 기사 처리
   ├── 본문 스크래핑
   ├── Gemini AI 요약
   ├── Target 키워드 매칭
   └── 관련도 점수 계산
   
4. 이메일 발송
   ├── 회사 키워드 포함 기사 강조 ⭐
   ├── 관련도 높은 순 정렬
   └── Gmail SMTP 발송
```

---

## 🛠️ 설치 및 설정

### 1. 필요 조건
- Python 3.8+
- Gmail 계정 (앱 비밀번호 필요)
- Google Gemini API 키

### 2. 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-repo/hydrogen-news-v3.git
cd hydrogen-news-v3

# 2. 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 디렉토리 생성
mkdir pdf logs
```

### 3. 설정 파일 수정

**`config.py` 수정:**

```python
# 1. Google Gemini API 키
GOOGLE_API_KEY = "your-gemini-api-key-here"

# 2. 이메일 설정
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"  # 16자리 앱 비밀번호
RECEIVER_EMAIL = "receiver@example.com"
```

### 4. Gmail 앱 비밀번호 생성

1. [Google 계정 보안 설정](https://myaccount.google.com/security)
2. "2단계 인증" 활성화
3. "앱 비밀번호" 생성
4. 생성된 16자리 비밀번호를 `config.py`에 입력

### 5. Google Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. API 키 복사하여 `config.py`에 입력

---

## 🚀 사용 방법

### 1. 기본 실행

```bash
python main.py
```

### 2. PDF 브리핑 파일 추가

```bash
# pdf/ 디렉토리에 PDF 파일 복사
cp "250925_일간수소브리핑.pdf" pdf/

# 실행
python main.py
```

### 3. 진단 모드 (선택사항)

```bash
# 개별 모듈 테스트
python source_fetcher.py  # 뉴스 수집 테스트
python pdf_reader.py      # PDF 처리 테스트
python summarizer.py      # 요약 테스트
```

### 4. 실행 결과

```
================================================================================
🚀 수소 뉴스 브리핑 시스템 v3.0 시작
⏰ 실행 시간: 2025-10-16 09:00:00
================================================================================

[단계 0] PDF 브리핑 파일 처리 (키워드 중심 요약)
📁 1개 PDF 파일 발견:
  - 250925_일간수소브리핑.pdf
처리 중: 250925_일간수소브리핑.pdf
  📄 전체 텍스트 길이: 15234 글자
  📌 매칭된 키워드: 18개
  📄 관련 문단: 12개
🤖 Gemini로 요약 중... (총 12개 문단)
✅ PDF 요약 완료

[단계 1] 뉴스 소스에서 기사 수집
  - 월간수소경제
  - Hydrogen Central
  - 네이버 뉴스 (4개 키워드)
  - 구글 뉴스 (6개 키워드) ⭐ NEW!
--------------------------------------------------------------------------------
  ✅ 월간수소경제: 5개 수집
  ✅ Hydrogen Central: 5개 수집
  ✅ 네이버(수소경제): 3개
  ✅ 네이버(그린수소): 3개
  ✅ 네이버(수소연료전지): 3개
  ✅ 네이버(수소충전소): 3개
  ✅ 구글(green hydrogen): 3개
  ✅ 구글(hydrogen fuel cell): 3개
  ✅ 구글(PEM electrolyzer): 3개
  ✅ 구글(hydrogen economy): 3개
  ✅ 구글(hydrogen startup): 3개
  ✅ 구글(AEM electrolyzer): 3개

📊 총 42개 기사 수집 완료 (중복 제거 후)

📌 전체 기사 수 제한: 42개 → 15개

[단계 2] 15개 기사 처리 (스크래핑 + 요약)
...
✅ 총 15개 기사 처리 완료

[단계 3] 이메일 본문 생성
[단계 4] 이메일 발송
✅ 이메일 발송 완료!

================================================================================
🎉 수소 뉴스 브리핑 v3.0 완료!
================================================================================
```

---

## 🔍 트러블슈팅

### 1. 크롤링 실패

**문제:** 특정 사이트 크롤링 실패 (403, 404 등)

**해결:**
```bash
# logs/failed_sources.txt 확인
cat logs/failed_sources.txt

# config.py에서 해당 소스 주석 처리
```

### 2. PDF 읽기 실패

**문제:** `PyPDF2 설치되지 않음`

**해결:**
```bash
pip install PyPDF2
```

### 3. 이메일 발송 실패

**문제:** `Authentication failed`

**해결:**
1. Gmail 앱 비밀번호 재생성
2. `config.py`에 정확히 입력 (공백 없이 16자리)

### 4. Gemini API 오류

**문제:** `API key not valid`

**해결:**
1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 확인
2. `config.py`에 정확히 입력

---

## 📊 실행 결과 예시

### 이메일 예시

```
제목: [수소 브리핑 v3.0] 2025-10-16 - 15개 기사

📰 2025-10-16 수소 뉴스 브리핑
v3.0 - Target 키워드 중심 | 총 15개 기사

📊 브리핑 요약
• 총 기사: 15개
• 회사 키워드 포함: 8개 ⭐
• 기술 키워드 포함: 12개
• PDF 브리핑: success

📄 월간수소경제 PDF 브리핑 요약
매칭 키워드: Electric Hydrogen, PEM 수전해, 연료전지, ...
관련 문단: 12개

📌 핵심 내용:
• Electric Hydrogen가 새로운 PEM 수전해 시스템 발표...
• ...

📰 수집 기사 요약

⭐ 관심 기업 Electric Hydrogen, 혁신적인 PEM 수전해...
출처: 구글뉴스(PEM electrolyzer) | 원문 링크
⭐ 관심 기업: Electric Hydrogen
🔧 기술 키워드: PEM 수전해, 촉매 사용량, 내구성
...

현대건설, 국내 최초 상업용 수전해 기반 수소 생산기지 준공
출처: 월간수소경제 | 원문 링크
🔧 기술 키워드: 수전해 시스템, 그린수소, 재생에너지
...
```

---

## 🔮 향후 계획

### v4.0 (예정)
- [ ] 노션 API 연동 (연도별 이슈 정리)
- [ ] 웹 대시보드 (Flask/Streamlit)
- [ ] 추가 해외 소스 (Hydrogen Tech World, The Hydrogen Standard)
- [ ] 중국어 뉴스 소스 추가

### v5.0 (예정)
- [ ] NAS 서버 연동 (PDF 자동 저장)
- [ ] 슬랙/텔레그램 알림
- [ ] 데이터베이스 (기사 히스토리)
- [ ] 주간/월간 리포트

---

## 📝 라이센스

MIT License

---

## 👥 기여

- **개발자:** 최정현
- **소속:** 하이스케이프 (HYSCAPE)
- **기간:** 2024.09 - 2024.12
- **문의:** your_email@example.com

---

## 🙏 감사

- **Google Gemini API** - AI 요약
- **월간수소경제** - 주요 뉴스 소스
- **Hydrogen Central** - RSS 피드
- **Version 5 PDF** - Target 키워드 및 회사 리스트

---

**v3.0 - 2025.10.16**