# 🚀 빠른 시작 가이드

## 1단계: 환경 설정 (5분)

### 1.1 가상환경 생성 (권장)
```bash
cd government_support_tracker
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 1.2 패키지 설치
```bash
pip install -r requirements.txt
```

---

## 2단계: 첫 실행 전 체크리스트

### ✅ 필수 작업
- [ ] `config.yaml`에서 회사 정보 확인
- [ ] 크롤링할 사이트 활성화 여부 확인

### ⚠️ 선택 작업 (나중에 해도 됨)
- [ ] Slack 웹훅 URL 설정
- [ ] 키워드 커스터마이징

---

## 3단계: 첫 실행 (테스트)

```bash
python main.py
```

**예상 결과:**
- K-Startup 사이트 크롤링 시도
- 공고 목록 수집 (HTML 구조 문제로 실패할 수 있음 → 정상)
- 로그 파일 생성: `tracker.log`

---

## 4단계: K-Startup HTML 구조 분석 (핵심!)

현재 `k_startup_scraper.py`는 **일반적인 게시판 구조**로 작성되어 있습니다.  
실제 K-Startup 사이트에 맞게 수정이 필요합니다.

### 4.1 브라우저 개발자 도구로 확인
1. https://www.k-startup.go.kr/web/contents/biznotify.do?schM=list 접속
2. `F12` 누르기 (개발자 도구)
3. 공고 목록 HTML 구조 확인

### 4.2 수정이 필요한 부분
`scrapers/k_startup_scraper.py` 파일에서:

```python
def _parse_list_page(self, soup: BeautifulSoup) -> List[Dict]:
    # 🔍 여기를 실제 HTML 구조에 맞게 수정
    
    # 예시 1: 테이블 형식
    rows = soup.select('table.board-list tbody tr')
    
    # 예시 2: 리스트 형식
    rows = soup.select('div.board-list ul li')
    
    # 예시 3: 카드 형식
    rows = soup.select('div.card-list .card-item')
```

### 4.3 확인 방법
```python
# 임시로 HTML을 출력해서 구조 확인
print(soup.prettify())
```

---

## 5단계: IRIS, Bizinfo 크롤러 추가

### 5.1 IRIS Scraper 템플릿
```python
# scrapers/iris_scraper.py 생성
from scrapers.base_scraper import BaseScraper

class IRISScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config, site_name='iris')
        self.base_url = "https://www.iris.go.kr"
        # TODO: 실제 공고 목록 URL 확인
        self.list_url = f"{self.base_url}/..."
    
    def fetch_announcements(self):
        # TODO: IRIS 사이트 크롤링 로직
        pass
    
    def parse_announcement(self, raw_data):
        # TODO: 데이터 파싱
        pass
```

### 5.2 main.py에 등록
```python
# main.py 수정
from scrapers.iris_scraper import IRISScraper

self.scraper_registry = {
    'KStartupScraper': KStartupScraper,
    'IRISScraper': IRISScraper,  # 추가
}
```

---

## 6단계: Slack 알림 연동 (선택)

### 6.1 Slack Webhook URL 발급
1. https://api.slack.com/messaging/webhooks 접속
2. 워크스페이스 선택
3. Webhook URL 복사

### 6.2 config.yaml 수정
```yaml
slack:
  enabled: true
  webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  channel: "#정부지원사업"
```

### 6.3 notifiers/slack_notifier.py 작성
```python
from slack_sdk.webhook import WebhookClient

def send_notification(webhook_url, announcements):
    client = WebhookClient(webhook_url)
    
    message = f"🎯 신규 공고 {len(announcements)}건 발견!"
    # TODO: 메시지 포맷팅
    
    client.send(text=message)
```

---

## 7단계: 스케줄링 (자동 실행)

### Option A: Cron (Linux/Mac)
```bash
# 매일 오전 9시 실행
0 9 * * * cd /path/to/project && python main.py
```

### Option B: Task Scheduler (Windows)
1. "작업 스케줄러" 실행
2. 새 작업 생성
3. 트리거: 매일 오전 9시
4. 동작: `python main.py` 실행

### Option C: Python APScheduler
```python
# scheduler.py 생성
from apscheduler.schedulers.blocking import BlockingScheduler
from main import main

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=9)
def scheduled_task():
    main()

scheduler.start()
```

---

## 🐛 문제 해결 (Troubleshooting)

### 문제 1: 크롤링이 안 됨
**원인**: HTML 구조가 코드와 다름  
**해결**: `_parse_list_page()` 메소드 수정

### 문제 2: 필터링 결과가 너무 적음
**원인**: 키워드가 너무 엄격함  
**해결**: `config.yaml`에서 키워드 추가/완화

### 문제 3: 동적 페이지 크롤링 실패
**원인**: JavaScript로 렌더링되는 페이지  
**해결**: Selenium 사용
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
```

---

## 📝 다음 단계 우선순위

### Week 1: 기본 크롤링 완성
- [x] 프로젝트 구조 설계
- [ ] K-Startup HTML 구조 분석 및 수정
- [ ] 테스트 실행 및 디버깅

### Week 2: 사이트 추가
- [ ] IRIS Scraper 구현
- [ ] Bizinfo Scraper 구현

### Week 3: 고도화
- [ ] Slack 알림 연동
- [ ] 스케줄링 설정
- [ ] 에러 핸들링 강화

---

## 💡 팁

1. **작은 것부터 시작**: K-Startup 1개 사이트만 제대로 작동시킨 후 확장
2. **로그 활용**: `tracker.log` 파일로 디버깅
3. **테스트 데이터 사용**: 크롤링 전에 샘플 HTML로 파싱 테스트
4. **키워드 조정**: 처음엔 넓게, 점차 좁히기

---

## 📞 도움이 필요하면

- 로그 파일 (`tracker.log`) 확인
- 에러 메시지와 함께 문의
- HTML 구조를 공유하면 더 빠른 해결 가능

---

**화이팅! 🚀**