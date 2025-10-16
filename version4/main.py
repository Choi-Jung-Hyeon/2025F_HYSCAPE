# main.py (v2.1 - PDF 통합)
"""
수소 뉴스 자동 요약 및 이메일 발송 시스템 메인 스크립트
- 다중 뉴스 소스 수집
- 네이버 뉴스 검색
- PDF 브리핑 파일 처리
"""

import time
from datetime import datetime

# v2.1 모듈 임포트
from source_fetcher import create_fetchers_from_config
from content_scraper import get_and_clean_article_content
from summarizer import get_summary_and_keywords
from notifier import send_email
from pdf_reader import process_pdf_briefing
from config import MAX_ARTICLES_PER_SOURCE, MAX_TOTAL_ARTICLES


def run_workflow():
    """전체 워크플로우를 실행하는 메인 함수"""
    
    print("=" * 70)
    print(f"🚀 수소 뉴스 브리핑 시스템 v2.1 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ========================================
    # 0. PDF 브리핑 파일 처리 (선택사항)
    # ========================================
    print("\n[단계 0] PDF 브리핑 파일을 처리합니다...")
    pdf_result = process_pdf_briefing()
    
    pdf_keywords = pdf_result.get('keywords', [])
    if pdf_keywords:
        print(f"  ✅ PDF에서 {len(pdf_keywords)}개 키워드 추출 완료")

    # ========================================
    # 1. 다중 뉴스 소스에서 기사 수집
    # ========================================
    print("\n[단계 1] 뉴스 소스에서 기사를 수집합니다...")
    
    manager = create_fetchers_from_config()
    articles = manager.fetch_all_articles(limit_per_source=MAX_ARTICLES_PER_SOURCE)

    if not articles:
        print("\n⚠️  처리할 새로운 기사가 없습니다. 시스템을 종료합니다.")
        return

    # 전체 기사 수 제한 적용
    if len(articles) > MAX_TOTAL_ARTICLES:
        print(f"\n📌 전체 기사 수 제한: {len(articles)}개 → {MAX_TOTAL_ARTICLES}개")
        articles = articles[:MAX_TOTAL_ARTICLES]

    # ========================================
    # 2. 이메일 본문 생성 시작
    # ========================================
    today_str = datetime.now().strftime('%Y-%m-%d')
    email_body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h1 style="color: #0066cc;">📰 {today_str} 수소 뉴스 브리핑 (v2.1)</h1>
        <p style="color: #666;">총 <strong>{len(articles)}</strong>개의 기사를 수집했습니다.</p>
    """
    
    # PDF 키워드 섹션 추가
    if pdf_keywords:
        email_body_html += f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #0066cc; margin: 20px 0;">
            <h3 style="color: #0066cc; margin-top: 0;">📄 PDF 브리핑 주요 키워드</h3>
            <p style="line-height: 1.8;">{', '.join(pdf_keywords)}</p>
        </div>
        """
    
    success_count = 0
    failed_articles = []

    # ========================================
    # 3. 각 기사 처리 루프
    # ========================================
    print(f"\n[단계 2] 총 {len(articles)}개 기사를 처리합니다...")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{'─' * 70}")
        print(f"[{i}/{len(articles)}] 처리 중: {article['title'][:50]}...")
        print(f"출처: {article['source']}")
        
        try:
            # 3-1. 본문 추출
            print("  ├─ 본문 추출 중...", end=" ")
            content = get_and_clean_article_content(article['url'])
            
            if not content or len(content) < 100:
                print("❌ 실패 (본문이 너무 짧음)")
                failed_articles.append((article, "본문 추출 실패"))
                continue
            
            print(f"✅ 성공 ({len(content)}자)")

            # 3-2. AI 요약
            print("  ├─ AI 요약 중...", end=" ")
            summary, keywords = get_summary_and_keywords(article['title'], content)
            
            if not summary:
                print("❌ 실패")
                failed_articles.append((article, "AI 요약 실패"))
                continue
            
            print("✅ 성공")
            
            # 3-3. 이메일 본문에 추가
            email_body_html += f"""
            <div style="border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px;">
                <h3 style="color: #333; margin-top: 0;">
                    <span style="color: #0066cc;">[{success_count + 1}]</span> {article['title']}
                </h3>
                <p style="color: #888; font-size: 0.9em;">
                    📰 출처: {article['source']} | 
                    <a href="{article['url']}" style="color: #0066cc;">원문 보기</a>
                </p>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 3px solid #0066cc;">
                    <p style="line-height: 1.6; color: #555;">{summary}</p>
                </div>
                <p style="margin-top: 10px;">
                    <strong>🔑 키워드:</strong> 
                    <span style="color: #0066cc;">{', '.join(keywords)}</span>
                </p>
            </div>
            """
            
            success_count += 1
            print(f"  └─ ✅ 완료 ({success_count}/{len(articles)})")
            
            # API 호출 제한 방지를 위한 짧은 대기
            time.sleep(2)
            
        except Exception as e:
            print(f"  └─ ❌ 처리 중 오류 발생: {e}")
            failed_articles.append((article, str(e)))

    # ========================================
    # 4. 이메일 본문 마무리
    # ========================================
    email_body_html += f"""
        <div style="margin-top: 40px; padding: 20px; background-color: #f5f5f5; border-radius: 5px;">
            <h3 style="color: #333;">📊 처리 결과</h3>
            <ul style="color: #555;">
                <li>✅ 성공: <strong>{success_count}</strong>개</li>
                <li>❌ 실패: <strong>{len(failed_articles)}</strong>개</li>
            </ul>
    """
    
    if failed_articles:
        email_body_html += """
            <h4 style="color: #d9534f;">실패한 기사 목록:</h4>
            <ul style="color: #777; font-size: 0.9em;">
        """
        for article, reason in failed_articles:
            email_body_html += f"<li>{article['title'][:60]}... ({reason})</li>"
        email_body_html += "</ul>"
    
    email_body_html += """
        </div>
        <p style="text-align: center; color: #999; margin-top: 30px;">
            <small>본 메일은 AI 기반 자동 요약 시스템에 의해 생성되었습니다.</small>
        </p>
    </div>
    """

    # ========================================
    # 5. 이메일 발송
    # ========================================
    print(f"\n[단계 3] 이메일을 발송합니다...")
    
    if success_count > 0:
        subject = f"[수소 뉴스] {today_str} 일일 브리핑 ({success_count}개)"
        send_email(subject, email_body_html)
        print("  ✅ 이메일 발송 완료!")
    else:
        print("  ⚠️  요약된 기사가 없어 이메일을 발송하지 않습니다.")

    print("\n" + "=" * 70)
    print("✨ 모든 작업을 완료했습니다!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        run_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()