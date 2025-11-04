# main.py (v7.0)
"""
수소 뉴스 자동 요약 및 이메일 발송 시스템 v7.0
- 모듈화된 source_fetcher 아키텍처
- Target 키워드 (기술 + 회사) 중심
- 구글 뉴스 추가
- PDF 키워드 중심 요약
- 실패 소스 로깅
"""

import time
from datetime import datetime

# v7.0 모듈 (수정됨!)
from source_fetcher.factory import SourceFetcherFactory  # ⭐ 변경!
from content_scraper import get_and_clean_article_content
from summarizer import get_summary_and_keywords, generate_article_html, calculate_relevance_score
from notifier import send_email
from pdf_reader import process_pdf_briefing, generate_pdf_html
from config import MAX_TOTAL_ARTICLES

def run_workflow():
    """전체 워크플로우 실행"""
    
    print("=" * 80)
    print("🚀 수소 뉴스 브리핑 시스템 v7.0 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # ========================================
    # 0. PDF 브리핑 처리 (Target 키워드 중심)
    # ========================================
    print("\n[단계 0] PDF 브리핑 파일 처리 (키워드 중심 요약)")
    pdf_result = process_pdf_briefing()
    
    pdf_html = generate_pdf_html(pdf_result)
    
    # ========================================
    # 1. 뉴스 소스에서 기사 수집
    # ========================================
    print("\n[단계 1] 뉴스 소스에서 기사 수집")
    print("  - 월간수소경제")
    print("  - Hydrogen Central")
    print("  - 네이버 뉴스 (4개 키워드)")
    print("  - 구글 뉴스 (5개 키워드) ⭐")
    print("-" * 80)
    
    # ⭐ 변경: Factory 패턴 사용
    manager = SourceFetcherFactory.create_manager_from_config()
    articles = manager.fetch_all_articles()
    
    if not articles:
        print("\n⚠️  처리할 기사가 없습니다. 시스템을 종료합니다.")
        return
    
    # 기사 수 제한
    if len(articles) > MAX_TOTAL_ARTICLES:
        print(f"\n📌 전체 기사 수 제한: {len(articles)}개 → {MAX_TOTAL_ARTICLES}개")
        articles = articles[:MAX_TOTAL_ARTICLES]
    
    # ========================================
    # 2. 각 기사 처리 (스크래핑 + 요약)
    # ========================================
    print(f"\n[단계 2] {len(articles)}개 기사 처리 (스크래핑 + 요약)")
    print("-" * 80)
    
    processed_articles = []
    success_count = 0
    
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] {article['title'][:60]}...")
        print(f"  출처: {article['source']}")
        
        try:
            # 2-1. 본문 스크래핑
            print("  ⏳ 본문 추출 중...")
            content = get_and_clean_article_content(article['url'], article['source'])
            
            if not content:
                print("  ⚠️  본문 추출 실패")
                continue
            
            print(f"  ✅ 본문 추출 완료 ({len(content)}자)")
            
            # 2-2. Gemini 요약
            print("  ⏳ AI 요약 중...")
            summary_result = get_summary_and_keywords(content, article['title'])
            
            if not summary_result['summary'] or summary_result['summary'] == "요약 실패":
                print("  ⚠️  요약 실패")
                continue
            
            # 관련도 점수 계산
            relevance_score = calculate_relevance_score(summary_result['matched_keywords'])
            
            print(f"  ✅ 요약 완료")
            print(f"     - 매칭 키워드: {len(summary_result['matched_keywords'])}개")
            print(f"     - 회사 키워드: {'있음 ⭐' if summary_result['has_company'] else '없음'}")
            print(f"     - 관련도 점수: {relevance_score}점")
            
            # 처리 완료 기사 저장
            processed_articles.append({
                'article': article,
                'summary_result': summary_result,
                'relevance_score': relevance_score
            })
            
            success_count += 1
            time.sleep(1)  # API 요청 간격
            
        except Exception as e:
            print(f"  ⚠️  처리 중 오류: {e}")
            continue
    
    # ========================================
    # 3. 관련도 순으로 정렬
    # ========================================
    processed_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    print(f"\n{'=' * 80}")
    print(f"✅ 총 {success_count}개 기사 처리 완료")
    print(f"{'=' * 80}")
    
    if not processed_articles:
        print("\n⚠️  처리된 기사가 없습니다.")
        return
    
    # ========================================
    # 4. 이메일 본문 생성
    # ========================================
    print("\n[단계 3] 이메일 본문 생성")
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # HTML 헤더
    email_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Noto Sans KR', Arial, sans-serif; 
                 max-width: 900px; margin: 0 auto; padding: 20px;">
        
        <!-- 제목 -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="margin: 0;">📰 {today_str} 수소 뉴스 브리핑</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">
                v7.0 - 모듈화 아키텍처 | 총 {len(processed_articles)}개 기사
            </p>
        </div>
        
        <!-- 요약 통계 -->
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <h3 style="margin-top: 0;">📊 브리핑 요약</h3>
            <ul style="line-height: 2;">
                <li>총 기사: <strong>{len(processed_articles)}개</strong></li>
                <li>회사 키워드 포함: <strong>{sum(1 for x in processed_articles if x['summary_result']['has_company'])}개</strong> ⭐</li>
                <li>기술 키워드 포함: <strong>{sum(1 for x in processed_articles if x['summary_result']['has_tech'])}개</strong></li>
                <li>PDF 브리핑: <strong>{pdf_result.get('status', 'no_files')}</strong></li>
            </ul>
        </div>
    """
    
    # PDF 요약 추가
    if pdf_html:
        email_html += pdf_html
    
    # 기사 추가
    email_html += """
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            📰 수집 기사 요약
        </h2>
    """
    
    for i, item in enumerate(processed_articles, 1):
        email_html += generate_article_html(item['article'], item['summary_result'])
    
    # HTML 푸터
    email_html += f"""
        <div style="margin-top: 40px; padding: 20px; background-color: #ecf0f1; 
                    border-radius: 10px; text-align: center;">
            <p style="color: #7f8c8d; margin: 0;">
                수소 뉴스 자동 브리핑 시스템 v7.0 (모듈화 아키텍처)<br>
                생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </body>
    </html>
    """
    
    # ========================================
    # 5. 이메일 발송
    # ========================================
    print("\n[단계 4] 이메일 발송")
    
    subject = f"[수소 브리핑 v7.0] {today_str} - {len(processed_articles)}개 기사"
    
    success = send_email(subject, email_html)
    
    if success:
        print(f"\n{'=' * 80}")
        print("🎉 수소 뉴스 브리핑 v7.0 완료!")
        print(f"{'=' * 80}")
    else:
        print("\n⚠️  이메일 발송 실패")

# ========================================
# 실행
# ========================================
if __name__ == "__main__":
    run_workflow()