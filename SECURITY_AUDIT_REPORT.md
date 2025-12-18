# 개인정보 및 보안 감사 상세 보고서

**감사 일시**: 2025-12-18
**감사 범위**: Git 저장소 전체 (236개 파일, 93개 커밋)
**감사자**: Claude Code

---

## 🚨 심각도 높음 (Critical)

### 1. Gmail 앱 비밀번호 노출

**노출된 비밀번호**: `REDACTED_GMAIL_PASSWORD`

**위치**:
- ✅ `hyscape_daily_automation/README_operation_guide.md:72` (수정 완료)
- 🔴 `project_archive/version1/ArticleScrab.ipynb` (git 추적 중)
- 🔴 `project_archive/version1/ArticleScrab_v2.ipynb` (git 추적 중)
- 🔴 `project_archive/version1/sendingmail.py` (git 추적 중)

**연관 이메일**: `DEVELOPER_EMAIL`

**위험도**:
- 외부인이 이 비밀번호로 Gmail 계정에 접근 가능
- 이메일 발송, 읽기, 삭제 등 모든 작업 가능
- 회사 기밀 정보 유출 위험

**필요 조치**:
1. ⚡ **즉시**: Gmail 앱 비밀번호 재발급 (필수)
2. 🔴 Git에서 해당 파일들 제거 또는 히스토리 정리

---

### 2. Google Gemini API 키 노출

**노출된 API 키**:
1. `REDACTED_API_KEY_1` (version4)
2. `REDACTED_API_KEY_2` (version1)

**위치**:
- 🔴 Git History: 커밋 `02ec3b5` - `version4/config.py` (삭제됨, 히스토리 남음)
- 🔴 `project_archive/version1/ArticleScrab.ipynb` (git 추적 중)
- 🔴 `project_archive/version1/ArticleScrab_v2.ipynb` (git 추적 중)

**위험도**:
- 무단으로 Gemini API 사용 가능
- 과도한 API 호출로 비용 청구 가능
- 일일 할당량 소진으로 서비스 중단 가능

**필요 조치**:
1. ⚡ **즉시**: Google API 키 재발급 또는 제한 설정 (필수)
2. 🔴 Git History에서 완전 제거

---

### 3. 개인 이메일 주소 노출

**노출된 이메일 주소**:

#### 회사 이메일:
- `ymkim@hyscape.co.kr`
- `h2lee@hyscape.co.kr`

#### 개인 이메일:
- `fourmi103@g.skku.edu` (개발자 - 학교 이메일)
- `DEVELOPER_EMAIL` (개발자 - 개인 Gmail)
- `eguitar97@naver.com`

**위치**:
- `hyscape_daily_automation/config_production.py:27-32` (수신자 목록)
- `hyscape_daily_automation/README_operation_guide.md:218-220` (연락처)
- 다수의 archived 파일들

**위험도**: 중간
- 스팸/피싱 메일 대상이 될 수 있음
- 개인정보 유출 우려

**권장 조치**:
- 수신자 목록을 환경 변수로 이동 (선택사항)
- 또는 현재 상태 유지 (회사 이메일은 공개되어도 큰 문제 없음)

---

## 📊 감사 통계

### Git 저장소 정보
- **총 추적 파일**: 236개
- **총 커밋 수**: 93개
- **문제 발견 파일**: 4개 (직접 노출) + 다수 (git history)

### 민감 정보 발견 현황

| 유형 | 발견 건수 | 상태 |
|------|----------|------|
| Gmail 앱 비밀번호 | 4곳 | 1곳 수정, 3곳 git 추적 중 |
| Google API 키 | 3곳 | git history 포함 |
| 개인 이메일 주소 | 15+ | 대부분 정상 사용 |
| Notion API 토큰 | 0 | 환경 변수 사용 (안전) |
| 전화번호 | 0 | 발견 안됨 |

---

## ✅ 안전한 구성

### 현재 프로덕션 시스템 (hyscape_daily_automation)
- ✅ `.env` 파일 사용으로 민감 정보 분리
- ✅ `config_production.py`는 환경 변수만 참조
- ✅ `notion_config_production.py`는 환경 변수만 참조
- ✅ `.env`는 git에 추적되지 않음
- ✅ `.env.template` 제공으로 안전한 설정 가이드

### 기타 버전들
- ✅ `notion_version3/config_template.py`: placeholder만 사용
- ✅ `government_version2/config.yaml`: API 키 없음 (크롤링만)
- ✅ `mail_version9`: 별도 config 없음 (통합됨)

---

## 🛠️ 수행된 보안 강화 조치

### 1. .gitignore 업데이트 (완료)
```gitignore
# 환경 변수 및 민감한 정보
.env
.env.*
!.env.template
!.env.example

# 로그 파일
*.log
logs/

# 데이터 파일
*.pdf
pdf/

# 민감한 정보가 포함된 아카이브 파일
project_archive/version*/ArticleScrab*.ipynb
project_archive/version*/sendingmail.py
```

### 2. README 수정 (완료)
- Gmail 비밀번호 평문 제거
- 안전한 환경 변수 참조 방법으로 변경

### 3. 보안 문서 생성 (완료)
- `SECURITY_NOTICE.md`: 상세한 보안 가이드
- `SECURITY_AUDIT_REPORT.md`: 이 감사 보고서

---

## ⚡ 즉시 필요한 조치

### 우선순위 1: 크리덴셜 재발급 (필수 - 24시간 내)

#### A. Gmail 앱 비밀번호
```bash
1. https://myaccount.google.com/apppasswords 접속
   (계정: DEVELOPER_EMAIL)
2. "Hyscape Automation" 앱 비밀번호 삭제
3. 새 앱 비밀번호 생성
4. 업데이트:
   hyscape_daily_automation/.env
   SENDER_PASSWORD=새로운16자리비밀번호
```

#### B. Google Gemini API 키
```bash
1. https://aistudio.google.com/app/apikey 접속
2. 노출된 키 2개 삭제:
   - REDACTED_API_KEY_1
   - REDACTED_API_KEY_2
3. 새 API 키 생성
4. 업데이트:
   hyscape_daily_automation/.env
   GOOGLE_API_KEY=새로운키
```

### 우선순위 2: Git 저장소 공개 여부 확인 (즉시)

```bash
# 원격 저장소 확인
git remote -v

# GitHub에서 Public/Private 확인
# GitHub 웹사이트 → Settings → Danger Zone
```

**만약 Public 저장소라면**:
- ⚡ **즉시 Private으로 변경** (필수)
- 🔴 Git History 정리 필수
- ⚡ 모든 API 키/비밀번호 즉시 재발급

**만약 Private 저장소라면**:
- ⚡ API 키/비밀번호 재발급 권장
- 🟡 Git History 정리 선택사항 (하지만 강력 권장)

### 우선순위 3: 민감한 파일 Git에서 제거 (권장 - 1주일 내)

#### 옵션 A: Git tracking만 중지 (간단하지만 히스토리 남음)
```bash
# 파일은 유지하되 더 이상 추적 안 함
git rm --cached project_archive/version1/ArticleScrab.ipynb
git rm --cached project_archive/version1/ArticleScrab_v2.ipynb
git rm --cached project_archive/version1/sendingmail.py

git commit -m "security: Stop tracking files with hardcoded credentials"
```

**주의**: 이 방법은 과거 커밋에는 여전히 남아있음

#### 옵션 B: Git History에서 완전 제거 (권장)
```bash
# git-filter-repo 사용 (권장)
pip install git-filter-repo

# 특정 파일 히스토리에서 완전 삭제
git filter-repo --invert-paths \
  --path project_archive/version1/ArticleScrab.ipynb \
  --path project_archive/version1/ArticleScrab_v2.ipynb \
  --path project_archive/version1/sendingmail.py

# 또는 민감한 문자열 치환
git filter-repo --replace-text <(cat <<EOF
REDACTED_GMAIL_PASSWORD==>REDACTED_PASSWORD
REDACTED_API_KEY_1==>REDACTED_API_KEY
REDACTED_API_KEY_2==>REDACTED_API_KEY
EOF
)

# Force push (주의: 팀원들과 협의 필요)
git push origin --force --all
```

**중요**:
- 이 작업 전에 팀원들과 협의 필요
- 모든 팀원이 저장소를 새로 clone해야 함
- 백업 필수

---

## 📋 향후 보안 관리 계획

### 코드 커밋 전 체크리스트
```bash
# 커밋 전 민감 정보 자동 검사
git secrets --install
git secrets --add 'invg [a-z]{4} [a-z]{4} [a-z]{4}'  # Gmail password
git secrets --add 'AIza[0-9A-Za-z\-_]{35}'  # Google API Key
git secrets --add 'secret_[a-zA-Z0-9]{43}'  # Notion token

# 전체 히스토리 스캔
git secrets --scan-history
```

### 주기적 보안 점검 (분기별)
- [ ] API 키 순환 (3개월마다)
- [ ] 접근 권한 검토
- [ ] 로그 파일 정리
- [ ] 사용하지 않는 크리덴셜 삭제

### 자동화 도구 설치 (권장)
```bash
# 1. git-secrets (AWS 오픈소스)
brew install git-secrets  # macOS
# 또는
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets && make install

# 2. truffleHog (깃 히스토리 스캔)
pip install truffleHog

# 사용법
trufflehog --regex --entropy=False .
```

---

## 🎯 권장 아키텍처 (Best Practice)

### 개발 환경
```
.env                    # 개발자 개인 크리덴셜 (gitignore)
.env.template           # 템플릿 (git 추적)
config_production.py    # 환경변수만 참조 (git 추적 가능)
```

### 프로덕션 배포
```
1. .env.template 복사 → .env
2. .env 파일에 실제 크리덴셜 입력
3. 절대 .env를 git에 추가하지 않음
4. 서버별로 다른 .env 사용
```

---

## 📞 추가 지원

### 문의처
- **개발자**: fourmi103@g.skku.edu
- **회사**: ymkim@hyscape.co.kr

### 참고 자료
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [git-secrets](https://github.com/awslabs/git-secrets)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## 📝 체크리스트

### 즉시 (24시간 내)
- [ ] Gmail 앱 비밀번호 재발급
- [ ] Google Gemini API 키 2개 재발급
- [ ] Git 저장소 공개 여부 확인
- [ ] Public이면 Private으로 변경

### 단기 (1주일 내)
- [ ] 민감한 파일 Git에서 제거 결정
- [ ] Git History 정리 (선택)
- [ ] 팀원들에게 보안 가이드 공유

### 중기 (1개월 내)
- [ ] git-secrets 설치 및 설정
- [ ] 보안 점검 프로세스 문서화
- [ ] Notion API 토큰 순환 계획

### 장기 (분기별)
- [ ] 정기 보안 감사
- [ ] 크리덴셜 순환
- [ ] 팀 보안 교육

---

**감사 완료**: 2025-12-18
**다음 감사 예정**: 2025-03-18 (3개월 후)
