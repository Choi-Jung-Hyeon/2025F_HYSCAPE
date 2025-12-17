#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - News Briefing Module

Workflow:
1. Process PDF briefings from shared directory
2. Collect hydrogen news articles from RSS/web sources
3. Summarize articles with Gemini AI
4. Send integrated email briefing
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, List

# Add dependencies to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dependencies'))

# Import from dependencies
from source_fetcher.factory import SourceFetcherFactory
from content_scraper import get_and_clean_article_content
from notifier import send_email
from gov_support.gov_support_manager import GovSupportManager

# Import from shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.pdf_analyzer import extract_text_from_pdf, extract_keyword_paragraphs, get_all_pdfs
from shared.gemini_client import GeminiClient

# Import config
import config_production as config

logger = logging.getLogger(__name__)


def run() -> Dict:
    """
    Execute news briefing workflow

    Returns:
        dict: {
            "status": "success" | "failed",
            "articles_sent": int,
            "error": str (if failed)
        }
    """
    logger.info("[NewsBriefing] Starting news briefing module...")

    try:
        # Initialize Gemini client
        gemini_client = GeminiClient(config.GOOGLE_API_KEY, config.GEMINI_MODEL)

        # Get date string
        today = datetime.now()
        date_str = today.strftime(config.DATE_FORMAT)

        # Step 1: Process PDF briefings
        logger.info("[NewsBriefing] Step 1/5: Processing PDF briefings...")
        pdf_summary_html = _process_pdf_briefings(gemini_client)

        # Step 2: Get government support recommendations
        logger.info("[NewsBriefing] Step 2/5: Getting government support recommendations...")
        gov_support_html = _get_gov_support_recommendations()

        # Step 3: Collect news articles
        logger.info("[NewsBriefing] Step 3/5: Collecting news articles...")
        articles = _collect_news_articles()

        # Step 4: Summarize articles
        logger.info("[NewsBriefing] Step 4/5: Summarizing articles...")
        summarized_articles = _summarize_articles(articles, gemini_client)

        # Step 5: Send email
        logger.info("[NewsBriefing] Step 5/5: Sending email...")
        news_html = _generate_news_html(summarized_articles)
        email_html = _build_email_html(pdf_summary_html, gov_support_html, news_html, date_str)

        success = send_email(
            subject=config.EMAIL_SUBJECT_TEMPLATE.format(date=date_str),
            html_body=email_html
        )

        if success:
            logger.info(f"[NewsBriefing] ✅ Email sent successfully to {len(config.RECEIVER_EMAIL)} recipients")
            return {
                "status": "success",
                "articles_sent": len(summarized_articles)
            }
        else:
            logger.error("[NewsBriefing] ❌ Email sending failed")
            return {
                "status": "failed",
                "error": "Email sending failed"
            }

    except Exception as e:
        logger.error(f"[NewsBriefing] ❌ Module failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }


def _process_pdf_briefings(gemini_client: GeminiClient) -> str:
    """
    Process PDF briefings from shared directory

    Args:
        gemini_client: Gemini API client

    Returns:
        HTML section for PDF summary
    """
    try:
        # Get PDFs from shared directory
        pdf_files = get_all_pdfs(config.PDF_DIR)

        if not pdf_files:
            logger.warning("[NewsBriefing] No PDF files found in shared directory")
            return """
            <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px;">
                <h2 style="color: #2c3e50;">📄 PDF 브리핑</h2>
                <p style="color: #7f8c8d;">처리된 PDF 브리핑이 없습니다.</p>
            </div>
            """

        # Process first PDF (most recent)
        pdf_file = pdf_files[0]
        logger.info(f"[NewsBriefing] Processing PDF: {pdf_file.name}")

        # Extract text
        full_text = extract_text_from_pdf(str(pdf_file))

        # Extract keyword paragraphs
        keyword_paragraphs = extract_keyword_paragraphs(
            full_text,
            config.PDF_TARGET_KEYWORDS
        )

        if not keyword_paragraphs:
            logger.warning("[NewsBriefing] No keyword matches in PDF")
            return """
            <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px;">
                <h2 style="color: #2c3e50;">📄 PDF 브리핑</h2>
                <p style="color: #7f8c8d;">키워드와 일치하는 내용이 없습니다.</p>
            </div>
            """

        # Summarize with Gemini
        summary_result = gemini_client.summarize_with_keywords(
            keyword_paragraphs,
            config.PDF_TARGET_KEYWORDS
        )

        summary = summary_result.get('summary', '')
        matched_keywords = summary_result.get('matched_keywords', [])

        # Generate HTML
        html = f"""
        <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px; border-left: 4px solid #3498db;">
            <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                📄 PDF 브리핑
            </h2>
            <p style="color: #7f8c8d; margin: 10px 0;">파일: {pdf_file.name} | 매칭된 키워드: {len(matched_keywords)}개</p>

            <div style="margin: 15px 0; padding: 15px; background-color: #f8f9fa; border-radius: 4px;">
                <h3 style="color: #2c3e50; font-size: 16px; margin: 0 0 10px 0;">📌 요약</h3>
                <p style="color: #555; line-height: 1.8; margin: 0;">{summary}</p>
            </div>

            <div style="margin: 10px 0;">
                <span style="color: #7f8c8d; font-size: 13px;">🔍 키워드:</span>
                <span style="color: #555; font-size: 13px; margin-left: 5px;">{', '.join(matched_keywords[:10])}</span>
            </div>
        </div>
        """

        return html

    except Exception as e:
        logger.error(f"[NewsBriefing] PDF processing failed: {e}", exc_info=True)
        return """
        <div style="margin: 20px 0; padding: 20px; background-color: #fff3cd; border-radius: 8px;">
            <h2 style="color: #856404;">⚠️ PDF 브리핑</h2>
            <p style="color: #856404;">PDF 브리핑 처리 중 오류가 발생했습니다.</p>
        </div>
        """


def _get_gov_support_recommendations() -> str:
    """
    Get government support program recommendations

    Returns:
        HTML section for government support recommendations
    """
    try:
        # Initialize manager with config file
        config_yaml_path = os.path.join(os.path.dirname(__file__), '..', 'config_production.yaml')
        manager = GovSupportManager(config_yaml_path)

        # Collect and filter notices
        manager.collect_all_notices()
        manager.apply_filters()

        # Get top 3 recommendations
        recommendations = manager.get_top_recommendations(top_n=3)

        if not recommendations:
            return """
            <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px;">
                <h2 style="color: #2c3e50;">🏛️ 정부지원사업 추천</h2>
                <p style="color: #7f8c8d;">추천할 정부지원사업이 없습니다.</p>
            </div>
            """

        # Generate HTML
        html_parts = [
            '<div style="margin: 20px 0;">',
            '  <h2 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">',
            '    🏛️ 정부지원사업 추천',
            '  </h2>',
            f'  <p style="color: #7f8c8d; margin: 10px 0;">추천 정부지원사업 {len(recommendations)}건</p>',
        ]

        for i, notice in enumerate(recommendations, 1):
            score = notice.get('score', 0)
            title = notice.get('title', '제목 없음')
            url = notice.get('url', '#')
            source = notice.get('source', '출처 미상')
            period = notice.get('period', '')

            notice_html = f"""
  <div style="margin: 15px 0; padding: 20px; background-color: white; border-radius: 8px;
              border-left: 4px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 18px;">
      <a href="{url}" style="color: #2c3e50; text-decoration: none;">{i}. {title}</a>
    </h3>

    <div style="margin: 10px 0; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
      <span style="color: #7f8c8d; font-size: 13px;">📌 {source}</span>
      {f'<span style="color: #95a5a6; font-size: 13px; margin-left: 15px;">📅 {period}</span>' if period else ''}
      <span style="color: #e74c3c; font-size: 13px; margin-left: 15px; font-weight: bold;">⭐ 관련도: {score}점</span>
    </div>

    <div style="margin-top: 10px;">
      <a href="{url}" style="color: #e74c3c; text-decoration: none; font-weight: bold; font-size: 14px;">
        자세히 보기 →
      </a>
    </div>
  </div>
"""
            html_parts.append(notice_html)

        html_parts.append('</div>')
        return '\n'.join(html_parts)

    except Exception as e:
        logger.warning(f"[NewsBriefing] Government support recommendation failed: {e}")
        return """
        <div style="margin: 20px 0; padding: 20px; background-color: #fff3cd; border-radius: 8px;">
            <h2 style="color: #856404;">⚠️ 정부지원사업 추천</h2>
            <p style="color: #856404;">정부지원사업 수집 중 오류가 발생했습니다.</p>
        </div>
        """


def _collect_news_articles() -> List[Dict]:
    """
    Collect news articles from configured sources

    Returns:
        List of article dictionaries
    """
    try:
        fetcher_manager = SourceFetcherFactory.create_manager_from_config()
        articles = fetcher_manager.fetch_all_articles(
            max_per_source=config.MAX_ARTICLES_PER_SOURCE,
            max_per_keyword=config.MAX_NAVER_PER_KEYWORD
        )
        logger.info(f"[NewsBriefing] Collected {len(articles)} articles")
        return articles[:config.MAX_TOTAL_ARTICLES]  # Limit total articles

    except Exception as e:
        logger.error(f"[NewsBriefing] Article collection failed: {e}", exc_info=True)
        return []


def _summarize_articles(articles: List[Dict], gemini_client: GeminiClient) -> List[Dict]:
    """
    Summarize articles with Gemini AI

    Args:
        articles: List of article dictionaries
        gemini_client: Gemini API client

    Returns:
        List of summarized articles
    """
    summarized = []

    for i, article in enumerate(articles, 1):
        try:
            logger.info(f"[NewsBriefing]   [{i}/{len(articles)}] {article.get('title', '')[:50]}...")

            # Extract content
            content = get_and_clean_article_content(article['url'])

            if content:
                # Summarize with Gemini
                summary_result = gemini_client.summarize_article(
                    content,
                    article['title'],
                    config.TARGET_KEYWORDS
                )

                article['summary'] = summary_result['summary']
                article['matched_keywords'] = summary_result['matched_keywords']
            else:
                article['summary'] = article.get('description', '')
                article['matched_keywords'] = []

            summarized.append(article)

        except Exception as e:
            logger.warning(f"[NewsBriefing]   Article processing failed: {e}")
            continue

    return summarized


def _generate_news_html(articles: List[Dict]) -> str:
    """
    Generate HTML for news section

    Args:
        articles: List of summarized articles

    Returns:
        HTML string
    """
    if not articles:
        return """
        <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px;">
            <h2 style="color: #2c3e50;">📰 수소 뉴스</h2>
            <p style="color: #7f8c8d;">수집된 뉴스가 없습니다.</p>
        </div>
        """

    html_parts = [
        '<div style="margin: 20px 0;">',
        '  <h2 style="color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px;">',
        '    📰 수소 뉴스',
        '  </h2>',
        f'  <p style="color: #7f8c8d; margin: 10px 0;">오늘의 수소 관련 주요 뉴스 {len(articles)}건</p>',
    ]

    for i, article in enumerate(articles, 1):
        title = article.get('title', '제목 없음')
        url = article.get('url', '#')
        source = article.get('source', '출처 미상')
        summary = article.get('summary', article.get('description', ''))
        pub_date = article.get('pub_date', '')

        article_html = f"""
  <div style="margin: 15px 0; padding: 20px; background-color: white; border-radius: 8px;
              border-left: 4px solid #27ae60; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 18px;">
      <a href="{url}" style="color: #2c3e50; text-decoration: none;">{i}. {title}</a>
    </h3>

    <div style="margin: 10px 0; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
      <span style="color: #7f8c8d; font-size: 13px;">📌 {source}</span>
      {f'<span style="color: #95a5a6; font-size: 13px; margin-left: 15px;">🕐 {pub_date}</span>' if pub_date else ''}
    </div>

    {f'<p style="color: #555; margin: 12px 0; line-height: 1.8;">{summary}</p>' if summary else ''}

    <div style="margin-top: 10px;">
      <a href="{url}" style="color: #27ae60; text-decoration: none; font-weight: bold; font-size: 14px;">
        전체 기사 읽기 →
      </a>
    </div>
  </div>
"""
        html_parts.append(article_html)

    html_parts.append('</div>')
    return '\n'.join(html_parts)


def _build_email_html(pdf_summary: str, gov_support_html: str, news_html: str, date_str: str) -> str:
    """
    Build complete email HTML

    Args:
        pdf_summary: PDF summary HTML section
        gov_support_html: Government support recommendations HTML section
        news_html: News HTML section
        date_str: Date string

    Returns:
        Complete HTML email body
    """
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hyscape Daily Briefing</title>
</head>
<body style="font-family: 'Noto Sans KR', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">

    <!-- Header -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0; font-size: 32px;">⚡ Hyscape Daily Automation</h1>
        <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 16px;">{date_str}</p>
    </div>

    <!-- PDF Summary Section -->
    {pdf_summary}

    <!-- Government Support Section -->
    {gov_support_html}

    <!-- News Section -->
    {news_html}

    <!-- Footer -->
    <div style="margin-top: 40px; padding: 20px; background-color: #2c3e50; color: white; border-radius: 8px; text-align: center;">
        <p style="margin: 5px 0; font-size: 14px;">본 브리핑은 AI 기반 자동 수집 및 요약 시스템으로 생성되었습니다.</p>
        <p style="margin: 5px 0; font-size: 12px; color: #95a5a6;">
            Powered by Gemini AI | © {datetime.now().year} Hyscape
        </p>
    </div>

</body>
</html>
"""
    return html
