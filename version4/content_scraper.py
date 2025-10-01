# content_scraper.py (v2 - newspaper3k)

from newspaper import Article
import time

def get_and_clean_article_content(url):
    for attempt in range(2):
        try:
            article = Article(url, language='ko')
            
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                return article.text
            else:
                print(f"  [정보] 기사 내용이 너무 짧아 건너뜁니다.")
                break

        except Exception as e:
            print(f"  [오류] 본문 추출 실패 (시도 {attempt + 1}/2): {url}")
            print(f"  오류 내용: {e}")
            time.sleep(2)
            
    return None

# 단위 테스트 코드
if __name__ == '__main__':
    print("--- content_scraper.py (v2) 단위 테스트 시작 ---")
    
    test_urls = [
        "https://www.e-kea.com/news/articleView.html?idxno=36659",
        "http://www.en-e.kr/news/articleView.html?idxno=21149", #
        "https://www.news1.kr/articles/?5246757"
    ]
    
    for test_url in test_urls:
        print(f"\n[테스트 URL]: {test_url}")
        content = get_and_clean_article_content(test_url)
        
        if content:
            print("[추출 성공 ✅]")
            print(content[:200] + "...")
        else:
            print("[추출 실패 ❗️]")
        
    print("\n--- 단위 테스트 종료 ---")