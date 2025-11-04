#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# article_collector.py (v8.0)
"""
월간수소경제(H2News) 아카이브 기사 수집기
- PDF 기획안  기반
- 지정된 연도의 기사 목록(pagination)을 크롤링
- newspaper3k를 사용해 개별 기사 본문 추출 (v7.0 `content_scraper` 로직 통합)
"""

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from urllib.parse import urljoin, urlparse
import logging
from time import sleep
from tqdm import tqdm
from typing import List, Dict, Optional

# 설정 파일 임포트
import config

class H2NewsArchiveCollector:
    """
    월간수소경제의 특정 연도 과거 기사를 수집합니다.
    (PDF [cite: 62] 'H2NewsArchiveCollector' 클래스 구현)
    """
    def __init__(self, year: int, limit: int = 0):
        self.base_url = config.H2NEWS_ARCHIVE_URL
        self.year = year
        # 0이 아니면 테스트 리밋 적용 (PDF [cite: 1-302]의 테스트 요구사항)
        self.limit = limit 
        self.articles_found_count = 0
        self.session = requests.Session()
        self.session.headers.update(config.DEFAULT_HEADERS)

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """지정된 URL의 BeautifulSoup 객체를 반환합니다."""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"페이지 로드 실패 (URL: {url}): {e}")
            return None

    def fetch_archive_by_year(self) -> List[Dict[str, str]]:
        """
        특정 연도의 모든 기사 URL과 제목, 날짜를 수집합니다.
        (PDF [cite: 63] `fetch_archive_by_year` 메서드 구현)
        
        월간수소경제는 페이지네이션(pagination)을 사용합니다.
        (예: ...articleList.html?page=2&year=2024)
        """
        logging.info(f"===== {self.year}년 월간수소경제 아카이브 수집 시작 =====")
        collected_articles = []
        page = 1
        
        while True:
            # 테스트 리밋에 도달하면 중단
            if self.limit > 0 and self.articles_found_count >= self.limit:
                logging.info(f"테스트 리밋 ({self.limit}개)에 도달하여 수집을 중단합니다.")
                break

            params = {
                "page": page,
                "year": self.year,
                "sc_section_code": "S1N1" # "뉴스" 섹션 코드
            }
            logging.info(f"{self.year}년 {page}페이지 수집 중...")
            soup = self._get_soup(self.base_url)
            if not soup:
                break

            # PDF 의 CSS 선택자 아이디어를 적용
            article_list = soup.select("ul.art_list > li") 
            
            if not article_list:
                logging.info(f"{page}페이지에 기사가 없습니다. {self.year}년 수집을 종료합니다.")
                break # 기사가 더 이상 없으면 종료

            for item in article_list:
                if self.limit > 0 and self.articles_found_count >= self.limit:
                    break
                
                title_tag = item.select_one("h2.titles a")
                date_tag = item.select_one("span.date")
                
                if title_tag and date_tag:
                    title = title_tag.get_text(strip=True)
                    relative_url = title_tag['href']
                    absolute_url = urljoin(self.base_url, relative_url)
                    date_str = date_tag.get_text(strip=True)
                    
                    collected_articles.append({
                        "title": title,
                        "url": absolute_url,
                        "date_str": date_str,
                        "year": self.year,
                        "source": "월간수소경제"
                    })
                    self.articles_found_count += 1

            # 페이지네이션의 '다음' 버튼이 비활성화되었는지 확인 (더 정확한 종료 조건)
            next_page_tag = soup.select_one("a.next-page")
            if not next_page_tag or 'disabled' in next_page_tag.get('class', []):
                logging.info(f"마지막 페이지({page}p)에 도달했습니다. {self.year}년 수집을 종료합니다.")
                break
                
            page += 1
            sleep(0.5) # 서버 부하 방지

        logging.info(f"총 {self.articles_found_count}개의 {self.year}년 기사 메타데이터 수집 완료.")
        return collected_articles

    def fetch_article_content(self, url: str) -> Optional[str]:
        """
        개별 기사 URL에서 본문을 추출합니다.
        (PDF [cite: 67] `fetch_article_content` 메서드 및 v7.0 `content_scraper` 로직)
        """
        try:
            # newspaper3k 설정
            article = Article(url, language='ko')
            article.download(input_html=self.session.get(url, timeout=config.REQUEST_TIMEOUT).text)
            article.parse()
            return article.text
        except Exception as e:
            logging.warning(f"Newspaper3k 본문 추출 실패 (URL: {url}): {e}")
            return None

    def run(self) -> List[Dict[str, str]]:
        """전체 수집 워크플로우를 실행합니다."""
        
        # 1. 연도별 기사 목록 수집
        articles_meta = self.fetch_archive_by_year()
        
        if not articles_meta:
            logging.warning(f"{self.year}년에 수집된 기사가 없습니다.")
            return []

        # 2. 각 기사 본문 추출 (tqdm으로 진행률 표시)
        logging.info(f"{len(articles_meta)}개 기사의 본문 추출을 시작합니다...")
        final_articles_with_content = []
        
        for meta in tqdm(articles_meta, desc=f"{self.year}년 본문 추출 중"):
            content = self.fetch_article_content(meta['url'])
            if content:
                meta['content'] = content
                final_articles_with_content.append(meta)
            else:
                logging.warning(f"본문 추출 실패: {meta['title']} ({meta['url']})")
            sleep(0.2) # 서버 부하 방지

        logging.info(f"총 {len(final_articles_with_content)}개 기사의 본문 추출 완료.")
        return final_articles_with_content

if __name__ == '__main__':
    # 이 파일을 직접 실행할 경우 테스트 수행
    logging.basicConfig(level=logging.INFO)
    
    # 2024년 기사 5개만 테스트 (PDF [cite: 1-302]의 테스트 요구사항)
    TEST_YEAR = 2024
    TEST_LIMIT = 5 
    
    collector = H2NewsArchiveCollector(year=TEST_YEAR, limit=TEST_LIMIT)
    articles = collector.run()
    
    print(f"\n===== {TEST_YEAR}년 테스트 수집 결과 (상위 {TEST_LIMIT}개) =====")
    for i, article in enumerate(articles):
        print(f"\n[{i+1}] {article['title']}")
        print(f"  - URL: {article['url']}")
        print(f"  - Date: {article['date_str']}")
        print(f"  - Content (첫 50자): {article['content'][:50]}...")
    print(f"\n==========================================")
    print(f"총 {len(articles)}개 기사 수집 및 본문 추출 성공")