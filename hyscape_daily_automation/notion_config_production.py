#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Notion Configuration
Settings for Notion database integration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# ===== Notion API Settings =====
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# ===== Notion Property Mappings =====
# Maps internal field names to actual Notion database property names
NOTION_PROPERTIES = {
    "title": "제목",        # Title type
    "date": "date",         # Date type
    "summary": "요약",      # Rich Text type
    "url": "url",           # URL type
    "sentiment": "기술전망",  # Select type
    "category": "category",  # Select type
    "keywords": "키워드"     # Multi-select type
}

# ===== Sentiment Tag Mappings =====
# Maps AI sentiment values to Notion select options with emoji prefixes
SENTIMENT_TAGS = {
    "Positive": "🟢 긍정적",
    "Negative": "🔴 부정적",
    "Neutral": "🟡 중립"
}

# ===== Category Tag Mappings =====
# Maps AI category values to Notion select options with emoji prefixes
CATEGORY_TAGS = {
    "기관": "🏛️ 기관",
    "정책": "📜 정책",
    "지자체": "🏙️ 지자체",
    "산업계": "🏭 산업계",
    "연구계": "🔬 연구계",
    "해외": "🌏 해외"
}

# ===== Analysis Prompt =====
# Structured prompt for comprehensive PDF briefing analysis
ANALYSIS_PROMPT = """
당신은 수소 및 수전해 기술 전문 분석가입니다.
아래 PDF 브리핑 내용을 분석하여 JSON 형식으로 답변해주세요.

**분석 기준:**

1. **summary** (요약): 핵심 내용을 3줄 이내로 요약 (한국어)

2. **sentiment** (기술전망): 수전해 및 수소 기술 발전 관점에서의 전망
   - "Positive": 기술 투자, 정부 지원, R&D 성과, 산업 확대
   - "Negative": 규제 강화, 예산 삭감, 프로젝트 취소
   - "Neutral": 단순 현황 보고, 중립적 뉴스

3. **category** (카테고리): 주요 출처/주체를 1개만 선택
   - "기관": 공공기관, 협회, 위원회 관련
   - "정책": 정부 정책, 법안, 규제 관련
   - "지자체": 지방자치단체, 시/도 관련
   - "산업계": 기업, 업계 동향 관련
   - "연구계": 대학, 연구소, R&D 관련
   - "해외": 해외 동향, 글로벌 이슈

4. **keywords** (키워드): 핵심 키워드 3-5개 추출 (한국어, 배열)
   - 기술명: 수소, 수전해, AEM, PEM, 액화수소 등
   - 주제어: 청정수소, 그린수소, 충전소, 연료전지 등
   - 산업어: 투자, 개정안, 규제, 인증 등

**출력 형식 (JSON):**
{{
  "summary": "요약 내용",
  "sentiment": "Positive",
  "category": "기관",
  "keywords": ["수소", "수전해", "청정수소"]
}}

**중요:** 반드시 위 4개 필드를 모두 포함하고, keywords는 배열 형태로 작성하세요.

**분석 대상 내용:**
{content}
"""
