# H2HUB 브리핑 자동화 시스템 v2.0 📘

## 🎯 프로젝트 개요

한국수소연합(H2HUB)의 일간/주간 수소 이슈 브리핑을 자동으로 수집, 분석, 아카이빙하는 엔드-투-엔드 자동화 시스템입니다.

**핵심 기능:**
- 📥 H2HUB 웹사이트에서 PDF 자동 다운로드
- 🤖 Google Gemini AI로 내용 분석 (요약, 감성, 카테고리, 키워드)
- 📊 Notion 데이터베이스에 자동 업로드
- 📦 처리 완료된 PDF 자동 아카이빙
- ⏰ 크론잡으로 완전 자동화

---

## 📊 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    H2HUB 브리핑 자동화 시스템                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────┐
        │   1. PDF 수집 (article_collector.py)  │
        │   - H2HUB 웹 크롤링                    │
        │   - PDF 다운로드                       │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   2. PDF 분석 (article_analyzer.py)   │
        │   - 텍스트 추출 (pdfplumber)           │
        │   - AI 분석 (Gemini 2.0 Flash)        │
        │     • 요약 (3줄)                       │
        │     • 감성 분석 (긍정/부정/중립)        │
        │     • 카테고리 (기관/정책/산업계 등)     │
        │     • 키워드 추출 (3-5개)              │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   3. Notion 업로드 (notion_uploader.py)│
        │   - 페이지 자동 생성                    │
        │   - 속성 매핑                          │
        │   - Select/Multi-select 처리          │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   4. 아카이빙 (run_automation.sh)     │
        │   - PDF → pdf_archive/ 이동           │
        │   - 백업 생성                          │
        │   - 로그 저장                          │
        └──────────────────────────────────────┘
```

---

## 🗂️ 파일 구조

```
h2hub_automation/
│
├── 🔧 실행 스크립트
│   ├── run_automation.sh          # 메인 자동화 스크립트 ⭐
│   ├── install.sh                 # 설치 스크립트
│   └── check_notion_properties.py # Notion DB 속성 확인
│
├── 🐍 Python 모듈
│   ├── main.py                    # 통합 워크플로우
│   ├── config.py                  # 설정 파일
│   ├── article_collector.py       # 웹 크롤링 & PDF 다운로드
│   ├── article_analyzer.py        # PDF 분석 (Gemini)
│   └── notion_uploader.py         # Notion 업로드
│
├── 📚 문서
│   ├── QUICKSTART.md              # 빠른 시작 ⭐
│   ├── AUTOMATION_GUIDE.md        # 자동화 상세 가이드
│   ├── README.md                  # 프로젝트 설명
│   └── TEST_GUIDE.md              # 테스트 가이드
│
├── 📦 의존성
│   ├── requirements.txt           # Python 패키지
│   └── .gitignore                 # Git 제외 파일
│
└── 📁 생성되는 디렉토리
    ├── logs/                      # 실행 로그
    ├── backups/                   # PDF 백업
    ├── downloads/                 # 임시 다운로드
    └── venv/                      # Python 가상환경
```

---

## 🚀 빠른 시작

### 1. 설치
```bash
chmod +x install.sh
./install.sh
```

### 2. 실행
```bash
./run_automation.sh
```

### 3. 자동화
```bash
crontab -e
# 매일 오전 9시 실행
0 9 * * * /path/to/run_automation.sh >> /path/to/logs/cron.log 2>&1
```

📖 **더 자세한 내용:** [QUICKSTART.md](QUICKSTART.md)

---

## 🎮 사용 예시

### 기존 PDF 처리
```bash
./run_automation.sh
```
→ `../pdf/` 폴더의 모든 PDF 처리

### 웹 크롤링
```bash
./run_automation.sh --pages 3
```
→ H2HUB에서 3페이지 크롤링

### 테스트 실행
```bash
./run_automation.sh --dry-run
```
→ 실제 실행 없이 테스트

### 수동 Python 실행
```bash
# Notion 테스트
python main.py --test-notion

# 특정 PDF 분석
python main.py --existing-pdfs /path/to/specific.pdf

# 웹 크롤링
python main.py --pages 1
```

---

## ⚙️ 설정 (config.py)

### API 키 설정
```python
GOOGLE_API_KEY = "your_gemini_api_key"
NOTION_API_KEY = "your_notion_api_key"
NOTION_DATABASE_ID = "your_database_id"
```

### Notion 데이터베이스 속성
| 속성명 | 타입 | 설명 |
|--------|------|------|
| 제목 | Title | PDF 제목 |
| date | Date | 브리핑 날짜 |
| 요약 | Rich Text | AI 요약 (3줄) |
| url | URL | 원본 PDF 링크 |
| 기술전망 | Select | 🟢긍정/🔴부정/🟡중립 |
| category | Select | 기관/정책/지자체/산업계/연구계/해외 |
| 키워드 | Multi-select | 핵심 키워드 3-5개 |

---

## 📊 워크플로우 상세

### 모드 1: 기존 PDF 처리 (기본)
```
1. ../pdf/ 폴더 스캔
2. PDF 파일 발견
3. 백업 생성 (backups/)
4. PDF 텍스트 추출 (pdfplumber)
5. Gemini AI 분석
   - 요약 생성
   - 감성 분석
   - 카테고리 분류
   - 키워드 추출
6. Notion 페이지 생성
7. PDF → pdf_archive/ 이동
8. 로그 저장
```

### 모드 2: 웹 크롤링
```
1. H2HUB 웹사이트 접속
2. 브리핑 목록 크롤링
3. PDF 다운로드 (downloads/)
4. [모드 1과 동일한 프로세스]
```

---

## 🔍 모니터링

### 실행 로그 확인
```bash
tail -f logs/automation_*.log
```

### 크론 로그 확인
```bash
tail -f logs/cron.log
```

### Notion 데이터베이스
- 실시간으로 업로드된 브리핑 확인
- 필터/정렬로 원하는 정보 검색

---

## 🛠️ 트러블슈팅

| 문제 | 해결 방법 |
|------|-----------|
| Notion 업로드 실패 | `python main.py --test-notion` |
| PDF 분석 실패 | PDF 파일 손상 확인 |
| 크론잡 안 됨 | 절대 경로 사용, 권한 확인 |
| 메모리 부족 | 페이지 수 줄이기 |

📖 **상세 가이드:** [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)

---

## 📦 의존성

### Python 패키지
- `requests` - HTTP 요청
- `beautifulsoup4` - HTML 파싱
- `pdfplumber` - PDF 텍스트 추출
- `google-generativeai` - Gemini AI
- `notion-client` - Notion API

### 시스템 요구사항
- Python 3.8+
- Linux/macOS/Windows
- 인터넷 연결
- 최소 1GB RAM

---

## 🎯 프로젝트 목표

### 달성된 목표 ✅
- ✅ 완전 자동화 (크론잡)
- ✅ PDF 수집부터 Notion 업로드까지 원클릭
- ✅ AI 분석 (요약, 감성, 카테고리, 키워드)
- ✅ 자동 아카이빙
- ✅ 로그 기록
- ✅ 백업 시스템

### 향후 개선 가능 항목 💡
- [ ] Slack 알림 연동
- [ ] 대시보드 구축 (Streamlit)
- [ ] 중복 PDF 감지
- [ ] 다국어 지원
- [ ] PDF OCR 지원 (스캔본)

---

## 📝 개발 히스토리

- **v1.0** (2025.11) - 기본 PDF 분석 및 Notion 업로드
- **v1.5** (2025.11) - 웹 크롤링 기능 추가
- **v2.0** (2025.12) - 완전 자동화 시스템 구축
  - 프로덕션 레벨 자동화 스크립트
  - 크론잡 지원
  - 로깅 시스템
  - 백업 기능
  - 에러 처리 강화

---

## 👤 작성자

**Hyscape SW Intern**
- 수소 산업 자동화 시스템 개발
- 2025년 인턴십 프로젝트

---

## 📄 라이선스

Internal Use Only - Hyscape

---

## 🔗 관련 링크

- [한국수소연합(H2HUB)](https://h2hub.or.kr)
- [Notion API 문서](https://developers.notion.com)
- [Google Gemini API](https://ai.google.dev)

---

## 📞 지원

문제 발생 시:
1. 로그 파일 확인
2. `--dry-run` 테스트
3. `--test-notion` 실행
4. [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) 참고

---

**🎉 이제 H2HUB 브리핑 자동화를 시작하세요!**

```bash
./run_automation.sh
```