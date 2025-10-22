#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 크롤링 기반 뉴스 수집 (수정 버전 - User-Agent 추가)
403 Forbidden 에러 해결
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Dict, Optional
import time

from source_fetcher.base_fetcher import BaseSourceFetcher

class WebScraperFetcher(BaseSourceFetcher):
    """
    웹 크롤링 기반 뉴스 수집
    HTML 페이지에서 CSS 셀렉터를 이용해 기사 정보 추출
    
    수정사항: User-Agent 헤더 추가로 봇 차단 우회
    """
    
    def __init__(self, source_name: str, config: Dict):
        """
        초기화
        
        Args:
            source_name: 소스 이름
            config: 설정 딕셔너리
                - url: 크롤링할 URL
                - article_selector: 기사 컨테이너 선택자
                - title_selector: 제목 선택자
                - link_selector: 링크 선택자
                - date_selector: 날짜 선택자 (선택)
        """
        super().__init__(source_name, config)
        
        self.url = config['url']
        self.article_selector = config['article_selector']
        self.title_selector = config['title_selector']
        self.link_selector = config['link_selector']
        self.date_selector = config.get('date_selector')
        
        # User-Agent 헤더 추가 (봇 차단 우회) ⭐
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.timeout = config.get('timeout', 10)
    
    def fetch(self, max_articles: int = 10, **kwargs) -> List[Dict]:
        """
        웹 페이지에서 기사 목록 수집
        
        Args:
            max_articles: 최대 기사 수
            
        Returns:
            기사 딕셔너리 리스트
        """
        self.logger.info(f"웹 크롤링 시작: {self.url}")
        articles = []
        
        try:
            # HTTP 요청 (User-Agent 포함) ⭐
            response = requests.get(
                self.url, 
                headers=self.headers,  # 헤더 추가!
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
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"⚠️ 기사 파싱 실패: {e}")
                    continue
            
            self.logger.info(f"✅ {self.source_name}: {len(articles)}개 기사 수집 성공")
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"❌ {self.source_name}: {e}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ {self.source_name} 네트워크 에러: {e}")
        except Exception as e:
            self.logger.error(f"❌ {self.source_name} 예상치 못한 에러: {e}")
        
        return articles
    
    def _parse_article(self, article_elem) -> Optional[Dict]:
        """
        개별 기사 요소 파싱
        
        Args:
            article_elem: BeautifulSoup 기사 요소
            
        Returns:
            기사 딕셔너리 또는 None
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
        published_date = None
        if self.date_selector:
            date_elem = article_elem.select_one(self.date_selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                published_date = self._parse_date(date_text)
        
        return {
            'source': self.source_name,
            'title': title,
            'url': url,
            'published_date': published_date,
            'fetched_at': datetime.now().isoformat()
        }
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        날짜 문자열 파싱 (간단 버전)
        
        Args:
            date_text: 날짜 문자열
            
        Returns:
            ISO 형식 날짜 또는 None
        """
        try:
            # 여기서는 간단히 문자열 그대로 반환
            # 필요시 더 정교한 파싱 로직 추가
            return date_text
        except Exception as e:
            self.logger.warning(f"날짜 파싱 실패: {e}")
            return None
    
    def validate_config(self, config: Dict) -> bool:
        """
        설정 검증
        
        Args:
            config: 설정 딕셔너리
            
        Returns:
            검증 성공 여부
        """
        required = ['url', 'article_selector', 'title_selector', 'link_selector']
        for key in required:
            if key not in config:
                self.logger.error(f"❌ 필수 설정 누락: {key}")
                return False
        return True