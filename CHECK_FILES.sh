#!/bin/bash
# 파일 검증 및 수정 스크립트

echo "=== H2HUB 파일 버전 검증 ==="
echo ""

# 필수 파일 확인
FILES=("main.py" "article_analyzer.py" "article_collector.py" "notion_uploader.py" "config.py")

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ $file 없음"
    else
        echo "✅ $file 존재"
    fi
done

echo ""
echo "=== 클래스 확인 ==="

# article_analyzer.py의 클래스 확인
if [ -f "article_analyzer.py" ]; then
    echo "article_analyzer.py의 클래스:"
    grep "^class " article_analyzer.py || echo "  클래스 없음"
fi

echo ""

# main.py의 import 확인
if [ -f "main.py" ]; then
    echo "main.py의 import:"
    head -20 main.py | grep "from article_analyzer import"
fi

echo ""
echo "=== 해결 방법 ==="
echo "1. article_analyzer.py에 'BriefingAnalyzer' 클래스가 없으면:"
echo "   → Claude에서 제공한 최신 article_analyzer.py를 다시 다운로드"
echo ""
echo "2. 또는 모든 Python 파일을 다시 다운로드 (권장)"