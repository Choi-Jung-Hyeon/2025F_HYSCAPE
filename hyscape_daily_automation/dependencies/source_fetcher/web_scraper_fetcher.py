#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 크롤링 기반 뉴스 수집 (수정 버전 v7.1)
- 초기화 메서드 수정: 다른 Fetcher와 일관된 인터페이스
- User-Agent 헤더로 봇 차단 우회
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

from source_fetcher.base_fetcher import BaseSourceFetcher

class WebScraperFetcher(BaseSourceFetcher):
    """
    웹 크롤링 기반 뉴스 수집
    HTML 페이지에서 CSS 셀렉터를 이용해 기사 정보 추출
    
    사용 예:
        fetcher = WebScraperFetcher(
            source_name="H2 View",
            url="https://www.h2-view.com/news/all-news/",
            article_selector="article.post",
            title_selector="h2.entry-title",
            link_selector="a"
        )
        articles = fetcher.fetch_articles(max_articles=5)
    """
    
    def __init__(self, source_name: str, url: str, 
                 article_selector: str, title_selector: str, 
                 link_selector: str, date_selector: str = None, **kwargs):
        """
        초기화 (수정됨 - 개별 파라미터 방식)
        
        Args:
            source_name: 소스 이름
            url: 크롤링할 URL
            article_selector: 기사 컨테이너 CSS 선택자
            title_selector: 제목 CSS 선택자
            link_selector: 링크 CSS 선택자
            date_selector: 날짜 CSS 선택자 (선택)
            **kwargs: 추가 설정 (timeout, headers 등)
        """
        super().__init__(source_name, url, **kwargs)
        
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.link_selector = link_selector
        self.date_selector = date_selector
        
        # User-Agent 헤더 추가 (봇 차단 우회) ⭐
        self.headers = kwargs.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.timeout = kwargs.get('timeout', 10)
    
    def fetch_articles(self, max_articles: int = 10) -> List[Dict]:
        """
        웹 페이지에서 기사 목록 수집
        
        Args:
            max_articles: 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        self.logger.info(f"웹 크롤링 시작: {self.url}")
        articles = []
        
        try:
            # HTTP 요청 (User-Agent 포함)
            response = requests.get(
                self.url, 
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 기사 컨테이너 찾기
            article_elements = soup.select(self.article_selector)
            
            if not article_elements:
                self.logger.warning(f"⚠️ 기사를 찾을 수 없습니다 (selector: {self.article_selector})")
                return []
            
            # 각 기사 파싱
            for article_elem in article_elements[:max_articles]:
                try:
                    article = self._parse_article(article_elem)
                    if article and self.validate_article(article):
                        articles.append(article)
                except Exception as e:
                    self.logger.debug(f"⚠️ 기사 파싱 실패: {e}")
                    continue
            
            self.log_success(len(articles))
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"❌ HTTP 에러: {e}")
            self.log_error(e)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ 네트워크 에러: {e}")
            self.log_error(e)
        except Exception as e:
            self.logger.error(f"❌ 예상치 못한 에러: {e}")
            self.log_error(e)
        
        return articles
    
    def _parse_article(self, article_elem) -> Optional[Dict]:
        """
        개별 기사 요소 파싱
        
        Args:
            article_elem: BeautifulSoup 기사 요소
            
        Returns:
            Dict: 기사 정보 또는 None
        """
        # 제목 추출
        title_elem = article_elem.select_one(self.title_selector)
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        
        # 링크 추출
        link_elem = article_elem.select_one(self.link_selector)
        if not link_elem:
            return None
        
        url = link_elem.get('href')
        if not url:
            return None
        
        # 상대 경로를 절대 경로로 변환
        if url.startswith('/'):
            base_url = '/'.join(self.url.split('/')[:3])
            url = base_url + url
        elif not url.startswith('http'):
            url = self.url.rstrip('/') + '/' + url.lstrip('/')
        
        # 날짜 추출 (선택사항)
        published = None
        if self.date_selector:
            date_elem = article_elem.select_one(self.date_selector)
            if date_elem:
                published = date_elem.get_text(strip=True)
        
        return {
            'source': self.source_name,
            'title': title,
            'url': url,
            'published': published or ''
        }


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("🧪 WebScraperFetcher v7.1 테스트")
    print("=" * 70)
    
    # H2 View 테스트
    print("\n[테스트 1] H2 View 크롤링")
    fetcher = WebScraperFetcher(
        source_name="H2 View",
        url="https://www.h2-view.com/news/all-news/",
        article_selector="article.post",
        title_selector="h2.entry-title",
        link_selector="a"
    )
    
    articles = fetcher.fetch_articles(max_articles=3)
    
    if articles:
        print(f"✅ {len(articles)}개 기사 수집 성공\n")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title'][:60]}...")
            print(f"   URL: {article['url']}\n")
    else:
        print("⚠️ 기사 수집 실패")