# source_fetcher/naver_fetcher.py
"""
네이버 뉴스 검색 Fetcher
- 키워드 기반 네이버 뉴스 검색
- HTML 파싱 방식 (API 키 불필요)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote
from .api_fetcher import APIFetcher

class NaverFetcher(APIFetcher):
    """
    네이버 뉴스 검색 (HTML 파싱 방식)
    
    사용 예:
        from config import NAVER_KEYWORDS, MAX_NAVER_PER_KEYWORD
        fetcher = NaverFetcher()
        articles = fetcher.fetch_articles_by_keywords(NAVER_KEYWORDS, MAX_NAVER_PER_KEYWORD)
    """
    
    def __init__(self, **kwargs):
        """
        네이버 뉴스 Fetcher 초기화
        """
        super().__init__(source_name="네이버뉴스", **kwargs)
        self.base_url = "https://search.naver.com/search.naver"
    
    def fetch_articles_by_keywords(self, keywords: List[str], max_per_keyword: int = 3) -> List[Dict]:
        """
        키워드 목록으로 네이버 뉴스 검색
        
        Args:
            keywords: 검색 키워드 목록
            max_per_keyword: 키워드당 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        all_articles = []
        
        for keyword in keywords:
            try:
                self.logger.info(f"🔍 네이버 검색: '{keyword}'")
                
                # 검색 파라미터
                params = {
                    'where': 'news',
                    'query': keyword,
                    'sort': '1',  # 최신순
                    'start': 1
                }
                
                # 헤더 설정 (봇 차단 방지)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
                }
                
                response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                news_items = soup.select('.news_area')[:max_per_keyword]
                
                if not news_items:
                    self.logger.warning(f"⚠️ '{keyword}' 검색 결과 없음")
                    continue
                
                # 기사 정보 추출
                for item in news_items:
                    try:
                        # 제목과 링크
                        title_elem = item.select_one('.news_tit')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        # 언론사
                        press_elem = item.select_one('.info.press')
                        press = press_elem.get_text(strip=True) if press_elem else ''
                        
                        # 발행일시
                        date_elem = item.select_one('.info_group .info')
                        published = date_elem.get_text(strip=True) if date_elem else ''
                        
                        article = {
                            'title': title,
                            'url': url,
                            'published': published,
                            'source': f"{self.source_name}({keyword})",
                            'press': press,
                            'keyword': keyword
                        }
                        
                        if self.validate_article(article):
                            all_articles.append(article)
                            
                    except Exception as e:
                        self.logger.debug(f"기사 파싱 실패: {e}")
                        continue
                
                self.logger.info(f"  ✅ '{keyword}': {len([a for a in all_articles if a.get('keyword') == keyword])}개")
                
            except Exception as e:
                self.logger.error(f"❌ '{keyword}' 검색 실패: {e}")
                self.log_error(e)
                continue
        
        self.log_success(len(all_articles))
        return all_articles


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("🧪 NaverFetcher 테스트")
    print("=" * 70)
    
    # 테스트 키워드
    test_keywords = ["수소", "수전해", "연료전지"]
    
    fetcher = NaverFetcher()
    articles = fetcher.fetch_articles_by_keywords(test_keywords, max_per_keyword=2)
    
    print(f"\n✅ 총 {len(articles)}개 기사 수집")
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article['keyword']}] {article['title'][:60]}...")
        print(f"   언론사: {article.get('press', 'N/A')}")
        print(f"   URL: {article['url']}")
        print()