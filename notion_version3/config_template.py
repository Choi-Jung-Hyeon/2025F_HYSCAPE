#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한국수소연합(H2HUB) 브리핑 자동화 시스템 설정 파일"""

import os
from pathlib import Path

# ===== 경로 설정 =====
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# ===== H2HUB 웹사이트 =====
H2HUB_BASE_URL = "https://h2hub.or.kr"
H2HUB_PERIODICALS_URL = "https://h2hub.or.kr/main/yard/periodicals.do"

BRIEFING_KEYWORDS = ["브리핑", "일간", "주간", "월간"]

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Connection': 'keep-alive'
}

# ===== Google Gemini API =====
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")
GEMINI_MODEL = "gemini-2.0-flash-exp"

# 분석 프롬프트
ANALYSIS_PROMPT = """다음 수소 브리핑을 분석하여 JSON으로 답변:

1. summary: 핵심 내용 3줄 요약
2. sentiment: Positive/Negative/Neutral
3. category: 기관/정책/지자체/산업계/연구계/해외 중 1개
4. keywords: 핵심 키워드 3-5개 (배열)

JSON 형식:
{{
  "summary": "...",
  "sentiment": "Positive",
  "category": "기관",
  "keywords": ["수소", "수전해"]
}}

텍스트:
{content}
"""

# ===== Notion API =====
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "secret_your-notion-key")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "your-database-id")

# Notion 속성 매핑 (실제 DB 속성명과 일치해야 함)
NOTION_PROPERTIES = {
    "title": "제목",
    "date": "날짜",
    "summary": "요약",
    "url": "링크",
    "sentiment": "기술전망",
    "category": "category",
    "keywords": "키워드"
}

# Select 옵션 매핑
SENTIMENT_TAGS = {
    "Positive": "🟢 긍정적",
    "Negative": "🔴 부정적",
    "Neutral": "🟡 중립"
}

CATEGORY_TAGS = {
    "기관": "🏛️ 기관",
    "정책": "📜 정책",
    "지자체": "🏙️ 지자체",
    "산업계": "🏭 산업계",
    "연구계": "🔬 연구계",
    "해외": "🌏 해외"
}

# ===== 로깅 =====
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'