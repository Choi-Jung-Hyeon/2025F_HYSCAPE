#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국수소연합(H2HUB) 브리핑 자동화 시스템 - 설정 파일 템플릿
이 파일을 config.py로 복사하여 사용하세요.
"""

import os
from pathlib import Path

# ===== 기본 경로 설정 =====
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# ===== H2HUB 웹사이트 설정 =====
H2HUB_BASE_URL = "https://h2hub.or.kr"
H2HUB_PERIODICALS_URL = "https://h2hub.or.kr/main/yard/periodicals.do"

# 브리핑 키워드 필터
BRIEFING_KEYWORDS = ["브리핑", "일간", "주간", "월간"]

# HTTP 요청 헤더
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# ===== OpenAI API 설정 =====
# TODO: 여기에 실제 OpenAI API 키를 입력하세요
# 발급: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-openai-api-key-here")
OPENAI_MODEL = "gpt-4o"  # gpt-4o 모델 사용

# AI 분석 프롬프트
ANALYSIS_PROMPT = """
당신은 수소 및 수전해 기술 전문 분석가입니다.
아래 PDF 브리핑 내용을 분석하여 JSON 형식으로 답변해주세요.

**분석 기준:**
- **summary**: 핵심 내용을 3줄 이내로 요약 (한국어)
- **sentiment**: 수전해 및 수소 기술 발전 관점에서의 전망
  * "Positive" (긍정적): 기술 투자, 정부 지원, R&D 성과, 산업 확대
  * "Negative" (부정적): 규제 강화, 예산 삭감, 프로젝트 취소
  * "Neutral" (중립): 단순 현황 보고, 중립적 뉴스

**출력 형식 (JSON):**
{{
  "summary": "요약 내용",
  "sentiment": "Positive/Negative/Neutral"
}}

**분석 대상 내용:**
{content}
"""

# ===== Notion API 설정 =====
# TODO: 여기에 실제 Notion API 키와 데이터베이스 ID를 입력하세요
# Notion Integration 생성: https://www.notion.so/my-integrations
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "secret_your-notion-integration-key")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "your-database-id-here")

# Notion 속성 매핑
# 주의: 이 속성 이름들이 실제 Notion 데이터베이스의 속성 이름과 정확히 일치해야 합니다!
NOTION_PROPERTIES = {
    "title": "제목",        # Title 속성
    "date": "날짜",         # Date 속성
    "summary": "요약",      # Rich Text 속성
    "url": "링크",          # URL 속성
    "sentiment": "기술전망"  # Select 속성 (🟢 긍정적, 🔴 부정적, 🟡 중립)
}

# Sentiment 매핑
# Notion의 Select 속성에 이 값들이 정확히 등록되어 있어야 합니다!
SENTIMENT_TAGS = {
    "Positive": "🟢 긍정적",
    "Negative": "🔴 부정적",
    "Neutral": "🟡 중립"
}

# ===== 로깅 설정 =====
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
