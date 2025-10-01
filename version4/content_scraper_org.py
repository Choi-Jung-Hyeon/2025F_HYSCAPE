# 파일명: content_scraper.py

import requests
from bs4 import BeautifulSoup
import re
import time

def get_and_clean_article_content(url):
    for attempt in range(3):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup)
            paragraphs = soup.find_all('p')
            # print(paragraphs)
            
            content_list = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text.split()) > 10:
                    content_list.append(text)
         
            clean_content = ' '.join(content_list)
            
            clean_content = re.sub(r'[^\w\s가-힣]', '', clean_content)
            # print(clean_content)   
            return clean_content

        except Exception as e:
            print(f"  [오류] 본문 추출 실패 (시도 {attempt + 1}/3): {url}")
            print(f"  오류 내용: {e}")
            time.sleep(2)
            
    return None

# 단위 테스트 코드
if __name__ == '__main__':
    print("--- content_scraper.py 단위 테스트 시작 ---")
    
    # 실제 뉴스 기사 URL로 테스트합니다.
    test_url = "https://www.h2news.kr/news/articleView.html?idxno=11140"
    
    content = get_and_clean_article_content(test_url)
    
    if content:
        print("\n[추출된 본문 내용 (일부)]")
        print(content[:400] + "...")
    else:
        print("\n본문 내용을 추출하는 데 실패했습니다.")
        
    print("\n--- 단위 테스트 종료 ---")