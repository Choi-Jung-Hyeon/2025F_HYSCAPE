#!/bin/bash
# 빠른 시작 스크립트
# 이 스크립트를 실행하여 프로젝트를 빠르게 시작할 수 있습니다.

echo "=========================================="
echo "한국수소연합 브리핑 자동화 시스템 설치"
echo "=========================================="
echo ""

# 1. 가상환경 생성
echo "1. 가상환경 생성 중..."
python3 -m venv venv

# 2. 가상환경 활성화
echo "2. 가상환경 활성화..."
source venv/bin/activate

# 3. 패키지 설치
echo "3. 필요한 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. config.py 파일을 열어 API 키를 입력하세요"
echo "   - OPENAI_API_KEY"
echo "   - NOTION_API_KEY"
echo "   - NOTION_DATABASE_ID"
echo ""
echo "2. Notion 데이터베이스 설정:"
echo "   - 제목 (Title)"
echo "   - 날짜 (Date)"
echo "   - 요약 (Rich Text)"
echo "   - 링크 (URL)"
echo "   - 기술전망 (Select: 🟢 긍정적, 🔴 부정적, 🟡 중립)"
echo ""
echo "3. 연결 테스트:"
echo "   python main.py --test-notion"
echo ""
echo "4. 실행:"
echo "   python main.py"
echo ""
