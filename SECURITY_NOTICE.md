# 보안 경고 및 조치 사항

**생성일**: 2025-12-18

## ⚠️ 발견된 보안 문제

Git 저장소 검토 결과, 다음의 민감한 정보가 노출되어 있었습니다:

### 1. Gmail 앱 비밀번호 노출 (수정 완료)
- **위치**: `README_operation_guide.md` (현재 수정됨)
- **노출된 정보**: Gmail 앱 비밀번호가 평문으로 기록
- **영향**: 이메일 계정 무단 접근 가능

### 2. Google API 키 노출 (Git History)
- **위치**: Git 커밋 히스토리 (`0df4d7c` - `version4/config.py`)
- **노출된 키**: `REDACTED_API_KEY_1`
- **영향**: Gemini API 무단 사용, 과금 발생 가능

### 3. 개인 이메일 주소
- **위치**: `config_production.py`
- **내용**: 수신자 목록에 개인 이메일 주소 포함

## 🚨 즉시 필요한 조치

### 우선순위 1: API 키 및 비밀번호 재발급 (필수)

#### Gmail 앱 비밀번호 재발급
1. Google 계정 로그인 (ymkim@hyscape.co.kr)
2. https://myaccount.google.com/apppasswords 접속
3. 기존 "Hyscape Automation" 앱 비밀번호 삭제
4. 새 앱 비밀번호 생성
5. `.env` 파일의 `SENDER_PASSWORD` 업데이트

#### Google Gemini API 키 재발급
1. https://aistudio.google.com/app/apikey 접속
2. 노출된 API 키 삭제 또는 제한 설정
3. 새 API 키 생성
4. `.env` 파일의 `GOOGLE_API_KEY` 업데이트

#### Notion API 토큰 확인
1. https://www.notion.so/my-integrations 접속
2. 현재 토큰이 노출되지 않았는지 확인
3. 의심되면 토큰 재발급
4. `.env` 파일 업데이트

### 우선순위 2: Git History 정리 (권장)

만약 이 저장소가 **Public** 또는 **외부 공유**되는 경우, Git History에서 민감한 정보를 완전히 제거해야 합니다.

#### Option A: BFG Repo-Cleaner (간단)
```bash
# BFG 다운로드
# https://rtyley.github.io/bfg-repo-cleaner/

# 민감한 정보가 포함된 파일 삭제
java -jar bfg.jar --delete-files config.py
java -jar bfg.jar --delete-files '*.pyc'

# Git history 정리
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

#### Option B: git filter-repo (정밀)
```bash
# git-filter-repo 설치
pip install git-filter-repo

# 특정 파일 히스토리에서 완전 제거
git filter-repo --path version4/config.py --invert-paths

# 또는 특정 문자열 치환
git filter-repo --replace-text <(echo "REDACTED_API_KEY_1==>REDACTED")
```

**⚠️ 주의**: 이 작업은 Git 히스토리를 변경하므로:
- 팀원들과 협의 필요
- 모든 팀원이 저장소를 새로 clone해야 함
- Force push 필요: `git push origin --force --all`

### 우선순위 3: 현재 저장소 상태 확인

#### 저장소가 Public인 경우
- **즉시 Private으로 변경**
- 위의 모든 API 키/비밀번호 재발급 필수
- Git History 정리 필수

#### 저장소가 Private인 경우
- API 키/비밀번호 재발급 권장
- Git History 정리 선택적 (하지만 권장)

## ✅ 완료된 조치

### 1. .gitignore 강화 (완료)
다음 항목들이 추가되었습니다:
- `.env` 및 모든 환경 변수 파일
- 로그 파일 (`*.log`, `logs/`)
- PDF 및 데이터 파일
- 백업 디렉토리

### 2. README에서 비밀번호 제거 (완료)
- 평문 비밀번호 삭제
- 안전한 참조 방법으로 대체

## 📋 향후 보안 체크리스트

### 코드 커밋 전
- [ ] `.env` 파일이 절대 커밋되지 않도록 확인
- [ ] 하드코딩된 API 키, 비밀번호가 없는지 확인
- [ ] `git status`로 커밋할 파일 재확인
- [ ] 개인정보(이메일, 전화번호 등) 포함 여부 확인

### 주기적 점검
- [ ] 분기별 Git 저장소 스캔 (git-secrets, truffleHog 등)
- [ ] API 키 순환 (3-6개월마다)
- [ ] 접근 권한 검토

### 도구 활용
```bash
# git-secrets 설치 및 설정
git secrets --install
git secrets --register-aws
git secrets --add 'AIza[0-9A-Za-z\-_]{35}'  # Google API Key pattern
git secrets --add '[a-z]{16}'  # Gmail app password pattern

# 히스토리 전체 스캔
git secrets --scan-history
```

## 📞 문의

보안 관련 문제 발견 시:
- **개발자**: fourmi103@g.skku.edu
- **회사 연락처**: ymkim@hyscape.co.kr

## 참고 자료

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [git-secrets](https://github.com/awslabs/git-secrets)
