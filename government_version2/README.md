# 정부 지원 사업 주간 추천 시스템

Hyscape를 위한 정부 지원 사업 자동 추천 및 알림 시스템

## 📋 프로젝트 개요

정부 사이트(K-Startup, IRIS, Bizinfo)를 자동으로 크롤링하여 수소·수전해 기술 분야에 적합한 지원 사업을 찾아내고 알림을 제공하는 시스템입니다.

### 주요 기능

- ✅ **다중 사이트 크롤링**: 여러 정부 지원 사이트를 동시에 모니터링
- ✅ **이원화된 필터링 전략**: 
  - Type A (기술 중심): 순수 R&D 사업용
  - Type B (지원 중심): 창업/성장 지원 사업용
- ✅ **중복 방지**: 히스토리 관리로 이미 확인한 공고 제외
- ✅ **확장 가능한 아키텍처**: 새 사이트 추가가 쉬운 Strategy Pattern
- ✅ **Slack 알림** (예정): 신규 공고 자동 알림

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론 (또는 파일 복사)
cd government_support_tracker

# 의존성 설치
pip install -r requirements.txt
```

### 2. 설정

`config.yaml` 파일을 열어 필요한 설정을 수정:

```yaml
# Slack 웹훅 URL 설정 (선택사항)
slack:
  enabled: true
  webhook_url: "YOUR_WEBHOOK_URL"
  
# 키워드 커스터마이징 가능
keywords:
  tech:
    - "수소"
    - "연료전지"
    # ...
```

### 3. 실행

```bash
python main.py
```

---

## 📁 프로젝트 구조

```
government_support_tracker/
├── config.yaml              # 설정 파일 (키워드, URL 등)
├── base_scraper.py          # 모든 크롤러의 부모 클래스
├── k_startup_scraper.py     # K-Startup 구현체
├── keyword_filter.py        # Type A/B 필터링 로직
├── main.py                  # 메인 실행 스크립트
├── requirements.txt         # 의존성 패키지
├── data/
│   └── scraped_history.json # 크롤링 히스토리 (자동 생성)
└── tracker.log              # 실행 로그 (자동 생성)
```

---

## 🔧 필터링 전략

### Type A: 기술 중심 (IRIS용)
- **조건**: 핵심 기술 키워드가 **반드시** 1개 이상 포함
- **대상**: 순수 R&D, 기술 개발 자금 사업
- **예시**: "수소", "연료전지", "재생에너지"

### Type B: 지원 중심 (K-Startup, Bizinfo용)
- **조건**: (기술 키워드) **OR** (지원 키워드 **AND** 자격 키워드)
- **대상**: 마케팅, 사업화, 글로벌 진출 지원
- **예시**: 
  - "수소 + 마케팅" ✅
  - "마케팅 + 성남" ✅
  - "일반 제조업 + 부산" ❌

---

## 🔌 새 사이트 추가하기

새로운 정부 사이트를 추가하는 방법:

### Step 1: 크롤러 클래스 작성

```python
# iris_scraper.py
from base_scraper import BaseScraper

class IRISScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config, site_name='iris')
    
    def fetch_announcements(self):
        # IRIS 사이트 크롤링 로직 구현
        pass
    
    def parse_announcement(self, raw_data):
        # 데이터 파싱 로직 구현
        pass
```

### Step 2: config.yaml에 사이트 추가

```yaml
sites:
  iris:
    name: "IRIS"
    enabled: true
    url: "https://www.iris.go.kr/index.do"
    filter_strategy: "type_a"
    scraper_class: "IRISScraper"
```

### Step 3: main.py에 크롤러 등록

```python
self.scraper_registry = {
    'KStartupScraper': KStartupScraper,
    'IRISScraper': IRISScraper,  # 추가
}
```

**끝!** 메인 로직 수정 없이 사이트 추가 완료

---

## 📊 출력 예시

```
================================================================================
🎯 추천 공고: 3건
================================================================================

[1] 2024년 그린수소 기술개발 지원사업
    출처: K-Startup
    마감일: 2024-12-31
    매칭 점수: 45점
    매칭 키워드: 수소, 재생에너지, 성남
    URL: https://...

[2] 경기도 청년 스타트업 글로벌 진출 지원
    출처: K-Startup
    마감일: 2024-12-25
    매칭 점수: 23점
    매칭 키워드: 마케팅, 글로벌, 경기
    URL: https://...

================================================================================
📊 키워드 통계
================================================================================
  수소: 2회
  마케팅: 2회
  경기: 2회
  ...
```

---

## 🛠️ 다음 단계 (TODO)

### 우선순위 높음
- [ ] **IRIS Scraper 구현** (순수 R&D 사업용)
- [ ] **Bizinfo Scraper 구현** (K-Startup과 유사)
- [ ] **K-Startup 실제 HTML 구조 분석 및 수정**
  - 현재 코드는 일반적인 구조로 작성됨
  - 실제 사이트 구조에 맞게 셀렉터 수정 필요

### 우선순위 중간
- [ ] **Slack 알림 구현**
  - slack-sdk 사용
  - 알림 메시지 템플릿 작성
- [ ] **스케줄링 추가** (일일 자동 실행)
  - cron 또는 APScheduler 사용
- [ ] **상세 페이지 크롤링 최적화**
  - 동적 페이지 대응 (Selenium)
  - 병렬 처리로 속도 개선

### 우선순위 낮음
- [ ] **데이터베이스 연동** (SQLite 또는 PostgreSQL)
- [ ] **웹 대시보드** (Flask/Streamlit)
- [ ] **이메일 알림** (대안 채널)

---

## ⚠️ 주의사항

### 크롤링 에티켓
1. **robots.txt 확인**: 크롤링 허용 여부 체크
2. **요청 간격**: 최소 1초 이상 대기 (현재 코드에 구현됨)
3. **User-Agent 설정**: 봇임을 명시
4. **과도한 요청 금지**: 서버 부하 방지

### 법적 고려사항
- 공개된 정보만 수집
- 개인정보 수집 금지
- 저작권 존중

---

## 📝 개발 노트

### 설계 원칙
1. **확장성**: Strategy Pattern으로 사이트 추가 용이
2. **유지보수성**: 키워드는 코드가 아닌 설정 파일에서 관리
3. **실용성**: 즉시 실행 가능한 구조
4. **안정성**: 에러 핸들링 및 로깅 철저

### 기술 스택
- Python 3.8+
- requests + BeautifulSoup (크롤링)
- PyYAML (설정 관리)
- slack-sdk (알림)

---

## 🤝 기여

버그 리포트, 기능 제안, 코드 개선은 언제든 환영합니다!

---

## 📧 문의

**프로젝트 담당**: Hyscape SW 인턴팀  
**회사**: Hyscape (수전해 기술 스타트업)

---

**Made with ❤️ for Hyscape**