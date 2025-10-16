# main.py (v2.0)
"""
수소 뉴스 자동 요약 및 이메일 발송 시스템 메인 스크립트
"""

import time
from datetime import datetime

# v2.0 모듈 임포트
from source_fetcher import create_fetchers_from_config
from content_scraper import get_and_clean_article_content
from summarizer import get_summary_and_keywords
from notifier import send_email


def run_workflow():
    """전체 워크플로우를 실행하는 메인 함수"""
    
    print("=" * 70)
    print(f"🚀 수소 뉴스 브리핑 시스템 v2.0 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ========================================
    # 1. 다중 뉴스 소스에서 기사 수집
    # ========================================
    print("\n[단계 1] 뉴스 소스에서 기사를 수집합니다...")
    
    manager = create_fetchers_from_config()
    articles = manager.fetch_all_articles(limit_per_source=5)  # 소스당 최대 5개

    if not articles:
        print("\n⚠️  처리할 새로운 기사가 없습니다. 시스템을 종료합니다.")
        return

    # 전체 기사 수 제한 (최대 10개)
    max_total = 10
    if len(articles) > max_total:
        print(f"\n📌 전체 기사 수 제한: {len(articles)}개 → {max_total}개")
        articles = articles[:max_total]

    # ========================================
    # 2. 이메일 본문 생성 시작
    # ========================================
    today_str = datetime.now().strftime('%Y-%m-%d')
    email_body_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h1 style="color: #0066cc;">📰 {today_str} 수소 뉴스 브리핑 (v2.0)</h1>
        <p style="color: #666;">총 <strong>{len(articles)}</strong>개의 기사를 수집했습니다.</p>
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
            
            # 3-3. HTML 생성
            email_body_html += f"""
            <div style="border-left: 4px solid #0066cc; padding-left: 15px; margin: 20px 0;">
                <h3 style="color: #333; margin-bottom: 5px;">
                    <a href="{article['url']}" target="_blank" style="text-decoration: none; color: #0066cc;">
                        {article['title']}
                    </a>
                </h3>
                <p style="color: #999; font-size: 12px; margin: 5px 0;">
                    📌 출처: {article['source']}
                </p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                    <strong>📝 AI 요약:</strong><br>
                    {summary.replace(chr(10), '<br>')}
                </p>
                <p style="color: #666; font-size: 14px;">
                    <strong>🔑 키워드:</strong> {keywords}
                </p>
            </div>
            """
            
            success_count += 1
            print(f"  └─ ✅ 완료 ({success_count}/{len(articles)})")

            # API 호출 제한을 위한 대기
            time.sleep(2)

        except Exception as e:
            print(f"  └─ ❌ 예상치 못한 오류: {e}")
            failed_articles.append((article, str(e)))
            continue

    # ========================================
    # 4. 이메일 본문 마무리
    # ========================================
    email_body_html += f"""
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            수소 뉴스 자동 요약 시스템 v2.0 | 
            성공: {success_count}건 / 실패: {len(failed_articles)}건
        </p>
    </div>
    """

    # ========================================
    # 5. 이메일 발송
    # ========================================
    print(f"\n{'=' * 70}")
    print(f"[단계 3] 이메일 발송")
    print(f"  ✅ 성공: {success_count}건")
    if failed_articles:
        print(f"  ❌ 실패: {len(failed_articles)}건")
        for article, reason in failed_articles[:3]:
            print(f"     - {article['title'][:40]}... ({reason})")
    print(f"{'=' * 70}")

    if success_count > 0:
        print("\n📧 이메일 발송을 시작합니다...")
        send_email(email_body_html)
    else:
        print("\n⚠️  요약에 성공한 기사가 없어 이메일을 발송하지 않습니다.")
    
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


def run_workflow():
    """전체 워크플로우를 실행하는 메인 함수"""
    
    print("=" * 70)
    print(f"🚀 수소 뉴스 브리핑 시스템 v2.0 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

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
        <h1 style="color: #0066cc;">📰 {today_str} 수소 뉴스 브리핑 (v2.0)</h1>
        <p style="color: #666;">총 <strong>{len(articles)}</strong>개의 기사를 수집했습니다.</p>
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
            
            # 3-3. HTML 생성
            email_body_html += f"""
            <div style="border-left: 4px solid #0066cc; padding-left: 15px; margin: 20px 0;">
                <h3 style="color: #333; margin-bottom: 5px;">
                    <a href="{article['url']}" target="_blank" style="text-decoration: none; color: #0066cc;">
                        {article['title']}
                    </a>
                </h3>
                <p style="color: #999; font-size: 12px; margin: 5px 0;">
                    📌 출처: {article['source']}
                </p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                    <strong>📝 AI 요약:</strong><br>
                    {summary.replace(chr(10), '<br>')}
                </p>
                <p style="color: #666; font-size: 14px;">
                    <strong>🔑 키워드:</strong> {keywords}
                </p>
            </div>
            """
            
            success_count += 1
            print(f"  └─ ✅ 완료 ({success_count}/{len(articles)})")

            # API 호출 제한을 위한 대기
            time.sleep(2)

        except Exception as e:
            print(f"  └─ ❌ 예상치 못한 오류: {e}")
            failed_articles.append((article, str(e)))
            continue

    # ========================================
    # 4. 이메일 본문 마무리
    # ========================================
    email_body_html += f"""
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            수소 뉴스 자동 요약 시스템 v2.0 | 
            성공: {success_count}건 / 실패: {len(failed_articles)}건
        </p>
    </div>
    """

    # ========================================
    # 5. 이메일 발송
    # ========================================
    print(f"\n{'=' * 70}")
    print(f"[단계 3] 이메일 발송")
    print(f"  ✅ 성공: {success_count}건")
    if failed_articles:
        print(f"  ❌ 실패: {len(failed_articles)}건")
        for article, reason in failed_articles[:3]:
            print(f"     - {article['title'][:40]}... ({reason})")
    print(f"{'=' * 70}")

    if success_count > 0:
        print("\n📧 이메일 발송을 시작합니다...")
        send_email(email_body_html)
    else:
        print("\n⚠️  요약에 성공한 기사가 없어 이메일을 발송하지 않습니다.")
    
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