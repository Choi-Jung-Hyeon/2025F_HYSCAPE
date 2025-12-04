# source_fetcher/__init__.py
"""
Source Fetcher 모듈
- 다양한 뉴스 소스로부터 기사 수집
- 확장 가능한 아키텍처
"""

from .base_fetcher import BaseSourceFetcher
from .rss_fetcher import RSSFetcher
from .web_scraper_fetcher import WebScraperFetcher
from .api_fetcher import APIFetcher
from .naver_fetcher import NaverFetcher
from .google_fetcher import GoogleFetcher
from .factory import SourceFetcherFactory, FetcherManager

__all__ = [
    'BaseSourceFetcher',
    'RSSFetcher',
    'WebScraperFetcher',
    'APIFetcher',
    'NaverFetcher',
    'GoogleFetcher',
    'SourceFetcherFactory',
    'FetcherManager'
]

__version__ = '7.0.0'