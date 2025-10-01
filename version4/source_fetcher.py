# source_fetcher.py

import feedparser
# from config import RSS_URL, KEYWORD
from config import RSS_URL

def fetch_articles_from_rss():
    print(f"월간수소경제 피드를 수집합니다.")
    
    feed = feedparser.parse(RSS_URL)
    
    articles = [{'title': entry.title, 'url': entry.link} for entry in feed.entries]
    
    print(f"총 {len(articles)}개의 기사를 찾았습니다.")
    return articles

# 단위 테스트 코드
if __name__ == '__main__':
    print("--- source_fetcher.py 단위 테스트 시작 ---")
    
    # 함수가 정상적으로 작동하는지 테스트합니다.
    test_articles = fetch_articles_from_rss()
    
    # 상위 5개 기사만 출력하여 확인합니다.
    for i, article in enumerate(test_articles[:5]):
        print(f"  [{i+1}] {article['title']}")
        print(f"      링크: {article['url']}")
        
    print("--- 단위 테스트 종료 ---")