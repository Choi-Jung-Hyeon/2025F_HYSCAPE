# source_fetcher.py (v2.1 - Enhanced)
"""
다중 뉴스 소스를 효율적으로 관리하고 기사 URL을 수집하는 모듈
- RSS 피드 수집
- 웹페이지 크롤링
- 네이버 뉴스 검색
- 접속 불가능한 소스 진단
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import feedparser
import requests
from bs4 import BeautifulSoup
import time


class NewsFetcher(ABC):
    """
    모든 뉴스 소스 Fetcher의 추상 베이스 클래스
    """
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.status = "Unknown"  # 상태: Success, Failed, Partial
        self.error_message = None
    
    @abstractmethod
    def fetch_articles(self) -> List[Dict[str, str]]:
        """뉴스 소스로부터 기사 목록을 가져오는 메서드"""
        pass


class RSSFetcher(NewsFetcher):
    """RSS 피드를 통해 기사를 수집하는 Fetcher"""
    
    def __init__(self, source_name: str, rss_url: str):
        super().__init__(source_name)
        self.rss_url = rss_url
    
    def fetch_articles(self) -> List[Dict[str, str]]:
        """RSS 피드를 파싱하여 기사 목록을 반환"""
        print(f"[{self.source_name}] RSS 피드를 수집합니다: {self.rss_url}")
        
        try:
            # User-Agent 추가로 차단 방지
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # requests로 먼저 가져온 후 feedparser에 전달
            response = requests.get(self.rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"  ⚠️ RSS 피드 파싱 경고: {feed.get('bozo_exception', '알 수 없는 오류')}")
                self.status = "Partial"
            
            if not feed.entries:
                print(f"  ❌ RSS 피드가 비어 있습니다.")
                self.status = "Failed"
                self.error_message = "Empty feed"
                return []
            
            articles = []
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', '제목 없음'),
                    'url': entry.get('link', ''),
                    'source': self.source_name
                }
                if article['url']:  # URL이 있는 경우만 추가
                    articles.append(article)
            
            print(f"  ✅ {len(articles)}개의 기사를 찾았습니다.")
            self.status = "Success"
            return articles
            
        except requests.exceptions.Timeout:
            print(f"  ❌ 타임아웃: 서버 응답이 없습니다.")
            self.status = "Failed"
            self.error_message = "Timeout"
            return []
            
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 연결 오류: 네트워크 문제 또는 잘못된 URL")
            self.status = "Failed"
            self.error_message = "Connection Error"
            return []
            
        except Exception as e:
            print(f"  ❌ RSS 피드 수집 중 오류 발생: {e}")
            self.status = "Failed"
            self.error_message = str(e)
            return []


class WebPageFetcher(NewsFetcher):
    """웹페이지를 크롤링하여 기사를 수집하는 Fetcher"""
    
    def __init__(self, source_name: str, page_url: str, selectors: Dict[str, str]):
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
            self.status = "Success"
            return articles
            
        except Exception as e:
            print(f"  ❌ 웹페이지 크롤링 중 오류 발생: {e}")
            self.status = "Failed"
            self.error_message = str(e)
            return []


class NaverNewsFetcher(NewsFetcher):
    """네이버 뉴스 검색을 통해 기사를 수집하는 Fetcher"""
    
    def __init__(self, keyword: str):
        super().__init__(f"네이버뉴스({keyword})")
        self.keyword = keyword
        self.search_url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1"  # sort=1: 최신순
    
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
            self.status = "Success"
            return articles
            
        except Exception as e:
            print(f"  ❌ 네이버 뉴스 검색 중 오류 발생: {e}")
            self.status = "Failed"
            self.error_message = str(e)
            return []


class SourceManager:
    """여러 뉴스 소스를 통합 관리하는 클래스"""
    
    def __init__(self):
        self.fetchers: List[NewsFetcher] = []
    
    def add_fetcher(self, fetcher: NewsFetcher):
        """Fetcher 추가"""
        self.fetchers.append(fetcher)
    
    def fetch_all_articles(self, limit_per_source: int = None) -> List[Dict[str, str]]:
        """
        모든 등록된 소스로부터 기사를 수집
        
        Args:
            limit_per_source: 소스당 가져올 최대 기사 수
        
        Returns:
            모든 소스의 기사를 합친 리스트
        """
        all_articles = []
        failed_sources = []
        
        print("\n" + "="*60)
        print("뉴스 소스 수집을 시작합니다")
        print("="*60)
        
        for fetcher in self.fetchers:
            articles = fetcher.fetch_articles()
            
            if fetcher.status == "Failed":
                failed_sources.append({
                    'source': fetcher.source_name,
                    'error': fetcher.error_message
                })
            
            if limit_per_source and len(articles) > limit_per_source:
                articles = articles[:limit_per_source]
                print(f"  📌 소스당 제한으로 {limit_per_source}개만 선택합니다.")
            
            all_articles.extend(articles)
            time.sleep(1)  # 과도한 요청 방지
        
        print("\n" + "="*60)
        print(f"총 {len(all_articles)}개의 기사를 수집했습니다")
        
        if failed_sources:
            print("\n⚠️ 접속 실패한 소스:")
            for failed in failed_sources:
                print(f"  - {failed['source']}: {failed['error']}")
        
        print("="*60 + "\n")
        
        return all_articles


def create_fetchers_from_config() -> SourceManager:
    """
    config.py의 NEWS_SOURCES를 읽어서 SourceManager를 생성
    네이버 뉴스 검색도 함께 추가
    """
    from config import NEWS_SOURCES, NAVER_NEWS_KEYWORDS
    
    manager = SourceManager()
    
    # RSS 소스 추가
    for source_name, rss_url in NEWS_SOURCES.items():
        manager.add_fetcher(
            RSSFetcher(source_name=source_name, rss_url=rss_url)
        )
    
    # 네이버 뉴스 검색 추가
    for keyword in NAVER_NEWS_KEYWORDS:
        manager.add_fetcher(
            NaverNewsFetcher(keyword=keyword)
        )
    
    return manager


# ============================================================
# 모듈 단위 테스트
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("source_fetcher.py (v2.1) 단위 테스트")
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