# source_fetcher/rss_fetcher.py
"""
RSS 피드 전용 Fetcher
- feedparser 라이브러리 사용
- 가장 안정적인 방식
"""

import feedparser
from typing import List, Dict
from .base_fetcher import BaseSourceFetcher

class RSSFetcher(BaseSourceFetcher):
    """
    RSS 피드로부터 기사 수집
    
    사용 예:
        fetcher = RSSFetcher("월간수소경제", "http://www.h2news.kr/rss/S1N1.xml")
        articles = fetcher.fetch_articles(max_articles=10)
    """
    
    def fetch_articles(self, max_articles: int = 5) -> List[Dict]:
        """
        RSS 피드에서 기사 목록 수집
        
        Args:
            max_articles: 수집할 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        try:
            self.logger.info(f"RSS 피드 수집 시작: {self.url}")
            
            # RSS 피드 파싱
            feed = feedparser.parse(self.url)
            
            if not feed.entries:
                self.logger.warning(f"RSS 피드에 기사가 없습니다: {self.url}")
                return []
            
            articles = []
            for entry in feed.entries[:max_articles]:
                article = {
                    'title': entry.get('title', '제목 없음'),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': self.source_name
                }
                
                # 유효성 검사
                if self.validate_article(article):
                    articles.append(article)
            
            self.log_success(len(articles))
            return articles
            
        except Exception as e:
            self.log_error(e)
            return []