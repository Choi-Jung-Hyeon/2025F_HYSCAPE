# H2HUB 브리핑 자동화 - 빠른 시작 🚀

## 30초 안에 시작하기

### 1️⃣ 설치
```bash
chmod +x install.sh
./install.sh
```

### 2️⃣ 실행
```bash
# 기존 PDF 처리
./run_automation.sh

# 또는 웹에서 크롤링
./run_automation.sh --pages 3
```

### 3️⃣ 자동화 설정
```bash
# 크론탭 편집
crontab -e

# 매일 오전 9시 실행 추가
0 9 * * * /path/to/run_automation.sh >> /path/to/logs/cron.log 2>&1
```

---

## 📁 사용 방법

### PDF 폴더에 파일 넣기
```
../pdf/
├── 250925_일간_수소_이슈_브리핑.pdf
├── 251126_일간_수소_이슈_브리핑.pdf
└── ...
```

### 자동화 실행
```bash
./run_automation.sh
```

결과:
- ✅ PDF 분석 (Gemini AI)
- ✅ Notion 업로드
- ✅ `../pdf_archive/`로 이동
- ✅ 로그 저장 (`logs/`)

---

## 🛠️ 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--pages N` | 웹에서 N페이지 크롤링 | `--pages 3` |
| `--dry-run` | 테스트 실행 (실제 X) | `--dry-run` |
| `--no-backup` | 백업 생성 안 함 | `--no-backup` |
| `--verbose` | 상세 로그 | `--verbose` |
| `--help` | 도움말 | `--help` |

---

## 📊 디렉토리 구조

```
프로젝트/
├── h2hub_automation/         ← 코드
│   ├── run_automation.sh     ← 실행!
│   ├── main.py
│   ├── config.py
│   └── logs/                 ← 로그
│
├── pdf/                      ← 처리할 PDF 여기
└── pdf_archive/              ← 처리 완료 PDF
```

---

## ⚠️ 트러블슈팅

### Notion 연결 안 됨?
```bash
python main.py --test-notion
```

### PDF 인식 안 됨?
```bash
./run_automation.sh --dry-run  # 테스트
```

### 크론잡 안 됨?
```bash
tail -f logs/cron.log  # 로그 확인
```

---

## 📖 상세 가이드

더 자세한 내용은 **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** 참고

---

## ✅ 체크리스트

- [ ] `install.sh` 실행
- [ ] `config.py` API 키 확인
- [ ] Notion 테스트 성공
- [ ] 첫 실행 성공
- [ ] 크론잡 설정
- [ ] 로그 확인

**완료되면 모든 준비 끝!** 🎉