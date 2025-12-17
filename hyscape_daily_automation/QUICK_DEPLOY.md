# 빠른 배포 가이드 (5분 완성)

## 📦 회사 컴퓨터에 가져갈 정보

### 1. 현재 .env 파일 내용 (보안 주의!)
```bash
# 개인 컴퓨터에서 실행 - 이 내용을 안전하게 복사하세요
cat /home/fourmi103/2025F_HYSCAPE/hyscape_daily_automation/.env
```

**출력 예시:**
```
GOOGLE_API_KEY=your_actual_google_api_key_here
GEMINI_MODEL=gemini-2.0-flash
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password_here
NOTION_API_TOKEN=your_actual_notion_token_here
NOTION_DATABASE_ID=your_actual_database_id_here
```

⚠️ **이 내용을 안전한 방법으로 회사 컴퓨터로 전송하세요:**
- 방법 1: 회사 보안 채널 (Teams, 사내 메신저 등)
- 방법 2: 암호화된 USB
- 방법 3: 회사 클라우드 스토리지 (OneDrive, 사내 NAS 등)

---

## 🚀 회사 컴퓨터에서 실행할 명령어 (순서대로)

### Step 1: Git Clone (30초)
```bash
# 프로젝트 폴더로 이동 (원하는 위치로 변경 가능)
cd ~
# 또는 Windows: cd C:\Projects

# 프로젝트 다운로드
git clone https://github.com/Choi-Jung-Hyeon/2025F_HYSCAPE.git
cd 2025F_HYSCAPE
```

### Step 2: Python 가상환경 생성 (1분)
```bash
# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # WSL/Linux
# 또는
.\venv\Scripts\activate   # Windows PowerShell
```

### Step 3: 의존성 설치 (2분)
```bash
cd hyscape_daily_automation
pip install -r requirements.txt
```

### Step 4: .env 파일 생성 (1분)
```bash
# 템플릿 복사
cp .env.template .env

# 에디터로 .env 파일 열기
nano .env  # 또는 vi, code, notepad 등

# 위에서 복사한 내용을 붙여넣기
# Ctrl+O (저장), Ctrl+X (종료)
```

### Step 5: 테스트 실행 (30초)
```bash
# 실행 권한 부여 (Linux/WSL만)
chmod +x run_automation.sh

# 실행
./run_automation.sh
```

---

## ✅ 성공 확인

다음과 같은 출력이 나오면 성공:
```
============================================================
⚡ Hyscape Unified Daily Automation System
============================================================

[2025-12-17 09:00:00] Starting automation...

[1/3] News Briefing Email...
[2/3] Government Support Recommendations...
[3/3] Notion Archive Upload...

============================================================
📊 Automation Summary
============================================================
News Briefing:    ✅ / ⚠️ (API quota 문제는 정상)
Gov Support:      ✅
Notion Archive:   ✅
============================================================
```

---

## 🎯 일일 자동 실행 설정 (선택사항)

### Windows 작업 스케줄러
```powershell
# 관리자 권한으로 PowerShell 실행
schtasks /create /tn "Hyscape Daily Automation" /tr "C:\Projects\2025F_HYSCAPE\hyscape_daily_automation\RUN_autobriefing.bat" /sc daily /st 09:00
```

### Linux/WSL Cron
```bash
crontab -e

# 아래 라인 추가 (매일 오전 9시 실행)
0 9 * * * ~/2025F_HYSCAPE/hyscape_daily_automation/run_automation.sh >> ~/2025F_HYSCAPE/hyscape_daily_automation/logs/cron.log 2>&1
```

---

## 📞 문제 해결

### Python이 없다고 나오면:
```bash
# Python 설치 확인
python3 --version
python --version

# 없으면 설치
# Windows: https://www.python.org/downloads/
# Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv
```

### Git이 없다고 나오면:
```bash
# Git 설치
# Windows: https://git-scm.com/downloads
# Ubuntu/Debian: sudo apt install git
```

### .env 파일이 안 불러와진다면:
```bash
# 파일 확인
ls -la .env

# 파일 내용 확인
cat .env

# 권한 확인
chmod 600 .env
```

---

## 🎉 완료!

이제 회사 컴퓨터에서 매일 오전 9시에 자동으로:
1. 수소 뉴스 수집 및 이메일 발송 📧
2. 정부지원사업 추천 🏛️
3. Notion 데이터베이스 업데이트 📝

가 자동으로 실행됩니다!

---

## 📌 참고

- 전체 문서: `DEPLOYMENT_CHECKLIST.md`
- 운영 가이드: `README_operation_guide.md`
- 로그 위치: `logs/unified_automation.log`
