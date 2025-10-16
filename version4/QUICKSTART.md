# 🚀 빠른 시작 가이드 (v3.0)

## ⏱️ 5분 안에 시작하기

### Step 1: 라이브러리 설치 (1분)

```bash
# 가상환경 활성화 (이미 했다면 skip)
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r requirements.txt

# PyPDF2 확인 (오류 발생 시)
pip install PyPDF2
```

---

### Step 2: config.py 수정 (2분)

`config.py` 파일을 열고 **3개만** 수정:

```python
# 1. Gemini API 키
GOOGLE_API_KEY = "여기에_발급받은_API_키"

# 2. Gmail 정보
SENDER_EMAIL = "본인_Gmail@gmail.com"
SENDER_PASSWORD = "Gmail_앱_비밀번호"

# 3. 수신자 (선택사항 - 테스트는 본인 이메일로)
RECEIVER_EMAIL = [
    "본인_Gmail@gmail.com"  # 테스트용
]
```

**Gmail 앱 비밀번호가 없다면?**
1. https://myaccount.google.com/security
2. 2단계 인증 활성화
3. "앱 비밀번호" 생성 (16자리)

---

### Step 3: PDF 파일 준비 (1분) - 선택사항

```bash
# PDF 디렉토리 생성
mkdir pdf

# PDF 파일 복사 (있다면)
cp "250925_일간수소 이슈 브리핑.pdf" pdf/
```

**PDF가 없어도 괜찮습니다!** 시스템은 정상 작동합니다.

---

### Step 4: 실행! (1분)

```bash
python main.py
```

**예상 소요 시간**: 2~3분

---

## ✅ 체크리스트

실행 전에 확인하세요:

- [ ] `venv` 활성화됨
- [ ] `requirements.txt` 설치 완료
- [ ] `PyPDF2` 설치 확인
- [ ] `config.py`에 API 키 입력
- [ ] `config.py`에 Gmail 정보 입력
- [ ] Gmail 2단계 인증 + 앱 비밀번호 생성

---

## 🎯 첫 실행 시 확인사항

### 정상 작동 시 출력:

```
🚀 수소 뉴스 브리핑 시스템 v3.0 시작
⏰ 실행 시간: 2025-10-16 ...

[단계 0] PDF 브리핑 파일을 처리합니다...
[단계 1] 뉴스 소스에서 기사를 수집합니다...
[월간수소경제] RSS 피드를 수집합니다
  ✅ 20개의 기사를 찾았습니다.

... (생략) ...

[단계 3] 이메일을 발송합니다...
  ✅ 이메일 발송 완료!

✨ 모든 작업을 완료했습니다!
```

### 이메일 도착!

- 제목: `[수소 뉴스] 2025-10-16 일일 브리핑 (15개)`
- 내용: 요약된 기사 15개 + PDF 키워드

---

## ⚠️ 오류 발생 시

### 오류 1: ModuleNotFoundError

```bash
pip install PyPDF2
```

### 오류 2: Authentication failed

- Gmail 앱 비밀번호 재생성
- `config.py`에 정확히 입력 (공백 없이)

### 오류 3: API Error

- Gemini API 키 확인
- https://aistudio.google.com/app/apikey 에서 재발급

---

## 🔍 문제 해결 도구

### 뉴스 소스 진단

```bash
python source_diagnostics.py
```

어떤 소스가 작동하는지 확인하세요.

---

## 🎉 성공했나요?

축하합니다! 이제 매일 자동으로 실행하도록 설정하세요:

```bash
crontab -e

# 매일 오전 8시
0 8 * * * cd /path/to/version4 && /path/to/venv/bin/python main.py
```

---

## 📚 더 알아보기

- 📖 [README.md](README.md) - 전체 문서
- 🔧 [config.py](config.py) - 설정 파일
- 📊 [소스 진단](source_diagnostics.py) - 진단 도구

---

**도움이 필요하면 언제든 질문하세요!** 😊