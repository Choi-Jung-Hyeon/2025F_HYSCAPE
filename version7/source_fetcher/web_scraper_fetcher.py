# source_fetcher/web_scraper_fetcher.py
"""
HTML 웹 크롤링 전용 Fetcher
- BeautifulSoup4 사용
- CSS 선택자 기반 추출
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base_fetcher import BaseSourceFetcher

class WebScraperFetcher(BaseSourceFetcher):
    """
    웹 페이지로부터 기사 수집
    
    사용 예:
        fetcher = WebScraperFetcher(
            "H2 View",
            "https://www.h2-view.com/news/",
            article_selector="article.post",
            title_selector="h2.title",
            link_selector="a"
        )
        articles = fetcher.fetch_articles(max_articles=5)
    """
    
    def __init__(
        self,
        source_name: str,
        url: str,
        article_selector: str = None,
        title_selector: str = None,
        link_selector: str = "a",
        **kwargs
    ):
        """
        Args:
            article_selector: 기사 블록을 선택하는 CSS 선택자
            title_selector: 제목을 선택하는 CSS 선택자
            link_selector: 링크를 선택하는 CSS 선택자
        """
        super().__init__(source_name, url, **kwargs)
        self.article_selector = article_selector or "article"
        self.title_selector = title_selector or "h2"
        self.link_selector = link_selector
        
        # 헤더 설정
        self.headers = self.config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_articles(self, max_articles: int = 5) -> List[Dict]:
        """
        웹 페이지에서 기사 목록 수집
        
        Args:
            max_articles: 수집할 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        try:
            self.logger.info(f"웹 크롤링 시작: {self.url}")
            
            # HTTP 요청
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.config.get('timeout', 10)
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 기사 블록 찾기
            article_blocks = soup.select(self.article_selector)
            
            if not article_blocks:
                self.logger.warning(f"기사를 찾을 수 없습니다: {self.article_selector}")
                return []
            
            articles = []
            for block in article_blocks[:max_articles]:
                article = self._extract_article_from_block(block)
                if article and self.validate_article(article):
                    articles.append(article)
            
            self.log_success(len(articles))
            return articles
            
        except requests.exceptions.RequestException as e:
            self.log_error(e)
            return []
        except Exception as e:
            self.log_error(e)
            return []
    
    def _extract_article_from_block(self, block) -> Optional[Dict]:
        """
        기사 블록에서 제목과 URL 추출
        
        Args:
            block: BeautifulSoup 태그 객체
            
        Returns:
            Dict or None: 추출된 기사 정보
        """
        try:
            # 제목 추출
            title_tag = block.select_one(self.title_selector)
            if not title_tag:
                return None
            title = title_tag.get_text(strip=True)
            
            # URL 추출
            link_tag = block.select_one(self.link_selector)
            if not link_tag or not link_tag.get('href'):
                return None
            
            url = link_tag['href']
            
            # 상대 URL을 절대 URL로 변환
            if not url.startswith(('http://', 'https://')):
                from urllib.parse import urljoin
                url = urljoin(self.url, url)
            
            return {
                'title': title,
                'url': url,
                'source': self.source_name
            }
            
        except Exception as e:
            self.logger.debug(f"기사 추출 실패: {e}")
            return None