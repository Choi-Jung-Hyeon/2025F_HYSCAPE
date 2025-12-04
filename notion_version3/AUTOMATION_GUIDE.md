# H2HUB 브리핑 자동화 시스템 운영 가이드

## 📋 목차
1. [설치](#설치)
2. [기본 사용법](#기본-사용법)
3. [크론잡 설정](#크론잡-설정)
4. [로그 관리](#로그-관리)
5. [트러블슈팅](#트러블슈팅)

---

## 🚀 설치

### 1단계: 설치 스크립트 실행
```bash
chmod +x install.sh
./install.sh
```

설치 스크립트가 자동으로:
- ✅ Python 가상환경 생성
- ✅ 필요한 패키지 설치
- ✅ 디렉토리 구조 생성
- ✅ Notion 연결 테스트

### 2단계: 설정 파일 확인
```bash
# config.py에서 API 키 확인
cat config.py | grep API_KEY
```

---

## 🎯 기본 사용법

### 기존 PDF 처리
```bash
./run_automation.sh
```
- `../pdf/` 폴더의 모든 PDF 처리
- 분석 → Notion 업로드
- 완료 후 `../pdf_archive/`로 이동

### 웹 크롤링 모드
```bash
./run_automation.sh --pages 3
```
- H2HUB 웹사이트에서 3페이지 크롤링
- PDF 다운로드 → 분석 → 업로드

### 테스트 실행 (Dry Run)
```bash
./run_automation.sh --dry-run
```
- 실제 실행 없이 테스트
- 어떤 작업이 수행될지 확인

### 백업 없이 실행
```bash
./run_automation.sh --no-backup
```
- PDF 백업을 생성하지 않음
- 디스크 공간 절약

---

## ⏰ 크론잡 설정

### 크론탭 편집
```bash
crontab -e
```

### 예시 1: 매일 오전 9시 실행
```cron
0 9 * * * /path/to/h2hub_automation/run_automation.sh >> /path/to/h2hub_automation/logs/cron.log 2>&1
```

### 예시 2: 매주 월요일 오전 9시
```cron
0 9 * * 1 /path/to/h2hub_automation/run_automation.sh --pages 1 >> /path/to/h2hub_automation/logs/cron.log 2>&1
```

### 예시 3: 평일 오전 9시
```cron
0 9 * * 1-5 /path/to/h2hub_automation/run_automation.sh >> /path/to/h2hub_automation/logs/cron.log 2>&1
```

### 예시 4: 매일 오전 9시, 오후 6시
```cron
0 9,18 * * * /path/to/h2hub_automation/run_automation.sh >> /path/to/h2hub_automation/logs/cron.log 2>&1
```

### 크론 시간 형식
```
분 시 일 월 요일 명령어
*  *  *  *  *   command

분: 0-59
시: 0-23
일: 1-31
월: 1-12
요일: 0-7 (0과 7은 일요일)
```

### 크론잡 확인
```bash
# 현재 설정된 크론잡 확인
crontab -l

# 크론 로그 확인
tail -f logs/cron.log
```

---

## 📊 로그 관리

### 로그 위치
```
h2hub_automation/
├── logs/
│   ├── automation_20241205_090000.log  # 자동화 실행 로그
│   ├── automation_20241206_090000.log
│   └── cron.log                        # 크론잡 실행 로그
```

### 로그 확인
```bash
# 최신 로그 보기
tail -f logs/automation_*.log

# 크론 로그 보기
tail -f logs/cron.log

# 특정 날짜 로그 검색
grep "2024-12-05" logs/automation_*.log

# 에러만 보기
grep "ERROR" logs/automation_*.log
```

### 로그 정리 (오래된 로그 삭제)
```bash
# 30일 이상된 로그 삭제
find logs/ -name "*.log" -mtime +30 -delete

# 크론잡으로 자동 정리 (매월 1일 실행)
0 0 1 * * find /path/to/h2hub_automation/logs/ -name "*.log" -mtime +30 -delete
```

---

## 🔍 트러블슈팅

### 1. Notion 업로드 실패
```bash
# Notion 연결 테스트
python main.py --test-notion

# 데이터베이스 속성 확인
python check_notion_properties.py
```

**해결 방법:**
- `config.py`에서 NOTION_API_KEY와 NOTION_DATABASE_ID 확인
- Notion에서 Integration 권한 확인
- 데이터베이스 속성명이 정확한지 확인

### 2. PDF 분석 실패
```bash
# 개별 PDF 테스트
python main.py --existing-pdfs /path/to/pdf/specific_file.pdf
```

**해결 방법:**
- PDF 파일이 손상되지 않았는지 확인
- PDF 텍스트 추출 가능한지 확인 (스캔본이 아닌지)
- `config.py`에서 GOOGLE_API_KEY 확인

### 3. 크론잡이 실행 안 됨
```bash
# 크론 서비스 상태 확인
sudo systemctl status cron

# 크론 로그 확인
tail -f logs/cron.log

# 수동 실행 테스트
./run_automation.sh --dry-run
```

**해결 방법:**
- 크론잡에서 절대 경로 사용
- 실행 권한 확인: `chmod +x run_automation.sh`
- Python 가상환경 경로 확인

### 4. 메모리 부족
```bash
# 시스템 리소스 확인
free -h
df -h
```

**해결 방법:**
- 한 번에 처리하는 페이지 수 줄이기
- 오래된 로그/백업 삭제
- PDF 아카이브 정리

---

## 📁 디렉토리 구조

```
h2hub_automation/
├── run_automation.sh      # 메인 실행 스크립트
├── install.sh             # 설치 스크립트
├── main.py                # Python 메인
├── config.py              # 설정 파일
├── article_collector.py   # PDF 수집
├── article_analyzer.py    # PDF 분석
├── notion_uploader.py     # Notion 업로드
├── requirements.txt       # Python 패키지
│
├── logs/                  # 실행 로그
│   ├── automation_*.log
│   └── cron.log
│
├── backups/               # PDF 백업
│   └── 20241205_090000/
│
├── downloads/             # 다운로드 임시 폴더
│
└── venv/                  # Python 가상환경

../pdf/                    # 처리할 PDF (외부)
../pdf_archive/            # 처리 완료 PDF (외부)
```

---

## 🔧 고급 설정

### 환경변수로 설정
```bash
# .bashrc 또는 .zshrc에 추가
export GOOGLE_API_KEY="your_key_here"
export NOTION_API_KEY="your_key_here"
export NOTION_DATABASE_ID="your_db_id_here"
export PDF_DIR="/custom/pdf/path"
```

### Systemd 타이머 사용 (크론 대체)
```bash
# /etc/systemd/system/h2hub-automation.service
[Unit]
Description=H2HUB Briefing Automation
After=network.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/h2hub_automation
ExecStart=/path/to/h2hub_automation/run_automation.sh
StandardOutput=append:/path/to/h2hub_automation/logs/systemd.log
StandardError=append:/path/to/h2hub_automation/logs/systemd.log

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/systemd/system/h2hub-automation.timer
[Unit]
Description=H2HUB Automation Timer
Requires=h2hub-automation.service

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# 활성화
sudo systemctl enable h2hub-automation.timer
sudo systemctl start h2hub-automation.timer

# 상태 확인
sudo systemctl status h2hub-automation.timer
```

---

## 📞 지원

문제가 발생하면:
1. 로그 파일 확인
2. `--dry-run` 모드로 테스트
3. Notion 연결 테스트 실행
4. GitHub Issues에 문의

---

## 📝 체크리스트

설치 후 확인:
- [ ] `./install.sh` 실행 완료
- [ ] `config.py` API 키 설정 완료
- [ ] `python main.py --test-notion` 성공
- [ ] `./run_automation.sh --dry-run` 테스트 성공
- [ ] 크론잡 설정 완료
- [ ] 로그 파일 생성 확인
- [ ] PDF 아카이브 동작 확인

운영 중 주기적 확인:
- [ ] 로그 파일 용량 확인 (매월)
- [ ] 백업 폴더 정리 (매월)
- [ ] Notion API 할당량 확인 (필요시)
- [ ] PDF 아카이브 정리 (분기별)