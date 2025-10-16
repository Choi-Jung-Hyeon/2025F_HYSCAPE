# source_fetcher.py (v2.0)
"""
다중 뉴스 소스를 효율적으로 관리하고 기사 URL을 수집하는 모듈
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import feedparser
import requests
from bs4 import BeautifulSoup


class NewsFetcher(ABC):
    """
    모든 뉴스 소스 Fetcher의 추상 베이스 클래스
    새로운 뉴스 소스를 추가할 때 이 클래스를 상속받아 구현합니다.
    """
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, str]]:
        """
        뉴스 소스로부터 기사 목록을 가져오는 메서드
        
        Returns:
            List[Dict]: 각 기사는 {'title': str, 'url': str, 'source': str} 형식
        """
        pass


class RSSFetcher(NewsFetcher):
    """
    RSS 피드를 통해 기사를 수집하는 Fetcher
    """
    
    def __init__(self, source_name: str, rss_url: str):
        super().__init__(source_name)
        self.rss_url = rss_url
    
    def fetch_articles(self) -> List[Dict[str, str]]:
        """RSS 피드를 파싱하여 기사 목록을 반환"""
        print(f"[{self.source_name}] RSS 피드를 수집합니다: {self.rss_url}")
        
        try:
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:  # 피드 파싱 오류 체크
                print(f"  ⚠️ RSS 피드 파싱 중 경고가 발생했습니다: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', '제목 없음'),
                    'url': entry.get('link', ''),
                    'source': self.source_name
                }
                articles.append(article)
            
            print(f"  ✅ {len(articles)}개의 기사를 찾았습니다.")
            return articles
            
        except Exception as e:
            print(f"  ❌ RSS 피드 수집 중 오류 발생: {e}")
            return []


class WebPageFetcher(NewsFetcher):
    """
    웹페이지를 크롤링하여 기사를 수집하는 Fetcher
    RSS를 제공하지 않는 사이트를 위한 클래스
    """
    
    def __init__(self, source_name: str, page_url: str, selectors: Dict[str, str]):
        """
        Args:
            source_name: 뉴스 소스 이름
            page_url: 크롤링할 웹페이지 URL
            selectors: CSS 선택자 딕셔너리
                - 'container': 기사 목록을 감싸는 컨테이너
                - 'title': 기사 제목 선택자
                - 'link': 기사 링크 선택자
        """
        super().__init__(source_name)
        self.page_url = page_url
        self.selectors = selectors
    
    def fetch_articles(self) -> List[Dict[str, str]]:
        """웹페이지를 크롤링하여 기사 목록을 반환"""
        print(f"[{self.source_name}] 웹페이지를 크롤링합니다: {self.page_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.page_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 컨테이너 선택자가 있으면 해당 영역 내에서만 검색
            if self.selectors.get('container'):
                containers = soup.select(self.selectors['container'])
            else:
                containers = [soup]
            
            for container in containers:
                # 제목과 링크 추출
                title_elem = container.select_one(self.selectors.get('title', 'a'))
                link_elem = container.select_one(self.selectors.get('link', 'a'))
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    
                    # 상대 경로를 절대 경로로 변환
                    if url and not url.startswith('http'):
                        from urllib.parse import urljoin
                        url = urljoin(self.page_url, url)
                    
                    if title and url:
                        article = {
                            'title': title,
                            'url': url,
                            'source': self.source_name
                        }
                        articles.append(article)
            
            print(f"  ✅ {len(articles)}개의 기사를 찾았습니다.")
            return articles
            
        except Exception as e:
            print(f"  ❌ 웹페이지 크롤링 중 오류 발생: {e}")
            return []


class NaverNewsFetcher(NewsFetcher):
    """
    네이버 뉴스 검색을 통해 기사를 수집하는 Fetcher
    특정 키워드로 최신 뉴스를 검색합니다
    """
    
    def __init__(self, keyword: str):
        super().__init__(f"네이버뉴스({keyword})")
        self.keyword = keyword
        self.search_url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    
    def fetch_articles(self) -> List[Dict[str, str]]:
        """네이버 뉴스 검색 결과를 크롤링하여 기사 목록을 반환"""
        print(f"[{self.source_name}] 네이버 뉴스를 검색합니다: {self.search_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # 네이버 뉴스 검색 결과 선택자
            news_items = soup.select('.news_tit')
            
            for item in news_items[:10]:  # 최대 10개
                title = item.get_text(strip=True)
                url = item.get('href', '')
                
                if title and url:
                    article = {
                        'title': title,
                        'url': url,
                        'source': self.source_name
                    }
                    articles.append(article)
            
            print(f"  ✅ {len(articles)}개의 기사를 찾았습니다.")
            return articles
            
        except Exception as e:
            print(f"  ❌ 네이버 뉴스 검색 중 오류 발생: {e}")
            return []


class SourceManager:
    """
    여러 뉴스 소스를 통합 관리하는 클래스
    """
    
    def __init__(self):
        self.fetchers: List[NewsFetcher] = []
    
    def add_fetcher(self, fetcher: NewsFetcher):
        """Fetcher 추가"""
        self.fetchers.append(fetcher)
    
    def fetch_all_articles(self, limit_per_source: int = None) -> List[Dict[str, str]]:
        """
        모든 등록된 소스로부터 기사를 수집
        
        Args:
            limit_per_source: 소스당 가져올 최대 기사 수 (None이면 제한 없음)
        
        Returns:
            모든 소스의 기사를 합친 리스트
        """
        all_articles = []
        
        print("\n" + "="*60)
        print("뉴스 소스 수집을 시작합니다")
        print("="*60)
        
        for fetcher in self.fetchers:
            articles = fetcher.fetch_articles()
            
            if limit_per_source and len(articles) > limit_per_source:
                articles = articles[:limit_per_source]
                print(f"  📌 소스당 제한으로 {limit_per_source}개만 선택합니다.")
            
            all_articles.extend(articles)
        
        print("\n" + "="*60)
        print(f"총 {len(all_articles)}개의 기사를 수집했습니다")
        print("="*60 + "\n")
        
        return all_articles


# ============================================================
# 실제 사용 예시 및 설정
# ============================================================

def create_fetchers_from_config() -> SourceManager:
    """
    config.py의 NEWS_SOURCES를 읽어서 SourceManager를 생성
    """
    from config import NEWS_SOURCES
    
    manager = SourceManager()
    
    for source_name, rss_url in NEWS_SOURCES.items():
        manager.add_fetcher(
            RSSFetcher(source_name=source_name, rss_url=rss_url)
        )
    
    return manager


# ============================================================
# 모듈 단위 테스트
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("source_fetcher.py (v2.0) 단위 테스트")
    print("=" * 60)
    
    # SourceManager 생성 및 Fetcher 등록
    manager = create_fetchers_from_config()
    
    # 모든 소스에서 기사 수집 (각 소스당 최대 3개)
    articles = manager.fetch_all_articles(limit_per_source=3)
    
    # 결과 출력
    print("\n📰 수집된 기사 목록:")
    print("-" * 60)
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    출처: {article['source']}")
        print(f"    링크: {article['url'][:80]}...")
    
    print("\n" + "=" * 60)
    print("단위 테스트 완료")
    print("=" * 60)