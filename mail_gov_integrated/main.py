#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수소 산업 통합 브리핑 시스템 메인 스크립트

통합 워크플로우:
1. PDF 브리핑 처리
2. 정부지원사업 추천 (신규!)
3. 수소 뉴스 수집
4. 기사 본문 추출 및 AI 요약
5. 이메일 발송
"""

import os
import sys
import logging
from datetime import datetime

# 로컬 모듈 import
import config
from pdf_reader import process_pdf_briefing, generate_pdf_html
from source_fetcher import SourceFetcherFactory
from content_scraper import get_and_clean_article_content
from summarizer import get_summary_and_keywords
from notifier import send_email
from gov_support.gov_support_manager import GovSupportManager


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/integrated_system.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def build_email_html(pdf_summary: str, gov_support_html: str, news_html: str, date_str: str) -> str:
    """
    이메일 HTML 본문 생성

    Args:
        pdf_summary: PDF 브리핑 요약 HTML
        gov_support_html: 정부지원사업 섹션 HTML
        news_html: 수소 뉴스 섹션 HTML
        date_str: 날짜 문자열

    Returns:
        str: 완성된 HTML 본문
    """
    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>수소 산업 통합 브리핑</title>
</head>
<body style="font-family: 'Noto Sans KR', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">

    <!-- 헤더 -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; margin: 0; font-size: 32px;">⚡ 수소 산업 통합 브리핑</h1>
        <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 16px;">{date_str}</p>
    </div>

    <!-- PDF 요약 섹션 -->
    {pdf_summary}

    <!-- 정부지원사업 추천 섹션 (신규!) -->
    {gov_support_html}

    <!-- 수소 뉴스 섹션 -->
    {news_html}

    <!-- 푸터 -->
    <div style="margin-top: 40px; padding: 20px; background-color: #2c3e50; color: white; border-radius: 8px; text-align: center;">
        <p style="margin: 5px 0; font-size: 14px;">본 브리핑은 AI 기반 자동 수집 및 요약 시스템으로 생성되었습니다.</p>
        <p style="margin: 5px 0; font-size: 12px; color: #95a5a6;">
            Powered by Gemini AI | © {datetime.now().year} Hyscape
        </p>
    </div>

</body>
</html>
"""
    return html_template


def generate_news_html(articles: list) -> str:
    """
    수소 뉴스 HTML 섹션 생성

    Args:
        articles: 기사 리스트

    Returns:
        str: 뉴스 섹션 HTML
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


def main():
    """메인 실행 함수"""
    logger = setup_logging()

    print("\n" + "=" * 80)
    print("⚡ 수소 산업 통합 브리핑 시스템 시작")
    print("=" * 80 + "\n")

    try:
        # 날짜 문자열 생성
        today = datetime.now()
        date_str = today.strftime(config.DATE_FORMAT)

        # ========================================
        # 1단계: PDF 브리핑 처리
        # ========================================
        logger.info("\n[1/5] PDF 브리핑 처리 중...")
        try:
            pdf_result = process_pdf_briefing()
            pdf_summary_html = generate_pdf_html(pdf_result)
            if not pdf_summary_html:
                pdf_summary_html = """
                <div style="margin: 20px 0; padding: 20px; background-color: white; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">📄 PDF 브리핑</h2>
                    <p style="color: #7f8c8d;">처리된 PDF 브리핑이 없습니다.</p>
                </div>
                """
            logger.info("✓ PDF 브리핑 처리 완료")
        except Exception as e:
            logger.error(f"✗ PDF 브리핑 처리 실패: {e}", exc_info=True)
            pdf_summary_html = """
            <div style="margin: 20px 0; padding: 20px; background-color: #fff3cd; border-radius: 8px;">
                <h2 style="color: #856404;">⚠️ PDF 브리핑</h2>
                <p style="color: #856404;">PDF 브리핑 처리 중 오류가 발생했습니다.</p>
            </div>
            """

        # ========================================
        # 2단계: 정부지원사업 추천 (신규!)
        # ========================================
        logger.info("\n[2/5] 정부지원사업 추천 수집 중...")
        try:
            gov_manager = GovSupportManager('config.yaml')
            gov_support_html = gov_manager.generate_html_section(top_n=5)
            logger.info("✓ 정부지원사업 추천 완료")
        except Exception as e:
            logger.error(f"✗ 정부지원사업 추천 실패: {e}", exc_info=True)
            gov_support_html = """
            <div style="margin: 20px 0; padding: 20px; background-color: #f8d7da; border-radius: 8px;">
                <h2 style="color: #721c24;">❌ 정부지원사업 추천</h2>
                <p style="color: #721c24;">정부지원사업 수집 중 오류가 발생했습니다.</p>
            </div>
            """

        # ========================================
        # 3단계: 수소 뉴스 수집
        # ========================================
        logger.info("\n[3/5] 수소 뉴스 수집 중...")
        try:
            fetcher_manager = SourceFetcherFactory.create_manager_from_config()
            all_articles = fetcher_manager.fetch_all_articles(
                max_per_source=config.MAX_ARTICLES_PER_SOURCE,
                max_per_keyword=config.MAX_NAVER_PER_KEYWORD
            )
            logger.info(f"✓ 총 {len(all_articles)}개 기사 수집 완료")
        except Exception as e:
            logger.error(f"✗ 뉴스 수집 실패: {e}", exc_info=True)
            all_articles = []

        # ========================================
        # 4단계: 기사 본문 추출 및 AI 요약
        # ========================================
        logger.info("\n[4/5] 기사 본문 추출 및 AI 요약 중...")
        summarized_articles = []
        for i, article in enumerate(all_articles, 1):
            try:
                logger.info(f"  [{i}/{len(all_articles)}] {article.get('title', '')[:50]}...")

                # 본문 추출
                content = get_and_clean_article_content(article['url'])
                if content:
                    # AI 요약
                    summary_result = get_summary_and_keywords(content, article['title'])
                    article['summary'] = summary_result['summary']
                    article['matched_keywords'] = summary_result['matched_keywords']
                    article['full_content'] = content
                else:
                    article['summary'] = article.get('description', '')
                    article['matched_keywords'] = []

                summarized_articles.append(article)

            except Exception as e:
                logger.warning(f"  기사 처리 실패: {e}")
                continue

        logger.info(f"✓ {len(summarized_articles)}개 기사 요약 완료")

        # ========================================
        # 5단계: 이메일 발송
        # ========================================
        logger.info("\n[5/5] 이메일 생성 및 발송 중...")

        # 뉴스 HTML 생성
        news_html = generate_news_html(summarized_articles)

        # 전체 이메일 HTML 조합
        email_html = build_email_html(
            pdf_summary=pdf_summary_html,
            gov_support_html=gov_support_html,
            news_html=news_html,
            date_str=date_str
        )

        # 이메일 발송
        subject = config.EMAIL_SUBJECT_TEMPLATE.format(date=date_str)
        success = send_email(subject, email_html)

        if success:
            logger.info("✓ 이메일 발송 완료!")
        else:
            logger.error("✗ 이메일 발송 실패")

        # ========================================
        # 완료
        # ========================================
        print("\n" + "=" * 80)
        print("⚡ 수소 산업 통합 브리핑 시스템 완료")
        print("=" * 80)
        print(f"\n📊 처리 결과:")
        print(f"  - PDF 브리핑: {'완료' if 'PDF 브리핑이 없습니다' not in pdf_summary_html else '없음'}")
        print(f"  - 정부지원사업: {'완료' if '추천할 공고가 없습니다' not in gov_support_html else '없음'}")
        print(f"  - 수소 뉴스: {len(summarized_articles)}건")
        print(f"  - 이메일 발송: {'성공' if success else '실패'}")
        print()

        return 0

    except KeyboardInterrupt:
        logger.warning("\n\n사용자에 의해 중단되었습니다.")
        return 1

    except Exception as e:
        logger.error(f"\n\n예상치 못한 오류 발생: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
