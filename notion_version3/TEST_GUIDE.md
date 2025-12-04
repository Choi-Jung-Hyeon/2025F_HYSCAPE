# H2HUB 브리핑 자동화 시스템 - 테스트 가이드 🧪

## 준비사항

### 1. 모든 파일 다운로드
다음 파일들을 같은 폴더에 다운로드하세요:
- `main.py`
- `article_collector.py`
- `article_analyzer.py`
- `notion_uploader.py`
- `config.py`
- `check_notion_properties.py`
- `requirements.txt`

### 2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. Notion 설정 (중요!)

#### 3-1. Notion Integration 생성
1. https://www.notion.so/my-integrations 접속
2. "New integration" 클릭
3. 이름: "H2HUB 브리핑 자동화"
4. **Internal Integration Token 복사** → `config.py`의 `NOTION_API_KEY`에 붙여넣기

#### 3-2. Notion 데이터베이스 생성
1. Notion에서 새 데이터베이스 페이지 생성
2. 다음 속성(컬럼) 추가:

| 속성명 | 타입 | 설명 |
|--------|------|------|
| 제목 | Title | 기본 제목 |
| date | Date | 브리핑 날짜 |
| url | URL | 원문 링크 |
| 요약 | Text | 요약 내용 |
| 기술전망 | Select | 🟢 긍정적, 🔴 부정적, 🟡 중립 |
| category | Select | 🏛️ 기관, 📜 정책, 🏙️ 지자체, 🏭 산업계, 🔬 연구계, 🌏 해외 |
| 키워드 | Multi-select | 키워드 태그 |

3. 데이터베이스 페이지 우측 상단 "..." → "Connections" → Integration 연결
4. URL에서 데이터베이스 ID 복사 (32자리 문자열) → `config.py`의 `NOTION_DATABASE_ID`에 붙여넣기

**URL 예시:**
```
https://notion.so/workspace/[DATABASE_ID]?v=...
                          ↑ 이 부분
```

### 4. Google Gemini API 키 (이미 설정되어 있음)
현재 `config.py`에 API 키가 포함되어 있습니다.
- 만료되었다면 https://aistudio.google.com/apikey 에서 새로 발급받으세요.

---

## 테스트 시나리오

### ✅ 1단계: Notion 연결 테스트
```bash
python check_notion_properties.py
```

**기대 결과:**
```
✅ 제목 (title) - 타입: title
✅ date (date) - 타입: date
✅ 요약 (rich_text) - 타입: rich_text
✅ url (url) - 타입: url
✅ 기술전망 (select) - 타입: select
✅ category (select) - 타입: select
✅ 키워드 (multi_select) - 타입: multi_select
```

**오류 발생 시:**
- `403 Forbidden` → Integration을 데이터베이스에 연결 안 함
- `404 Not Found` → DATABASE_ID가 잘못됨
- 속성 없음 오류 → 데이터베이스 속성명 확인

---

### ✅ 2단계: 웹 크롤링 테스트 (업로드 제외)
```bash
python main.py --pages 1 --no-upload
```

**기대 결과:**
```
✅ 모든 컴포넌트 초기화 완료
📄 1페이지 수집 중...
✅ 수집 완료: N개
✅ 텍스트 추출 완료 (XXXX 자)
✅ AI 분석 완료
  📝 요약: ...
  😊 전망: 긍정적
  🏢 카테고리: 산업계
  🏷️ 키워드: [수소, 수전해, ...]
```

---

### ✅ 3단계: 전체 워크플로우 (Notion 업로드 포함)
```bash
python main.py --pages 1
```

**기대 결과:**
```
✅ 분석 완료: N개
✅ Notion 업로드 시작...
✅ 업로드 성공: [제목1]
✅ 업로드 성공: [제목2]
✅ 총 N개 업로드 완료
```

Notion 데이터베이스에서 새 페이지가 생성되었는지 확인하세요!

---

### ✅ 4단계: 기존 PDF 파일 분석
로컬에 PDF 파일이 있다면:
```bash
python main.py --existing-pdfs /path/to/pdfs
```

---

## 자주 발생하는 오류

### 1. `403 Forbidden` (Notion)
**원인:** Integration이 데이터베이스에 연결되지 않음  
**해결:** 
1. Notion 데이터베이스 페이지 열기
2. 우측 상단 "..." → "Connections"
3. Integration 선택

### 2. `속성이 없습니다` (Notion)
**원인:** 데이터베이스 속성명이 `config.py`와 다름  
**해결:** 
- `check_notion_properties.py` 실행해서 실제 속성명 확인
- `config.py`의 `NOTION_PROPERTIES` 수정

### 3. `텍스트가 너무 짧습니다`
**원인:** PDF가 손상되었거나 텍스트 추출 실패  
**해결:** 
- 정상적인 PDF 파일인지 확인
- 다른 PDF 뷰어로 열어서 텍스트 복사가 되는지 확인

### 4. `AI 분석 실패`
**원인:** Gemini API 키 만료 또는 할당량 초과  
**해결:**
- https://aistudio.google.com/apikey 에서 새 키 발급
- 무료 할당량: 분당 15 requests, 일일 1500 requests

---

## 성공 기준 ✅

1. ✅ `check_notion_properties.py`에서 모든 속성 확인됨
2. ✅ `main.py --pages 1 --no-upload`에서 PDF 분석 성공
3. ✅ `main.py --pages 1`에서 Notion 업로드 성공
4. ✅ Notion 데이터베이스에 새 페이지 생성됨
5. ✅ 모든 필드(요약, 전망, 카테고리, 키워드)가 정확히 채워짐

---

## 프로덕션 실행 (정기 자동화)

### Windows (작업 스케줄러)
1. 작업 스케줄러 열기
2. "기본 작업 만들기"
3. 트리거: 매일 오전 9시
4. 작업: `python C:\path\to\main.py --pages 3`

### Linux/Mac (Cron)
```bash
crontab -e

# 매일 오전 9시 실행
0 9 * * * cd /path/to/project && python3 main.py --pages 3 >> logs/cron.log 2>&1
```

---

## 추가 옵션

```bash
# 여러 페이지 수집
python main.py --pages 5

# 기존 PDF만 분석
python main.py --existing-pdfs ./pdfs

# Notion 업로드 제외 (분석만)
python main.py --pages 1 --no-upload

# Notion 연결 테스트
python main.py --test-notion
```

---

## 문의사항
- Notion 설정 문제: 데이터베이스 속성명과 Integration 연결 확인
- PDF 분석 문제: 정상적인 PDF 파일인지 확인
- API 오류: 키 유효성과 할당량 확인

**모든 테스트를 통과하면 시스템이 정상 작동하는 것입니다!** 🎉