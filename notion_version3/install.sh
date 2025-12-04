#!/bin/bash
# ============================================================================
# H2HUB 자동화 시스템 설치 스크립트
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}H2HUB 브리핑 자동화 시스템 설치${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""

# 현재 디렉토리
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 필수 패키지 확인
echo -e "${GREEN}1. Python 환경 확인...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3가 설치되어 있지 않습니다.${NC}"
    echo "설치: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
echo "   ✅ Python3 $(python3 --version)"

# 2. 가상환경 생성
echo ""
echo -e "${GREEN}2. 가상환경 생성...${NC}"
if [ ! -d "$INSTALL_DIR/venv" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
    echo "   ✅ 가상환경 생성 완료"
else
    echo "   ℹ️  가상환경이 이미 존재합니다"
fi

# 3. 의존성 설치
echo ""
echo -e "${GREEN}3. 의존성 설치...${NC}"
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"
echo "   ✅ 패키지 설치 완료"

# 4. 디렉토리 생성
echo ""
echo -e "${GREEN}4. 디렉토리 구조 생성...${NC}"
mkdir -p "$INSTALL_DIR/../pdf"
mkdir -p "$INSTALL_DIR/../pdf_archive"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/backups"
mkdir -p "$INSTALL_DIR/downloads"
echo "   ✅ 디렉토리 생성 완료"

# 5. 실행 권한 부여
echo ""
echo -e "${GREEN}5. 실행 권한 설정...${NC}"
chmod +x "$INSTALL_DIR/run_automation.sh"
echo "   ✅ 실행 권한 부여 완료"

# 6. 설정 파일 확인
echo ""
echo -e "${GREEN}6. 설정 파일 확인...${NC}"
if [ ! -f "$INSTALL_DIR/config.py" ]; then
    echo -e "${YELLOW}⚠️  config.py가 없습니다!${NC}"
    echo "   config_template.py를 config.py로 복사하고 API 키를 설정하세요."
    exit 1
fi
echo "   ✅ config.py 존재"

# 7. Notion 연결 테스트
echo ""
echo -e "${GREEN}7. Notion 연결 테스트...${NC}"
python "$INSTALL_DIR/main.py" --test-notion

# 8. 크론잡 설정 안내
echo ""
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}✅ 설치 완료!${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""
echo -e "${YELLOW}📝 크론잡 설정 방법:${NC}"
echo ""
echo "1. 크론탭 편집:"
echo "   crontab -e"
echo ""
echo "2. 다음 라인 추가 (매일 오전 9시 실행):"
echo "   0 9 * * * $INSTALL_DIR/run_automation.sh >> $INSTALL_DIR/logs/cron.log 2>&1"
echo ""
echo "3. 또는 매주 월요일 오전 9시:"
echo "   0 9 * * 1 $INSTALL_DIR/run_automation.sh >> $INSTALL_DIR/logs/cron.log 2>&1"
echo ""
echo -e "${YELLOW}📖 사용 예시:${NC}"
echo "   ./run_automation.sh              # 기존 PDF 처리"
echo "   ./run_automation.sh --pages 3    # 웹에서 3페이지 크롤링"
echo "   ./run_automation.sh --dry-run    # 테스트 실행"
echo ""
echo -e "${GREEN}======================================================================${NC}"