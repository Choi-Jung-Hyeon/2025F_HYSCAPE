#!/bin/bash
# H2HUB 브리핑 자동화 스크립트
# 사용법: ./run_automation.sh

set -e  # 오류 발생 시 중단

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}H2HUB 브리핑 자동화 시스템${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""

# 디렉토리 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PDF_DIR="$SCRIPT_DIR/../pdf"
ARCHIVE_DIR="$SCRIPT_DIR/../pdf_archive"

# 아카이브 디렉토리 생성
mkdir -p "$ARCHIVE_DIR"

# PDF 파일 개수 확인
PDF_COUNT=$(find "$PDF_DIR" -maxdepth 1 -name "*.pdf" -type f | wc -l)

if [ "$PDF_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  처리할 PDF 파일이 없습니다.${NC}"
    echo -e "${YELLOW}   $PDF_DIR 에 PDF 파일을 추가해주세요.${NC}"
    exit 0
fi

echo -e "${GREEN}📄 $PDF_COUNT개의 새 PDF 파일 발견${NC}"
echo ""

# Python 가상환경 활성화
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo -e "${GREEN}🔧 가상환경 활성화...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# 메인 스크립트 실행
echo -e "${GREEN}🚀 분석 및 업로드 시작...${NC}"
echo ""

python "$SCRIPT_DIR/main.py" --existing-pdfs "$PDF_DIR"

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 처리 완료!${NC}"
    echo ""
    
    # 처리된 PDF를 아카이브로 이동
    echo -e "${GREEN}📦 처리된 PDF 파일을 아카이브로 이동...${NC}"
    
    for pdf_file in "$PDF_DIR"/*.pdf; do
        if [ -f "$pdf_file" ]; then
            filename=$(basename "$pdf_file")
            mv "$pdf_file" "$ARCHIVE_DIR/"
            echo -e "   ✓ $filename → pdf_archive/"
        fi
    done
    
    echo ""
    echo -e "${GREEN}======================================================================${NC}"
    echo -e "${GREEN}🎉 모든 작업 완료!${NC}"
    echo -e "${GREEN}   - 처리된 파일: $PDF_COUNT개${NC}"
    echo -e "${GREEN}   - 아카이브 위치: $ARCHIVE_DIR${NC}"
    echo -e "${GREEN}======================================================================${NC}"
    
else
    echo ""
    echo -e "${RED}❌ 오류 발생! PDF 파일은 이동하지 않았습니다.${NC}"
    exit 1
fi