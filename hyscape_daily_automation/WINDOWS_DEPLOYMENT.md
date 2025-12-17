# Windows 환경 배포 가이드

## 목표 환경
- **배포 위치**: `H:\부서\cjh\hyscape_daily_automation`
- **PDF 디렉토리**: `H:\부서\cjh\pdf\`
- **Python 경로**: `C:\Users\jjeor\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe`

## 배포 절차

### 1단계: 파일 복사
1. WSL 환경에서 Windows로 전체 디렉토리 복사:
   ```bash
   # WSL에서 실행
   cp -r ~/2025F_HYSCAPE/hyscape_daily_automation /mnt/h/부서/cjh/
   cp -r ~/2025F_HYSCAPE/pdf /mnt/h/부서/cjh/
   ```

2. 또는 Windows 탐색기에서:
   - `\\wsl$\Ubuntu\home\fourmi103\2025F_HYSCAPE\hyscape_daily_automation` 복사
   - `H:\부서\cjh\` 에 붙여넣기

### 2단계: 환경 설정
1. `H:\부서\cjh\hyscape_daily_automation\` 디렉토리로 이동
2. `.env.template` 파일을 `.env` 로 복사
3. `.env` 파일 편집:
   ```env
   # Google Gemini API
   GOOGLE_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.0-flash

   # Gmail SMTP Settings
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password_here
   ```

### 3단계: Python 의존성 설치
1. `setup_windows.bat` 더블클릭 또는 명령 프롬프트에서:
   ```cmd
   cd /d H:\부서\cjh\hyscape_daily_automation
   setup_windows.bat
   ```

2. 설치되는 주요 패키지:
   - `google-generativeai`: Gemini AI API
   - `pdfplumber`, `PyPDF2`: PDF 처리
   - `requests`, `beautifulsoup4`: 웹 크롤링
   - `feedparser`: RSS 파싱
   - `notion-client`: Notion 연동
   - `python-dotenv`: 환경 변수 관리
   - `PyYAML`: YAML 설정 파일

### 4단계: 수동 테스트
1. PDF 파일을 `H:\부서\cjh\pdf\` 디렉토리에 배치
2. `RUN_autobriefing_windows.bat` 더블클릭
3. 콘솔 출력 확인:
   - PDF 브리핑 처리 확인
   - 정부지원사업 크롤링 확인
   - 뉴스 수집 및 요약 확인
   - 이메일 발송 확인
4. 로그 파일 확인: `H:\부서\cjh\hyscape_daily_automation\logs\unified_automation.log`

### 5단계: 작업 스케줄러 설정

#### 방법 1: GUI 사용
1. **작업 스케줄러** 열기 (`Win + R` → `taskschd.msc`)
2. **작업 만들기** 클릭
3. **일반 탭**:
   - 이름: `Hyscape Daily Automation`
   - 설명: `수소 뉴스 브리핑 자동화`
   - 보안 옵션: "사용자의 로그온 여부와 관계없이 실행" 선택
4. **트리거 탭**:
   - **새로 만들기** 클릭
   - 작업 시작: `일정에 따라`
   - 설정: `매일`
   - 시작 시간: `오전 8:00` (원하는 시간으로 조정)
   - 사용: ✓ 체크
5. **동작 탭**:
   - **새로 만들기** 클릭
   - 동작: `프로그램 시작`
   - 프로그램/스크립트: `H:\부서\cjh\hyscape_daily_automation\RUN_autobriefing_windows.bat`
   - 시작 위치: `H:\부서\cjh\hyscape_daily_automation`
6. **조건 탭**:
   - "컴퓨터의 AC 전원이 켜진 경우에만" 체크 해제 (노트북의 경우)
7. **설정 탭**:
   - "요청 시 작업 실행 허용" 체크
   - "작업이 실패하면 다시 시작 간격" 설정: `1분`, 시도 횟수: `3`
8. **확인** 클릭

#### 방법 2: PowerShell 사용
```powershell
# 관리자 권한으로 PowerShell 실행
$action = New-ScheduledTaskAction -Execute "H:\부서\cjh\hyscape_daily_automation\RUN_autobriefing_windows.bat" -WorkingDirectory "H:\부서\cjh\hyscape_daily_automation"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$principal = New-ScheduledTaskPrincipal -UserId "jjeor" -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "Hyscape Daily Automation" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "수소 뉴스 브리핑 자동화"
```

## 디렉토리 구조
```
H:\부서\cjh\
├── hyscape_daily_automation\          # 메인 프로그램
│   ├── main_unified.py                # 통합 실행 스크립트
│   ├── config_production.py           # 설정 파일
│   ├── config_production.yaml         # 정부지원사업 설정
│   ├── .env                           # 환경 변수 (비밀)
│   ├── .env.template                  # 환경 변수 템플릿
│   ├── requirements.txt               # Python 의존성
│   ├── RUN_autobriefing_windows.bat  # 실행 스크립트
│   ├── setup_windows.bat              # 설치 스크립트
│   ├── modules\                       # 기능 모듈
│   │   ├── news_briefing.py          # 뉴스 브리핑
│   │   ├── gov_support.py            # 정부지원사업
│   │   └── notion_archive.py         # Notion 아카이브
│   ├── dependencies\                  # 공통 의존성
│   │   ├── source_fetcher\           # 뉴스 소스 수집
│   │   ├── gov_support\              # 정부지원 크롤링
│   │   ├── notifier.py               # 이메일 발송
│   │   └── content_scraper.py        # 웹 스크래핑
│   ├── shared\                        # 공유 유틸리티
│   │   ├── pdf_analyzer.py           # PDF 처리
│   │   └── gemini_client.py          # Gemini API 클라이언트
│   └── logs\                          # 로그 파일
│       └── unified_automation.log
└── pdf\                               # PDF 브리핑 파일
    ├── 251203_일간 수소 이슈 브리핑.pdf
    ├── 251204_일간 수소 이슈 브리핑.pdf
    └── 251205_일간 수소 이슈 브리핑.pdf
```

## 문제 해결

### 1. Python을 찾을 수 없음
- Python 경로 확인:
  ```cmd
  where python
  ```
- Microsoft Store에서 Python 3.13 설치 확인

### 2. 모듈을 찾을 수 없음
- 의존성 재설치:
  ```cmd
  cd /d H:\부서\cjh\hyscape_daily_automation
  setup_windows.bat
  ```

### 3. PDF 파일을 찾을 수 없음
- PDF 디렉토리 확인:
  ```cmd
  dir H:\부서\cjh\pdf
  ```
- `config_production.py`의 `PDF_DIR` 설정이 자동으로 올바른 경로를 사용하는지 확인

### 4. 이메일 발송 실패
- `.env` 파일의 Gmail 설정 확인:
  - `SENDER_EMAIL`: Gmail 주소
  - `SENDER_PASSWORD`: **앱 비밀번호** (16자, 일반 비밀번호 아님)
- Gmail 앱 비밀번호 생성: https://myaccount.google.com/apppasswords

### 5. Gemini API 오류
- `.env` 파일의 `GOOGLE_API_KEY` 확인
- API 할당량 확인: https://aistudio.google.com/
- 오류 메시지 확인: `logs\unified_automation.log`

### 6. 작업 스케줄러가 실행되지 않음
- 작업 스케줄러에서 작업 기록 확인
- "사용자의 로그온 여부와 관계없이 실행" 옵션 확인
- Windows 업데이트 후 재부팅 필요 여부 확인

## 로그 확인
```cmd
cd /d H:\부서\cjh\hyscape_daily_automation\logs
type unified_automation.log
```

## 수동 실행 (디버깅)
```cmd
cd /d H:\부서\cjh\hyscape_daily_automation
"C:\Users\jjeor\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" main_unified.py
```

## 경로 설정 자동화
`config_production.py`는 자동으로 플랫폼을 감지하여 경로를 설정합니다:
- **Linux**: `/home/fourmi103/2025F_HYSCAPE/pdf/`
- **Windows**: `H:\부서\cjh\pdf\`

경로 변경이 필요한 경우 `config_production.py` 수정:
```python
# 현재 설정 (자동)
BASE_DIR = Path(__file__).parent.parent
PDF_DIR = str(BASE_DIR / "pdf")

# 수동 설정 (필요시)
# PDF_DIR = "H:\\부서\\cjh\\pdf"
```

## 연락처
- 문제 발생 시 로그 파일(`logs\unified_automation.log`)을 확인하세요
- Gemini API 관련: https://aistudio.google.com/
- Gmail 앱 비밀번호: https://myaccount.google.com/apppasswords
