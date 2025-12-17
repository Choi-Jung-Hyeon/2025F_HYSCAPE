# 회사 컴퓨터 배포 체크리스트

## 📝 1단계: 회사 컴퓨터 환경 확인

### A. 운영 체제
- [ ] Windows 버전: ____________ (예: Windows 10/11)
- [ ] WSL 설치 여부: [ ] 있음 / [ ] 없음
- [ ] WSL 배포판: ____________ (예: Ubuntu 20.04)

### B. 소프트웨어 설치 확인
- [ ] Git 설치 여부
  - 확인 방법: `git --version`
  - 다운로드: https://git-scm.com/downloads

- [ ] Python 3.8+ 설치 여부
  - 확인 방법: `python --version` 또는 `python3 --version`
  - 다운로드: https://www.python.org/downloads/
  - **중요:** Python 경로를 메모하세요!
    - Windows 예시: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
    - WSL 예시: `/usr/bin/python3`

### C. 프로젝트 경로 결정
- [ ] 프로젝트를 저장할 폴더 경로 결정
  - Windows 예시: `C:\Projects\2025F_HYSCAPE`
  - WSL 예시: `/home/username/2025F_HYSCAPE`
  - **선택한 경로:** ____________________________

---

## 🔧 2단계: 회사 컴퓨터에서 할 작업

### Step 1: Git Clone
```bash
# WSL 또는 Git Bash에서
cd <프로젝트를 저장할 폴더>
git clone https://github.com/Choi-Jung-Hyeon/2025F_HYSCAPE.git
cd 2025F_HYSCAPE
```

### Step 2: Python 가상환경 생성
```bash
# WSL/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: 의존성 설치
```bash
cd hyscape_daily_automation
pip install -r requirements.txt
```

### Step 4: .env 파일 복사 ⚠️ 중요!
```bash
# .env 파일은 Git에 없으므로 수동으로 생성 필요
cp .env.template .env
# 그 다음 .env 파일을 편집하여 실제 API 키 입력
```

**방법 1: 개인 컴퓨터에서 직접 복사**
```bash
# 개인 컴퓨터에서 .env 파일 내용을 USB나 보안 채널로 전송
cat /home/fourmi103/2025F_HYSCAPE/hyscape_daily_automation/.env
```

**방법 2: 회사 컴퓨터에서 직접 입력**
- `.env.template`을 `.env`로 복사 후 수동으로 API 키 입력
- 필요한 값:
  - `GOOGLE_API_KEY`: Gemini API 키
  - `SENDER_EMAIL`: Gmail 주소
  - `SENDER_PASSWORD`: Gmail 앱 비밀번호
  - `NOTION_API_TOKEN`: Notion API 토큰
  - `NOTION_DATABASE_ID`: Notion DB ID

### Step 5: 실행 테스트
```bash
# WSL/Linux
./run_automation.sh

# Windows (PowerShell에서)
python main_unified.py
```

---

## ⚙️ 3단계: 자동 실행 설정 (선택사항)

### Windows 작업 스케줄러 설정
1. 작업 스케줄러 열기 (`taskschd.msc`)
2. 작업 만들기
3. 트리거: 매일 오전 9시
4. 동작: `RUN_autobriefing.bat` 실행

### Linux/WSL Cron 설정
```bash
crontab -e

# 매일 오전 9시 실행
0 9 * * * /home/username/2025F_HYSCAPE/hyscape_daily_automation/run_automation.sh >> /home/username/2025F_HYSCAPE/hyscape_daily_automation/logs/cron.log 2>&1
```

---

## 🔐 보안 주의사항

### .env 파일 관리
- [ ] .env 파일은 **절대** Git에 커밋하지 않기
- [ ] 전송 시 보안 채널 사용 (회사 VPN, 암호화된 USB 등)
- [ ] 복사 후 개인 컴퓨터의 임시 파일 삭제
- [ ] 회사 컴퓨터에서 .env 파일 권한 설정
  ```bash
  chmod 600 .env  # 소유자만 읽기/쓰기 가능
  ```

---

## 🆘 트러블슈팅

### 문제 1: Python을 찾을 수 없음
```bash
# Python 경로 확인
which python3  # WSL/Linux
where python   # Windows
```

### 문제 2: 의존성 설치 실패
```bash
# pip 업그레이드
pip install --upgrade pip
# 의존성 재설치
pip install -r requirements.txt
```

### 문제 3: .env 파일 로딩 안 됨
```bash
# .env 파일 위치 확인
ls -la hyscape_daily_automation/.env

# 테스트
python -c "
import sys
sys.path.insert(0, 'hyscape_daily_automation')
import config_production as config
print('API Key loaded:', 'Yes' if config.GOOGLE_API_KEY else 'No')
"
```

### 문제 4: WSL에서 배치 파일 실행 안 됨
- Windows에서 `RUN_autobriefing.bat` 실행 (WSL 내부가 아닌 Windows 탐색기에서)
- 또는 WSL에서 `./run_automation.sh` 실행

---

## ✅ 배포 완료 확인

- [ ] Git clone 완료
- [ ] 가상환경 생성 및 활성화 완료
- [ ] 의존성 설치 완료 (`pip list` 확인)
- [ ] .env 파일 복사 및 설정 완료
- [ ] 실행 테스트 성공 (최소 1개 모듈 성공)
- [ ] 로그 파일 생성 확인 (`logs/unified_automation.log`)
- [ ] (선택) 자동 실행 스케줄 설정 완료

---

## 📞 문제 발생 시

1. 로그 확인: `cat logs/unified_automation.log`
2. 에러 로그 확인: `cat logs/error.log`
3. 수동 실행으로 디버깅:
   ```bash
   cd hyscape_daily_automation
   python main_unified.py
   ```

---

## 📌 중요 파일 목록

**반드시 복사해야 할 파일:**
- `.env` (수동 생성/복사 필요)

**자동으로 Git에서 가져올 파일:**
- `main_unified.py`
- `config_production.py`
- `notion_config_production.py`
- `requirements.txt`
- `run_automation.sh`
- `RUN_autobriefing.bat`
- 모든 모듈 및 의존성

**생성될 파일:**
- `logs/unified_automation.log`
- `logs/error.log`
- `__pycache__/` (자동 생성)
