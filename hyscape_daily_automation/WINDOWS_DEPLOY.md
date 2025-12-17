# Windows PowerShell 배포 가이드 (NAS 사용)

## 📦 사전 준비

### 1. NAS 서버에 파일 복사

**개인 컴퓨터에서:**
```bash
# 레포지토리를 NAS 서버로 복사
# 예: \\nas-server\shared\2025F_HYSCAPE\hyscape_daily_automation
```

또는 ZIP 파일로 압축하여 전송:
```bash
cd /home/fourmi103/2025F_HYSCAPE
zip -r hyscape_automation.zip hyscape_daily_automation/
# 이 ZIP 파일을 NAS로 복사
```

### 2. .env 파일 준비

**중요:** `.env` 파일은 Git에 없으므로 수동으로 생성 필요

**방법 1: USB로 전송**
```bash
# 개인 컴퓨터에서 .env 파일을 USB에 복사
cp /home/fourmi103/2025F_HYSCAPE/hyscape_daily_automation/.env /path/to/usb/
```

**방법 2: 내용 복사하여 수동 생성**
```bash
# 개인 컴퓨터에서 내용 출력
cat /home/fourmi103/2025F_HYSCAPE/hyscape_daily_automation/.env
# 출력된 내용을 메모장에 복사
```

---

## 🚀 회사 컴퓨터 설치 (PowerShell)

### Step 1: Python 설치 확인

```powershell
# PowerShell 관리자 권한으로 실행
python --version
```

**Python이 없다면:**
1. https://www.python.org/downloads/ 접속
2. 최신 버전 다운로드 (3.8 이상)
3. 설치 시 "Add Python to PATH" 체크 필수!

### Step 2: 프로젝트 폴더로 이동

```powershell
# NAS 서버의 프로젝트 폴더로 이동
cd \\nas-server\shared\2025F_HYSCAPE\hyscape_daily_automation

# 또는 로컬로 복사했다면
cd C:\Projects\hyscape_daily_automation
```

### Step 3: 가상환경 생성

```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\activate

# 활성화되면 프롬프트 앞에 (venv) 표시됨
```

### Step 4: 의존성 설치

```powershell
# 의존성 설치 (2-3분 소요)
pip install -r requirements.txt

# 설치 확인
pip list
```

### Step 5: .env 파일 생성

```powershell
# .env.template을 복사
copy .env.template .env

# 메모장으로 .env 파일 열기
notepad .env
```

**메모장에서 편집:**
```
GOOGLE_API_KEY=your_actual_google_api_key_here
GEMINI_MODEL=gemini-2.0-flash
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16char_app_password
NOTION_API_TOKEN=your_actual_notion_token_here
NOTION_DATABASE_ID=your_actual_database_id_here
```

**저장:** Ctrl+S, 닫기: Alt+F4

### Step 6: 테스트 실행

```powershell
# 이메일 테스트
python test_email.py

# 전체 자동화 실행
python main_unified.py
```

---

## ⚙️ 매일 자동 실행 설정

### Windows 작업 스케줄러 설정

**1. 실행 스크립트 생성 (run_daily.bat)**

```powershell
# 메모장으로 새 파일 생성
notepad run_daily.bat
```

**내용 작성:**
```batch
@echo off
cd C:\Projects\hyscape_daily_automation
call venv\Scripts\activate
python main_unified.py
pause
```

**저장:** Ctrl+S

**2. 작업 스케줄러 등록**

```powershell
# PowerShell에서 실행 (관리자 권한)
$action = New-ScheduledTaskAction -Execute "C:\Projects\hyscape_daily_automation\run_daily.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "Hyscape Daily Automation" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

**또는 GUI로 설정:**
1. `작업 스케줄러` 실행 (시작 메뉴에서 검색)
2. "작업 만들기" 클릭
3. **일반 탭:**
   - 이름: `Hyscape Daily Automation`
   - 설명: `매일 9시 자동 브리핑`
4. **트리거 탭:**
   - "새로 만들기" → 매일 오전 9:00
5. **동작 탭:**
   - "새로 만들기" → `C:\Projects\hyscape_daily_automation\run_daily.bat` 실행
6. "확인" 클릭

---

## 📁 프로젝트 구조 (Windows)

```
C:\Projects\hyscape_daily_automation\
│
├── .env                          # 수동 생성 필요
├── .env.template                 # 템플릿
├── main_unified.py               # 메인 실행 파일
├── test_email.py                 # 이메일 테스트
├── requirements.txt              # 의존성 목록
│
├── config_production.py          # 설정 파일
├── config_production.yaml        # 정부사업 설정
├── notion_config_production.py   # Notion 설정
│
├── modules\                      # 실행 모듈
│   ├── news_briefing.py
│   ├── gov_support.py
│   └── notion_archive.py
│
├── shared\                       # 공유 유틸리티
│   ├── pdf_analyzer.py
│   └── gemini_client.py
│
├── dependencies\                 # 외부 의존성
│   ├── source_fetcher\
│   ├── gov_support\
│   └── ...
│
├── logs\                         # 로그 폴더 (자동 생성)
│   └── unified_automation.log
│
└── venv\                         # 가상환경 (Step 3에서 생성)
```

---

## 🔧 트러블슈팅

### 1. Python을 찾을 수 없음

```powershell
# Python 경로 확인
where python

# PATH에 추가 (관리자 PowerShell)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Python311", [EnvironmentVariableTarget]::Machine)
```

### 2. 가상환경 활성화 실패

```powershell
# 실행 정책 변경 (관리자 PowerShell)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 활성화 시도
.\venv\Scripts\activate
```

### 3. 의존성 설치 실패

```powershell
# pip 업그레이드
python -m pip install --upgrade pip

# 의존성 재설치
pip install -r requirements.txt --no-cache-dir
```

### 4. .env 파일 로딩 안 됨

```powershell
# 파일 존재 확인
dir .env

# 파일 인코딩 확인 (UTF-8이어야 함)
# 메모장 → 파일 → 다른 이름으로 저장 → 인코딩: UTF-8

# 테스트
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('API Key:', 'OK' if os.getenv('GOOGLE_API_KEY') else 'MISSING')"
```

### 5. 방화벽 차단

```powershell
# Windows Defender 방화벽에서 Python 허용
# 제어판 → Windows Defender 방화벽 → 앱 또는 기능 허용
# Python 찾아서 "개인" 및 "공용" 체크
```

---

## ✅ 배포 체크리스트

- [ ] Python 3.8+ 설치 확인
- [ ] NAS에서 프로젝트 폴더 복사
- [ ] 가상환경 생성 (`python -m venv venv`)
- [ ] 가상환경 활성화 (`.\venv\Scripts\activate`)
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] .env 파일 생성 및 API 키 입력
- [ ] 이메일 테스트 성공 (`python test_email.py`)
- [ ] 전체 실행 테스트 (`python main_unified.py`)
- [ ] 작업 스케줄러 등록 (매일 오전 9시)
- [ ] 로그 폴더 확인 (`logs\unified_automation.log`)

---

## 📞 문제 발생 시

**로그 확인:**
```powershell
# 최근 로그 보기
Get-Content logs\unified_automation.log -Tail 50

# 에러만 필터링
Get-Content logs\unified_automation.log | Select-String "ERROR"
```

**수동 실행으로 디버깅:**
```powershell
cd C:\Projects\hyscape_daily_automation
.\venv\Scripts\activate
python main_unified.py
```

---

## 🎉 완료!

이제 매일 오전 9시에 자동으로:
1. 📄 PDF 브리핑 요약
2. 🏛️ 정부지원사업 추천 3건
3. 📰 수소 뉴스 5건

이 이메일로 발송됩니다!

**수동 실행:**
```powershell
cd C:\Projects\hyscape_daily_automation
.\venv\Scripts\activate
python main_unified.py
```
