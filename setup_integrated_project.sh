#!/bin/bash
# setup_integrated_project.sh
# mail_version9 + government_version2 통합 프로젝트 생성 스크립트

set -e  # 에러 발생 시 중단

echo "======================================"
echo "통합 프로젝트 생성 시작"
echo "======================================"

# 기본 경로
BASE_DIR=~/2025F_HYSCAPE
PROJECT_NAME=mail_gov_integrated
PROJECT_DIR=$BASE_DIR/$PROJECT_NAME

# 1. 프로젝트 디렉토리 생성
echo "[1/6] 프로젝트 디렉토리 생성..."
mkdir -p $PROJECT_DIR/{gov_support,pdf,logs}
cd $PROJECT_DIR

# 2. mail_version9 파일 복사
echo "[2/6] mail_version9 파일 복사..."
if [ -d "$BASE_DIR/mail_version9" ]; then
    cp -r $BASE_DIR/mail_version9/source_fetcher ./
    cp $BASE_DIR/mail_version9/content_scraper.py ./
    cp $BASE_DIR/mail_version9/summarizer.py ./
    cp $BASE_DIR/mail_version9/notifier.py ./
    cp $BASE_DIR/mail_version9/pdf_reader.py ./
    cp $BASE_DIR/mail_version9/requirements.txt ./
    echo "  ✓ mail_version9 복사 완료"
else
    echo "  ✗ mail_version9 디렉토리를 찾을 수 없습니다"
    exit 1
fi

# 3. government_version2 파일 복사
echo "[3/6] government_version2 파일 복사..."
if [ -d "$BASE_DIR/government_version2" ]; then
    # scrapers 디렉토리가 있으면 그곳에서 복사
    if [ -d "$BASE_DIR/government_version2/scrapers" ]; then
        cp $BASE_DIR/government_version2/scrapers/base_scraper.py ./gov_support/
        cp $BASE_DIR/government_version2/scrapers/k_startup_scraper.py ./gov_support/
        [ -f "$BASE_DIR/government_version2/scrapers/ntis_scraper.py" ] && \
            cp $BASE_DIR/government_version2/scrapers/ntis_scraper.py ./gov_support/
    else
        # 루트에서 복사
        cp $BASE_DIR/government_version2/base_scraper.py ./gov_support/ 2>/dev/null || true
        cp $BASE_DIR/government_version2/k_startup_scraper.py ./gov_support/ 2>/dev/null || true
        cp $BASE_DIR/government_version2/ntis_scraper.py ./gov_support/ 2>/dev/null || true
    fi
    
    # config.yaml 복사
    [ -f "$BASE_DIR/government_version2/config.yaml" ] && \
        cp $BASE_DIR/government_version2/config.yaml ./
    
    echo "  ✓ government_version2 복사 완료"
else
    echo "  ⚠ government_version2 디렉토리를 찾을 수 없습니다"
fi

# 4. 설정 파일 복사 (업로드된 파일 사용)
echo "[4/6] 설정 파일 확인..."
if [ -f "./config.py" ]; then
    echo "  ✓ config.py 발견"
else
    echo "  ⚠ config.py를 수동으로 추가해야 합니다"
fi

if [ -f "./config.yaml" ]; then
    echo "  ✓ config.yaml 발견"
else
    echo "  ⚠ config.yaml을 수동으로 추가해야 합니다"
fi

# 5. __init__.py 생성
echo "[5/6] __init__.py 생성..."
cat > ./gov_support/__init__.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""정부지원사업 크롤링 모듈"""

from .gov_support_manager import GovSupportManager

__all__ = ['GovSupportManager']
__version__ = '1.0.0'
EOF

echo "  ✓ __init__.py 생성 완료"

# 6. 프로젝트 구조 출력
echo "[6/6] 프로젝트 구조:"
echo "======================================"
find . -type f -name "*.py" | head -20
echo "======================================"

echo ""
echo "✅ 프로젝트 생성 완료!"
echo ""
echo "📋 다음 단계:"
echo "  1. config.py와 config.yaml 파일이 있는지 확인"
echo "  2. Claude Code로 다음 파일 생성:"
echo "     - gov_support/filter_strategy.py"
echo "     - gov_support/gov_support_manager.py"
echo "     - main.py"
echo "  3. 테스트 실행: python main.py"
echo ""
echo "💡 Claude Code 프롬프트:"
echo '  "gov_support_manager.py와 filter_strategy.py, main.py를 작성해주세요"'