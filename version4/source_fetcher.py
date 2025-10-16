# source_fetcher.py (v3.0)
"""
뉴스 소스에서 기사 목록을 수집하는 모듈
- 웹 크롤링 (월간수소경제 등)
- RSS 피드 (Hydrogen Central 등)
- 네이버 뉴스 검색
- 구글 뉴스 검색 (NEW!)
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import time
from datetime import datetime
from config import (
    NEWS_SOURCES, 
    NAVER_KEYWORDS, 
    GOOGLE_KEYWORDS,
    MAX_ARTICLES_PER_SOURCE,
    MAX_NAVER_PER_KEYWORD,
    MAX_GOOGLE_PER_KEYWORD,
    FAILED_SOURCES_LOG
)

# ========================================
# 실패한 소스 로깅
# ========================================
def log_failed_source(source_name, reason):
    """실패한 소스를 로그 파일에 기록"""
    with open(FAILED_SOURCES_LOG, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {source_name}: {reason}\n")
    print(f"  ⚠️  {source_name} 실패: {reason}")

# ========================================
# 1. 웹 스크래핑 Fetcher
# ========================================
class WebFetcher:
    """일반 웹사이트에서 기사 목록 수집"""
    
    def __init__(self, source_name, url):
        self.source_name = source_name
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_articles(self, limit=5):
        """기사 목록 수집"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # 월간수소경제 전용 파싱
            if "h2news.kr" in self.url:
                articles = self._parse_h2news(soup)
            
            # H2 View 파싱
            elif "h2-view.com" in self.url:
                articles = self._parse_h2view(soup)
            
            # 기타 사이트 일반 파싱
            else:
                articles = self._parse_generic(soup)
            
            articles = articles[:limit]
            print(f"  ✅ {self.source_name}: {len(articles)}개 수집")
            return articles
            
        except requests.exceptions.HTTPError as e:
            log_failed_source(self.source_name, f"HTTP {e.response.status_code}")
            return []
        except Exception as e:
            log_failed_source(self.source_name, str(e))
            return []
    
    def _parse_h2news(self, soup):
        """월간수소경제 파싱"""
        articles = []
        for item in soup.select('div.card-body'):
            try:
                title_tag = item.select_one('a.card-title')
                if title_tag:
                    title = title_tag.text.strip()
                    url = "https://www.h2news.kr" + title_tag['href']
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': self.source_name
                    })
            except:
                continue
        return articles
    
    def _parse_h2view(self, soup):
        """H2 View 파싱"""
        articles = []
        for item in soup.select('article.post'):
            try:
                title_tag = item.select_one('h2.entry-title a')
                if title_tag:
                    title = title_tag.text.strip()
                    url = title_tag['href']
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': self.source_name
                    })
            except:
                continue
        return articles
    
    def _parse_generic(self, soup):
        """일반 사이트 파싱"""
        articles = []
        
        # article 태그 찾기
        for item in soup.find_all(['article', 'div'], class_=['post', 'article', 'news-item'])[:10]:
            try:
                title_tag = item.find(['h1', 'h2', 'h3', 'h4'], class_=['title', 'headline'])
                link_tag = title_tag.find('a') if title_tag else item.find('a')
                
                if link_tag:
                    title = link_tag.text.strip()
                    url = link_tag.get('href', '')
                    
                    if not url.startswith('http'):
                        url = self.url.rstrip('/') + '/' + url.lstrip('/')
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': self.source_name
                    })
            except:
                continue
        
        return articles

# ========================================
# 2. RSS Fetcher
# ========================================
class RSSFetcher:
    """RSS 피드에서 기사 목록 수집"""
    
    def __init__(self, source_name, url):
        self.source_name = source_name
        self.url = url
    
    def fetch_articles(self, limit=5):
        """RSS 피드에서 기사 수집"""
        try:
            feed = feedparser.parse(self.url)
            
            if not feed.entries:
                log_failed_source(self.source_name, "No entries in RSS feed")
                return []
            
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.get('title', 'No title'),
                    'url': entry.get('link', ''),
                    'source': self.source_name
                })
            
            print(f"  ✅ {self.source_name}: {len(articles)}개 수집")
            return articles
            
        except Exception as e:
            log_failed_source(self.source_name, str(e))
            return []

# ========================================
# 3. 네이버 뉴스 Fetcher
# ========================================
class NaverNewsFetcher:
    """네이버 뉴스 검색"""
    
    def __init__(self):
        self.source_name = "네이버뉴스"
        self.base_url = "https://search.naver.com/search.naver"
    
    def fetch_articles(self, keywords, max_per_keyword=3):
        """키워드별 뉴스 검색"""
        all_articles = []
        
        for keyword in keywords:
            try:
                params = {
                    'where': 'news',
                    'query': keyword,
                    'sort': '1',  # 최신순
                    'start': 1
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
                }
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # 네이버 뉴스 HTML 구조 (2025년 버전)
                # 방법 1: news_area 클래스
                news_items = soup.select('div.news_area')
                
                if not news_items:
                    # 방법 2: 다른 선택자 시도
                    news_items = soup.select('li.bx')
                
                for item in news_items[:max_per_keyword]:
                    try:
                        # 제목과 URL 추출
                        title_tag = item.select_one('a.news_tit')
                        if not title_tag:
                            title_tag = item.select_one('a[class*="news"]')
                        
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                            url = title_tag.get('href', '')
                            
                            if title and url:
                                articles.append({
                                    'title': title,
                                    'url': url,
                                    'source': f"{self.source_name}({keyword})"
                                })
                    except:
                        continue
                
                all_articles.extend(articles)
                
                if articles:
                    print(f"  ✅ 네이버({keyword}): {len(articles)}개")
                else:
                    print(f"  ⚠️  네이버({keyword}): 0개 (HTML 구조 변경 가능성)")
                
                time.sleep(1)  # 요청 간격 (네이버 차단 방지)
                
            except Exception as e:
                log_failed_source(f"네이버({keyword})", str(e))
        
        return all_articles

# ========================================
# 4. 구글 뉴스 Fetcher (NEW!)
# ========================================
class GoogleNewsFetcher:
    """구글 뉴스 검색"""
    
    def __init__(self):
        self.source_name = "구글뉴스"
        self.base_url = "https://news.google.com/rss/search"
    
    def fetch_articles(self, keywords, max_per_keyword=3):
        """키워드별 구글 뉴스 RSS 검색"""
        all_articles = []
        
        for keyword in keywords:
            try:
                # 구글 뉴스 RSS URL
                params = {
                    'q': keyword,
                    'hl': 'en-US',
                    'gl': 'US',
                    'ceid': 'US:en'
                }
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                # RSS 파싱
                feed = feedparser.parse(response.content)
                articles = []
                
                for entry in feed.entries[:max_per_keyword]:
                    # 구글 뉴스 URL에서 실제 기사 URL 추출
                    actual_url = self._extract_actual_url(entry.get('link', ''))
                    
                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'url': actual_url,
                        'source': f"{self.source_name}({keyword})"
                    })
                
                all_articles.extend(articles)
                print(f"  ✅ 구글({keyword}): {len(articles)}개")
                time.sleep(0.5)  # 요청 간격
                
            except Exception as e:
                log_failed_source(f"구글({keyword})", str(e))
        
        return all_articles
    
    def _extract_actual_url(self, google_url):
        """
        구글 뉴스 redirect URL에서 실제 기사 URL 추출
        예: https://news.google.com/rss/articles/... → 실제 URL
        """
        try:
            # redirect 따라가기
            response = requests.head(google_url, allow_redirects=True, timeout=5)
            return response.url
        except:
            # 실패 시 원본 URL 반환
            return google_url

# ========================================
# 5. Fetcher Manager
# ========================================
class FetcherManager:
    """모든 Fetcher를 관리하는 매니저"""
    
    def __init__(self):
        self.fetchers = []
    
    def add_fetcher(self, fetcher):
        """Fetcher 추가"""
        self.fetchers.append(fetcher)
    
    def fetch_all_articles(self, limit_per_source=5):
        """모든 소스에서 기사 수집"""
        all_articles = []
        
        for fetcher in self.fetchers:
            if hasattr(fetcher, 'fetch_articles'):
                # NaverNewsFetcher, GoogleNewsFetcher는 keywords 인자 필요
                if isinstance(fetcher, NaverNewsFetcher):
                    articles = fetcher.fetch_articles(
                        NAVER_KEYWORDS, 
                        MAX_NAVER_PER_KEYWORD
                    )
                elif isinstance(fetcher, GoogleNewsFetcher):
                    articles = fetcher.fetch_articles(
                        GOOGLE_KEYWORDS,
                        MAX_GOOGLE_PER_KEYWORD
                    )
                else:
                    articles = fetcher.fetch_articles(limit_per_source)
                
                all_articles.extend(articles)
        
        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        print(f"\n📊 총 {len(unique_articles)}개 기사 수집 완료 (중복 제거 후)")
        return unique_articles

# ========================================
# 6. Config 기반 Fetcher 생성
# ========================================
def create_fetchers_from_config():
    """config.py 기반으로 Fetcher Manager 생성"""
    manager = FetcherManager()
    
    # NEWS_SOURCES에서 Fetcher 생성
    for source_name, info in NEWS_SOURCES.items():
        if info.get('status') == 'active' or info.get('status') == 'testing':
            if info['type'] == 'web':
                manager.add_fetcher(WebFetcher(source_name, info['url']))
            elif info['type'] == 'rss':
                manager.add_fetcher(RSSFetcher(source_name, info['url']))
    
    # 네이버 뉴스 추가
    manager.add_fetcher(NaverNewsFetcher())
    
    # 구글 뉴스 추가 (NEW!)
    manager.add_fetcher(GoogleNewsFetcher())
    
    return manager

# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Source Fetcher v3.0 테스트")
    print("=" * 70)
    
    manager = create_fetchers_from_config()
    articles = manager.fetch_all_articles(limit_per_source=MAX_ARTICLES_PER_SOURCE)
    
    print(f"\n✅ 총 {len(articles)}개 기사 수집")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. [{article['source']}] {article['title'][:50]}...")