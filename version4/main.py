# main.py
import time
from datetime import datetime

# from config import KEYWORD
from source_fetcher import fetch_articles_from_rss
from content_scraper import get_and_clean_article_content
from summarizer import get_summary_and_keywords
from notifier import send_email
from h2korea_fetcher import fetch_h2korea_publications

def run_workflow():
    print("="*50)
    print(f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) - 뉴스 브리핑 시스템 시작")
    print("="*50)

    # 1. n8n: RSS Feed Read
    articles = fetch_articles_from_rss()

    if not articles:
        print("처리할 새로운 기사가 없습니다. 시스템을 종료합니다.")
        return

    today_str = datetime.now().strftime('%Y-%m-%d')
    email_body_html = f"<h1>📰 {today_str} 오늘의 월간수소경제 브리핑</h1>"
    success_count = 0

    # 2. n8n: Loop Over Items
    for i, article in enumerate(articles[:5]): 
        print(f"\n[{i+1}/{len(articles[:5])}] '{article['title']}' 기사 처리 시작...")
        
        # 3. n8n: HTTP Request + Content Processor
        # print(article['url'])
        content = get_and_clean_article_content(article['url'])
        # print(content)
        
        if not content:
            print("  -> ❗️ 본문 추출에 실패하여 다음 기사로 넘어갑니다.")
            continue

        # 4. n8n: OpenAI Chat Model
        summary, keywords = get_summary_and_keywords(article['title'], content)
        
        if not summary:
            print("  -> ❗️ AI 요약에 실패하여 다음 기사로 넘어갑니다.")
            continue
            
        # 5. 이메일 본문에 추가할 HTML 내용 생성
        email_body_html += f"""
        <hr>
        <h3><a href="{article['url']}" target="_blank">{article['title']}</a></h3>
        <p><b>[AI 요약]</b><br>{summary.replace('\n', '<br>')}</p>
        <p><b>[키워드]</b><br>{keywords}</p>
        """
        success_count += 1
        print("  -> ✅ 요약 및 HTML 생성을 완료했습니다.")

        # 6. n8n: Wait Node
        time.sleep(2)

    # 7. 최종 결과를 이메일로 발송
    if success_count > 0:
        print(f"\n총 {success_count}개의 기사 요약을 완료했습니다. 이메일을 발송합니다.")
        send_email(email_body_html)
    else:
        print("\n요약에 성공한 기사가 없어 이메일을 발송하지 않습니다.")
        
    print("\n" + "="*50)
    print("모든 작업을 완료했습니다.")
    print("="*50)


if __name__ == "__main__":
    run_workflow()