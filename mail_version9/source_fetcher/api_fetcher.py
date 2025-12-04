# source_fetcher/api_fetcher.py
"""
API 기반 Fetcher 추상 클래스
- 네이버 뉴스, 구글 뉴스 등의 공통 부모 클래스
- 키워드 기반 검색 API 공통 로직
"""

from abc import abstractmethod
from typing import List, Dict
from .base_fetcher import BaseSourceFetcher

class APIFetcher(BaseSourceFetcher):
    """
    검색 API 기반 Fetcher의 추상 클래스
    
    네이버, 구글 등의 키워드 검색 API를 위한 공통 인터페이스
    
    사용 예:
        class NaverFetcher(APIFetcher):
            def fetch_articles_by_keywords(self, keywords, max_per_keyword=3):
                # 구현...
    """
    
    def __init__(self, source_name: str, **kwargs):
        """
        Args:
            source_name: 소스 이름 (예: "네이버 뉴스", "구글 뉴스")
            **kwargs: 추가 설정 (API 키, 엔진 ID 등)
        """
        # API Fetcher는 URL이 고정되지 않으므로 빈 문자열 사용
        super().__init__(source_name, url="", **kwargs)
    
    def fetch_articles(self, max_articles: int = 5) -> List[Dict]:
        """
        이 메서드는 사용하지 않음
        대신 fetch_articles_by_keywords 사용
        """
        raise NotImplementedError(
            "APIFetcher는 fetch_articles_by_keywords() 메서드를 사용해야 합니다."
        )
    
    @abstractmethod
    def fetch_articles_by_keywords(self, keywords: List[str], max_per_keyword: int = 3) -> List[Dict]:
        """
        키워드 목록으로 기사 검색 (하위 클래스에서 구현)
        
        Args:
            keywords: 검색 키워드 목록
            max_per_keyword: 키워드당 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        pass