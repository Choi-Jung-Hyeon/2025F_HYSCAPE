#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Shared Gemini API Client

Unified Gemini API client with retry logic and multiple analysis modes:
- Mode 1: Keyword-based summary (for email news briefing)
- Mode 2: Comprehensive analysis (for Notion archive)
- Mode 3: Article summary (for email news articles)
"""

import json
import time
import logging
import re
from typing import Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Unified Gemini API client with retry logic and mode-specific prompting
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key
            model: Model name (default: gemini-2.0-flash)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        logger.info(f"Gemini client initialized with model: {model}")

    def generate(self, prompt: str, temperature: float = 0.3, max_retries: int = 2) -> str:
        """
        Core generation method with retry logic

        Args:
            prompt: Prompt text
            temperature: Generation temperature (default: 0.3 for deterministic)
            max_retries: Maximum retry attempts (default: 2)

        Returns:
            Generated text

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": 800
                    }
                    # Safety settings removed - using defaults
                )

                return response.text.strip()

            except Exception as e:
                error_str = str(e).lower()

                # Check for quota/rate limit errors (429)
                if '429' in error_str or 'quota' in error_str or 'rate limit' in error_str:
                    if attempt < max_retries:
                        wait_time = 30  # 30 seconds wait (from mail_gov_integrated/summarizer.py)
                        logger.warning(f"API quota exceeded, waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue

                # For other errors or final retry, raise
                logger.error(f"Gemini API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt >= max_retries:
                    raise

        raise Exception(f"All {max_retries + 1} attempts failed")

    def summarize_with_keywords(self, paragraphs: List[str], keywords: List[str]) -> Dict:
        """
        Mode 1: Keyword-based summary for email briefing

        Args:
            paragraphs: List of paragraphs containing keywords
            keywords: List of matched keywords

        Returns:
            {
                "summary": str,
                "matched_keywords": list[str]
            }
        """
        if not paragraphs:
            return {"summary": "", "matched_keywords": []}

        # Limit paragraphs for API token limits
        text = "\n\n".join(paragraphs[:10])  # Max 10 paragraphs

        prompt = f"""
다음은 수소/수전해 관련 PDF 브리핑에서 추출한 내용입니다.
핵심 키워드: {', '.join(keywords[:20])}

**추출된 내용:**
{text}

**요약 지침:**
1. 3-5줄로 핵심 내용 요약 (한국어)
2. 주요 키워드 강조
3. 구체적인 수치, 날짜, 기업명 포함
4. 기술적 세부사항 포함

**요약:**
"""

        summary = self.generate(prompt)

        return {
            "summary": summary,
            "matched_keywords": keywords
        }

    def analyze_briefing(self, text: str, analysis_prompt_template: str) -> Dict:
        """
        Mode 2: Comprehensive analysis for Notion archive

        Args:
            text: Full PDF text
            analysis_prompt_template: Prompt template with {content} placeholder

        Returns:
            {
                "summary": str,
                "sentiment": str,  # Positive/Negative/Neutral
                "category": str,   # 기관/정책/지자체/산업계/연구계/해외
                "keywords": list[str]
            }
        """
        # Limit text length for API token limits
        text = text[:10000]  # Max 10,000 chars

        prompt = analysis_prompt_template.format(content=text)

        response_text = self.generate(prompt)

        # Parse JSON response
        analysis = self._parse_json_response(response_text)

        # Validate and auto-correct
        analysis = self._validate_analysis(analysis)

        return analysis

    def summarize_article(self, content: str, title: str, keywords: List[str]) -> Dict:
        """
        Mode 3: Article summary for email news section

        Args:
            content: Article content
            title: Article title
            keywords: Target keywords for matching

        Returns:
            {
                "summary": str,
                "matched_keywords": list[str],
                "score": int
            }
        """
        # Limit content for API
        content = content[:5000]  # Max 5,000 chars

        # Build prompt
        prompt = f"""
다음 수소 관련 뉴스 기사를 분석하여 요약해주세요.

**기사 제목:** {title}

**기사 내용:**
{content}

**주요 키워드:** {', '.join(keywords[:30])}

**요약 지침:**
1. 핵심 내용 3-5줄로 요약 (한국어)
2. 기업명이 언급되면 **굵게** 표시
3. 기술 키워드 포함 시 세부사항 설명
4. 투자/계약/협력 내용은 금액과 시기 포함
5. 구체적인 수치 포함

**요약:**
"""

        summary = self.generate(prompt)

        # Extract matched keywords from summary
        matched_keywords = []
        summary_lower = summary.lower()
        for keyword in keywords:
            if keyword.lower() in summary_lower:
                matched_keywords.append(keyword)

        # Calculate relevance score
        score = len(matched_keywords) * 10

        return {
            "summary": summary,
            "matched_keywords": matched_keywords,
            "score": score
        }

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Parse JSON from Gemini response (may include code blocks)

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed JSON dict
        """
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()

        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

            logger.error(f"Failed to parse JSON from response: {response_text[:200]}")
            raise Exception(f"Invalid JSON response from Gemini")

    def _validate_analysis(self, analysis: Dict) -> Dict:
        """
        Validate and auto-correct analysis output

        Args:
            analysis: Parsed analysis dict

        Returns:
            Validated and corrected dict
        """
        # Ensure required keys
        required_keys = ['summary', 'sentiment', 'category', 'keywords']
        for key in required_keys:
            if key not in analysis:
                logger.warning(f"Missing key '{key}' in analysis, using default")
                if key == 'keywords':
                    analysis[key] = []
                else:
                    analysis[key] = ""

        # Validate sentiment
        valid_sentiments = ['Positive', 'Negative', 'Neutral']
        if analysis['sentiment'] not in valid_sentiments:
            logger.warning(f"Invalid sentiment '{analysis['sentiment']}', defaulting to 'Neutral'")
            analysis['sentiment'] = 'Neutral'

        # Validate category
        valid_categories = ['기관', '정책', '지자체', '산업계', '연구계', '해외']
        if analysis['category'] not in valid_categories:
            logger.warning(f"Invalid category '{analysis['category']}', defaulting to '기관'")
            analysis['category'] = '기관'

        # Validate keywords (ensure it's a list, limit to 5)
        if not isinstance(analysis['keywords'], list):
            analysis['keywords'] = []
        analysis['keywords'] = analysis['keywords'][:5]

        return analysis
