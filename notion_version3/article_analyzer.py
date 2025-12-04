#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한국수소연합(H2HUB) PDF 브리핑 수집 모듈"""

import logging
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class H2HUBBriefingCollector:
    """H2HUB 브리핑 수집 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.DEFAULT_HEADERS)
        self.download_dir = config.DOWNLOADS_DIR
        logger.info("H2HUB Collector 초기화 완료")
    
    def collect_briefings(self, max_pages: int = 3) -> List[Dict]:
        """브리핑 PDF 수집"""
        logger.info("=" * 70)
        logger.info("한국수소연합 브리핑 수집 시작")
        logger.info("=" * 70)
        
        collected = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"\n📄 {page_num}페이지 수집 중...")
            
            offset = (page_num - 1) * 10
            articles = self._fetch_article_list(offset)
            
            if not articles:
                logger.warning(f"{page_num}페이지에서 게시글 없음")
                break
            
            logger.info(f"  ➜ {len(articles)}개 게시글 발견")
            
            for article in articles:
                result = self._process_article(article)
                if result:
                    collected.append(result)
                    time.sleep(1)
        
        logger.info(f"\n✅ 수집 완료: {len(collected)}개")
        return collected
    
    def _fetch_article_list(self, offset: int = 0) -> List[Dict]:
        """게시판 목록 페이지에서 게시글 정보 추출"""
        try:
            url = f"{config.H2HUB_PERIODICALS_URL}?mode=list&article.offset={offset}&articleLimit=10"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            for td in soup.find_all('td', class_='b-td-left'):
                title_box = td.find('div', class_='b-title-box')
                if not title_box:
                    continue
                
                link = title_box.find('a')
                title_span = title_box.find('span', class_='b-title')
                date_span = title_box.find('span', class_='b-date')
                
                if not (link and title_span):
                    continue
                
                title = title_span.get_text(strip=True)
                href = link.get('href', '')
                date = date_span.get_text(strip=True) if date_span else ''
                
                # "브리핑" 키워드 필터링
                if not any(keyword in title for keyword in config.BRIEFING_KEYWORDS):
                    continue
                
                detail_url = urljoin(config.H2HUB_BASE_URL, href)
                articles.append({
                    'title': title,
                    'date': date,
                    'detail_url': detail_url
                })
            
            return articles
        except Exception as e:
            logger.error(f"  ❌ 페이지 요청 실패: {e}")
            return []
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """개별 게시글 처리 (PDF 다운로드)"""
        title = article['title']
        date = article['date']
        detail_url = article['detail_url']
        
        logger.info(f"\n  📎 처리 중: {title}")
        
        try:
            response = self.session.get(detail_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_url = self._find_pdf_link(soup)
            
            if not pdf_url:
                logger.warning("    ⚠️ PDF 링크 없음")
                return None
            
            pdf_path = self._download_pdf(pdf_url, title, date)
            
            if not pdf_path:
                return None
            
            logger.info(f"    ✅ 다운로드 완료: {Path(pdf_path).name}")
            
            return {
                'title': title,
                'date': date,
                'pdf_path': pdf_path,
                'url': detail_url
            }
        except Exception as e:
            logger.error(f"    ❌ 처리 실패: {e}")
            return None
    
    def _find_pdf_link(self, soup: BeautifulSoup) -> Optional[str]:
        """상세 페이지에서 PDF 링크 찾기"""
        # .pdf 확장자 링크 찾기
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.endswith('.pdf') or '.pdf' in href.lower():
                return urljoin(config.H2HUB_BASE_URL, href)
        
        # "바로보기" 버튼 찾기
        for link in soup.find_all('a'):
            link_text = link.get_text(strip=True)
            if any(keyword in link_text for keyword in ['바로보기', '다운로드', 'PDF']):
                href = link.get('href', '')
                if href:
                    return urljoin(config.H2HUB_BASE_URL, href)
        
        return None
    
    def _download_pdf(self, pdf_url: str, title: str, date: str) -> Optional[str]:
        """PDF 파일 다운로드"""
        try:
            # 안전한 파일명 생성
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            # 날짜 포맷팅
            if date and len(date) >= 10:
                date_str = date.replace('-', '').replace('.', '')[2:8]
            else:
                date_str = time.strftime('%y%m%d')
            
            filename = f"{date_str}_{safe_title}.pdf"
            filepath = self.download_dir / filename
            
            # 이미 존재하면 스킵
            if filepath.exists():
                logger.info(f"    ℹ️ 이미 존재: {filename}")
                return str(filepath)
            
            # PDF 다운로드
            response = self.session.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(filepath)
        except Exception as e:
            logger.error(f"    ❌ 다운로드 실패: {e}")
            return None


def main():
    """테스트용"""
    collector = H2HUBBriefingCollector()
    results = collector.collect_briefings(max_pages=2)
    
    print(f"\n수집 완료: {len(results)}개")
    for result in results:
        print(f"\n제목: {result['title']}")
        print(f"파일: {result['pdf_path']}")


if __name__ == "__main__":
    main()