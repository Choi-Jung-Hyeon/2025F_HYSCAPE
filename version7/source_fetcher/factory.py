# source_fetcher/factory.py
"""
Fetcher 생성 팩토리
- config.py 기반 자동 Fetcher 생성
- 팩토리 패턴 사용
- 새 소스 추가 시 코드 수정 불필요
"""

from typing import Dict, List, Type
import logging
from .base_fetcher import BaseSourceFetcher
from .rss_fetcher import RSSFetcher
from .web_scraper_fetcher import WebScraperFetcher
from .naver_fetcher import NaverFetcher
from .google_fetcher import GoogleFetcher

# 로거 설정
logger = logging.getLogger("SourceFetcherFactory")
logger.setLevel(logging.INFO)

class SourceFetcherFactory:
    """
    소스 설정에 따라 적절한 Fetcher를 생성하는 팩토리
    
    사용 예:
        from config import NEWS_SOURCES
        
        # 단일 Fetcher 생성
        fetcher = SourceFetcherFactory.create("월간수소경제", NEWS_SOURCES["월간수소경제"])
        
        # 전체 Manager 생성
        manager = SourceFetcherFactory.create_manager_from_config()
    """
    
    # 타입별 Fetcher 매핑
    _fetchers: Dict[str, Type[BaseSourceFetcher]] = {
        'rss': RSSFetcher,
        'web': WebScraperFetcher,
        'naver': NaverFetcher,
        'google': GoogleFetcher
    }
    
    @classmethod
    def create(cls, source_name: str, source_config: Dict) -> BaseSourceFetcher:
        """
        소스 설정으로부터 Fetcher 인스턴스 생성
        
        Args:
            source_name: 소스 이름 (예: "월간수소경제")
            source_config: config.py의 NEWS_SOURCES 항목
                {
                    'type': 'rss',
                    'url': 'http://...',
                    'status': 'active',
                    ...
                }
        
        Returns:
            BaseSourceFetcher: 생성된 Fetcher 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 소스 타입
        """
        source_type = source_config.get('type')
        
        if source_type not in cls._fetchers:
            raise ValueError(f"지원하지 않는 소스 타입: {source_type}")
        
        fetcher_class = cls._fetchers[source_type]
        
        # 타입별 특수 파라미터 처리
        if source_type == 'rss':
            return fetcher_class(
                source_name=source_name,
                url=source_config['url'],
                **source_config.get('extra', {})
            )
        
        elif source_type == 'web':
            return fetcher_class(
                source_name=source_name,
                url=source_config['url'],
                article_selector=source_config.get('article_selector', ''),
                title_selector=source_config.get('title_selector', ''),
                link_selector=source_config.get('link_selector', ''),
                **source_config.get('extra', {})
            )
        
        elif source_type in ['naver', 'google']:
            # API Fetcher는 특별한 파라미터 불필요
            return fetcher_class(**source_config.get('extra', {}))
        
        else:
            # 기본 생성
            return fetcher_class(
                source_name=source_name,
                url=source_config.get('url', ''),
                **source_config.get('extra', {})
            )
    
    @classmethod
    def register_fetcher(cls, source_type: str, fetcher_class: Type[BaseSourceFetcher]):
        """
        새로운 Fetcher 타입을 동적으로 등록
        
        Args:
            source_type: 타입 이름 (예: "custom")
            fetcher_class: Fetcher 클래스
            
        사용 예:
            SourceFetcherFactory.register_fetcher('custom', CustomFetcher)
        """
        cls._fetchers[source_type] = fetcher_class
        logger.info(f"✅ 새 Fetcher 타입 등록: {source_type} -> {fetcher_class.__name__}")
    
    @classmethod
    def create_manager_from_config(cls) -> 'FetcherManager':
        """
        config.py로부터 FetcherManager 자동 생성
        
        Returns:
            FetcherManager: 모든 active 소스에 대한 Fetcher 포함
        """
        try:
            from config import NEWS_SOURCES
        except ImportError:
            raise ImportError("config.py 파일을 찾을 수 없습니다.")
        
        manager = FetcherManager()
        
        for source_name, source_config in NEWS_SOURCES.items():
            status = source_config.get('status', 'inactive')
            
            if status == 'active':
                try:
                    fetcher = cls.create(source_name, source_config)
                    manager.add_fetcher(fetcher)
                    logger.info(f"✅ {source_name} Fetcher 생성 완료")
                except Exception as e:
                    logger.error(f"❌ {source_name} Fetcher 생성 실패: {e}")
                    continue
        
        logger.info(f"\n📦 총 {len(manager.fetchers)}개 Fetcher 등록 완료")
        return manager


class FetcherManager:
    """
    모든 Fetcher를 관리하는 매니저
    
    사용 예:
        manager = FetcherManager()
        manager.add_fetcher(rss_fetcher)
        manager.add_fetcher(naver_fetcher)
        
        articles = manager.fetch_all_articles(max_per_source=5)
    """
    
    def __init__(self):
        """FetcherManager 초기화"""
        self.fetchers: List[BaseSourceFetcher] = []
        self.logger = logging.getLogger("FetcherManager")
    
    def add_fetcher(self, fetcher: BaseSourceFetcher):
        """
        Fetcher 추가
        
        Args:
            fetcher: BaseSourceFetcher 인스턴스
        """
        self.fetchers.append(fetcher)
    
    def fetch_all_articles(self, max_per_source: int = 5, max_per_keyword: int = 3) -> List[Dict]:
        """
        모든 Fetcher로부터 기사 수집
        
        Args:
            max_per_source: 일반 소스당 최대 기사 수
            max_per_keyword: 키워드 소스당 최대 기사 수
            
        Returns:
            List[Dict]: 중복 제거된 기사 목록
        """
        logger.info("\n" + "=" * 70)
        logger.info("📰 전체 소스 수집 시작")
        logger.info("=" * 70)
        
        all_articles = []
        
        for fetcher in self.fetchers:
            try:
                # API Fetcher (네이버, 구글)는 키워드 필요
                if hasattr(fetcher, 'fetch_articles_by_keywords'):
                    try:
                        from config import NAVER_KEYWORDS, GOOGLE_KEYWORDS
                        from config import MAX_NAVER_PER_KEYWORD, MAX_GOOGLE_PER_KEYWORD
                    except ImportError:
                        logger.warning(f"⚠️ {fetcher.source_name}: 키워드 설정 없음")
                        continue
                    
                    if 'naver' in fetcher.source_name.lower():
                        articles = fetcher.fetch_articles_by_keywords(
                            NAVER_KEYWORDS, 
                            max_per_keyword=MAX_NAVER_PER_KEYWORD
                        )
                    elif 'google' in fetcher.source_name.lower():
                        articles = fetcher.fetch_articles_by_keywords(
                            GOOGLE_KEYWORDS,
                            max_per_keyword=MAX_GOOGLE_PER_KEYWORD
                        )
                    else:
                        continue
                    
                    all_articles.extend(articles)
                
                # 일반 Fetcher (RSS, 웹)
                else:
                    articles = fetcher.fetch_articles(max_per_source)
                    all_articles.extend(articles)
                    
            except Exception as e:
                logger.error(f"❌ {fetcher.source_name} 수집 실패: {e}")
                continue
        
        # 중복 제거 (URL 기준)
        unique_articles = self._remove_duplicates(all_articles)
        
        logger.info(f"\n📊 총 {len(unique_articles)}개 기사 수집 완료 (중복 제거 후)")
        return unique_articles
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        URL 기준으로 중복 제거
        
        Args:
            articles: 기사 목록
            
        Returns:
            List[Dict]: 중복 제거된 기사 목록
        """
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("🧪 SourceFetcherFactory 테스트")
    print("=" * 70)
    
    # 테스트 1: 단일 Fetcher 생성
    print("\n[테스트 1] 단일 Fetcher 생성")
    rss_config = {
        'type': 'rss',
        'url': 'http://www.h2news.kr/rss/S1N1.xml',
        'status': 'active'
    }
    
    fetcher = SourceFetcherFactory.create("월간수소경제", rss_config)
    print(f"✅ 생성됨: {fetcher}")
    
    # 테스트 2: FetcherManager 생성
    print("\n[테스트 2] FetcherManager 생성")
    manager = SourceFetcherFactory.create_manager_from_config()
    print(f"✅ {len(manager.fetchers)}개 Fetcher 등록됨")
    
    # 테스트 3: 전체 기사 수집
    print("\n[테스트 3] 전체 기사 수집")
    articles = manager.fetch_all_articles(max_per_source=3, max_per_keyword=2)
    
    print(f"\n✅ 총 {len(articles)}개 기사 수집")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. [{article['source']}] {article['title'][:50]}...")