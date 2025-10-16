# content_scraper.py (v3.0)
"""
기사 본문 추출 모듈
"""

import requests
from bs4 import BeautifulSoup
import time

def get_and_clean_article_content(url, source_name=""):
    """
    URL에서 기사 본문 추출 및 정제
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 본문 추출 (다양한 선택자 시도)
        content = None
        
        # 방법 1: article 태그
        article = soup.find('article')
        if article:
            content = article.get_text(separator='\n', strip=True)
        
        # 방법 2: div.article-body, div.content 등
        if not content:
            for selector in ['div.article-body', 'div.content', 'div.entry-content', 
                           'div.post-content', 'div.news-content']:
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get_text(separator='\n', strip=True)
                    break
        
        # 방법 3: p 태그들 수집
        if not content:
            paragraphs = soup.find_all('p')
            if len(paragraphs) > 3:
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        # 정제
        if content:
            # 불필요한 공백 제거
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            # 최소 길이 확인
            if len(content) < 100:
                return None
            
            return content[:5000]  # 최대 5000자
        
        return None
        
    except Exception as e:
        print(f"    ⚠️  본문 추출 실패: {e}")
        return None

if __name__ == "__main__":
    # 테스트
    test_url = "https://www.h2news.kr/news/article.html?no=11945"
    content = get_and_clean_article_content(test_url)
    if content:
        print(f"추출 성공: {len(content)}자")
        print(content[:200] + "...")
    else:
        print("추출 실패")