# source_fetcher/google_fetcher.py
"""
구글 뉴스 검색 Fetcher
- 키워드 기반 구글 뉴스 검색
- HTML 파싱 방식 (API 키 불필요)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote
from .api_fetcher import APIFetcher

class GoogleFetcher(APIFetcher):
    """
    구글 뉴스 검색 (HTML 파싱 방식)
    
    사용 예:
        from config import GOOGLE_KEYWORDS, MAX_GOOGLE_PER_KEYWORD
        fetcher = GoogleFetcher()
        articles = fetcher.fetch_articles_by_keywords(GOOGLE_KEYWORDS, MAX_GOOGLE_PER_KEYWORD)
    """
    
    def __init__(self, **kwargs):
        """
        구글 뉴스 Fetcher 초기화
        """
        super().__init__(source_name="구글뉴스", **kwargs)
        self.base_url = "https://www.google.com/search"
    
    def fetch_articles_by_keywords(self, keywords: List[str], max_per_keyword: int = 3) -> List[Dict]:
        """
        키워드 목록으로 구글 뉴스 검색
        
        Args:
            keywords: 검색 키워드 목록
            max_per_keyword: 키워드당 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        all_articles = []
        
        for keyword in keywords:
            try:
                self.logger.info(f"🔍 구글 검색: '{keyword}'")
                
                # 검색 파라미터 (뉴스 탭)
                params = {
                    'q': keyword,
                    'tbm': 'nws',  # 뉴스 탭
                    'hl': 'ko',     # 한국어
                    'gl': 'kr',     # 한국 지역
                    'num': max_per_keyword  # 결과 개수
                }
                
                # 헤더 설정 (봇 차단 방지)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.google.com/'
                }
                
                response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 구글 뉴스 결과 추출 (여러 선택자 시도)
                news_items = []
                
                # 선택자 1: 일반적인 뉴스 결과
                news_items = soup.select('div.SoaBEf')[:max_per_keyword]
                
                # 선택자 2: 대체 선택자
                if not news_items:
                    news_items = soup.select('div[data-sokoban-container]')[:max_per_keyword]
                
                # 선택자 3: 기본 검색 결과
                if not news_items:
                    news_items = soup.select('div.g')[:max_per_keyword]
                
                if not news_items:
                    self.logger.warning(f"⚠️ '{keyword}' 검색 결과 없음")
                    continue
                
                # 기사 정보 추출
                for item in news_items:
                    try:
                        # 제목과 링크 추출 (여러 방법 시도)
                        title_elem = item.select_one('div[role="heading"]') or \
                                   item.select_one('h3') or \
                                   item.select_one('.n0jPhd')
                        
                        link_elem = item.select_one('a')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        
                        # 구글 리다이렉트 URL 정리
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        # 발행일시 추출
                        date_elem = item.select_one('.OSrXXb') or \
                                  item.select_one('.LfVVr') or \
                                  item.select_one('span.f')
                        published = date_elem.get_text(strip=True) if date_elem else ''
                        
                        # 언론사 추출
                        source_elem = item.select_one('.CEMjEf') or \
                                    item.select_one('.NUnG9d span')
                        press = source_elem.get_text(strip=True) if source_elem else ''
                        
                        article = {
                            'title': title,
                            'url': url,
                            'published': published,
                            'source': f"{self.source_name}({keyword})",
                            'press': press,
                            'keyword': keyword
                        }
                        
                        if self.validate_article(article) and not url.startswith('/search'):
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
    print("🧪 GoogleFetcher 테스트")
    print("=" * 70)
    
    # 테스트 키워드
    test_keywords = ["hydrogen fuel cell", "water electrolysis", "green hydrogen"]
    
    fetcher = GoogleFetcher()
    articles = fetcher.fetch_articles_by_keywords(test_keywords, max_per_keyword=2)
    
    print(f"\n✅ 총 {len(articles)}개 기사 수집")
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article['keyword']}] {article['title'][:60]}...")
        print(f"   언론사: {article.get('press', 'N/A')}")
        print(f"   URL: {article['url']}")
        print()