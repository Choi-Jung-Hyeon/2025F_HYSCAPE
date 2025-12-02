#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국수소연합(H2HUB) PDF 브리핑 수집 모듈
웹사이트에서 "브리핑" 키워드가 포함된 게시글의 PDF를 다운로드합니다.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import re

import requests
from bs4 import BeautifulSoup

import config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class H2HubCollector:
    """
    한국수소연합(H2HUB) 브리핑 수집 클래스
    
    주요 기능:
    1. 게시판 페이지 크롤링
    2. "브리핑" 키워드 필터링
    3. PDF 파일 다운로드
    """
    
    def __init__(self):
        """수집기 초기화"""
        self.session = requests.Session()
        self.session.headers.update(config.DEFAULT_HEADERS)
        self.download_dir = config.DOWNLOADS_DIR
        
        logger.info("H2HUB Collector 초기화 완료")
        logger.info(f"다운로드 경로: {self.download_dir}")
    
    def collect_briefings(self, max_pages: int = 3) -> List[Dict]:
        """
        H2HUB에서 브리핑 PDF를 수집하는 메인 메서드
        
        Args:
            max_pages: 크롤링할 최대 페이지 수
            
        Returns:
            List[Dict]: 수집된 브리핑 정보 리스트
                [
                    {
                        'title': '제목',
                        'date': '날짜',
                        'pdf_path': '로컬 PDF 경로',
                        'url': '원본 URL'
                    },
                    ...
                ]
        """
        logger.info("=" * 70)
        logger.info("한국수소연합 브리핑 수집 시작")
        logger.info("=" * 70)
        
        collected = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"\n📄 {page_num}페이지 수집 중...")
            
            # 페이지 오프셋 계산 (10개씩)
            offset = (page_num - 1) * 10
            
            # 게시판 HTML 가져오기
            articles = self._fetch_article_list(offset)
            
            if not articles:
                logger.warning(f"{page_num}페이지에서 게시글을 찾을 수 없습니다.")
                break
            
            logger.info(f"  ➜ {len(articles)}개의 게시글 발견")
            
            # 각 게시글 처리
            for article in articles:
                result = self._process_article(article)
                
                if result:
                    collected.append(result)
                    time.sleep(1)  # 서버 부하 방지
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ 수집 완료: 총 {len(collected)}개의 브리핑 다운로드")
        logger.info("=" * 70)
        
        return collected
    
    def _fetch_article_list(self, offset: int = 0) -> List[Dict]:
        """
        게시판 목록 페이지에서 게시글 정보 추출
        
        Args:
            offset: 페이지 오프셋 (0, 10, 20, ...)
            
        Returns:
            List[Dict]: 게시글 정보 리스트
        """
        try:
            # URL 생성
            url = f"{config.H2HUB_PERIODICALS_URL}?mode=list&article.offset={offset}&articleLimit=10"
            
            logger.debug(f"  요청 URL: {url}")
            
            # HTTP 요청
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 게시글 목록 찾기 (실제 HTML 구조 기반)
            articles = []
            
            # td.b-td-left 안의 div.b-title-box 찾기
            for td in soup.find_all('td', class_='b-td-left'):
                title_box = td.find('div', class_='b-title-box')
                
                if not title_box:
                    continue
                
                # 링크와 제목 추출
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
                
                # 상세 URL 생성
                detail_url = urljoin(config.H2HUB_BASE_URL, href)
                
                articles.append({
                    'title': title,
                    'date': date,
                    'detail_url': detail_url
                })
                
                logger.debug(f"    - {title} ({date})")
            
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"  ❌ 페이지 요청 실패: {e}")
            return []
        
        except Exception as e:
            logger.error(f"  ❌ 파싱 오류: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """
        개별 게시글 처리 (PDF 다운로드)
        
        Args:
            article: 게시글 정보
            
        Returns:
            Dict: 처리 결과 또는 None
        """
        title = article['title']
        date = article['date']
        detail_url = article['detail_url']
        
        logger.info(f"\n  📎 처리 중: {title}")
        
        try:
            # 상세 페이지 접근
            response = self.session.get(detail_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # PDF 링크 찾기
            pdf_url = self._find_pdf_link(soup)
            
            if not pdf_url:
                logger.warning("    ⚠️ PDF 링크를 찾을 수 없습니다")
                return None
            
            # PDF 다운로드
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
        """
        상세 페이지에서 PDF 다운로드 링크 찾기
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            str: PDF URL 또는 None
        """
        # 방법 1: .hwp 또는 .pdf 확장자가 있는 링크 찾기
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            if href.endswith('.pdf') or '.pdf' in href.lower():
                return urljoin(config.H2HUB_BASE_URL, href)
        
        # 방법 2: "바로보기" 또는 "다운로드" 버튼 찾기
        for link in soup.find_all('a'):
            link_text = link.get_text(strip=True)
            
            if any(keyword in link_text for keyword in ['바로보기', '다운로드', 'PDF', 'pdf']):
                href = link.get('href', '')
                if href:
                    return urljoin(config.H2HUB_BASE_URL, href)
        
        # 방법 3: input[type="hidden"] 에서 파일 정보 찾기
        file_input = soup.find('input', {'type': 'hidden', 'name': re.compile(r'file|attach', re.I)})
        if file_input and file_input.get('value'):
            file_value = file_input['value']
            if file_value.endswith('.pdf'):
                return urljoin(config.H2HUB_BASE_URL, file_value)
        
        return None
    
    def _download_pdf(self, pdf_url: str, title: str, date: str) -> Optional[str]:
        """
        PDF 파일 다운로드
        
        Args:
            pdf_url: PDF URL
            title: 제목
            date: 날짜
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        try:
            # 안전한 파일명 생성
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            # 날짜 포맷팅 (YYYY-MM-DD → YYMMDD)
            if date and len(date) >= 10:
                date_str = date.replace('-', '').replace('.', '')[2:8]  # 25.12.03 → 251203
            else:
                date_str = time.strftime('%y%m%d')
            
            filename = f"{date_str}_{safe_title}.pdf"
            filepath = self.download_dir / filename
            
            # 이미 다운로드되어 있으면 스킵
            if filepath.exists():
                logger.info(f"    ℹ️ 이미 존재: {filename}")
                return str(filepath)
            
            # PDF 다운로드
            logger.debug(f"    다운로드 URL: {pdf_url}")
            response = self.session.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 파일 저장
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"    ❌ 다운로드 실패: {e}")
            return None


def main():
    """테스트용 메인 함수"""
    collector = H2HubCollector()
    results = collector.collect_briefings(max_pages=2)
    
    print("\n" + "=" * 70)
    print(f"수집 완료: {len(results)}개")
    print("=" * 70)
    
    for result in results:
        print(f"\n제목: {result['title']}")
        print(f"날짜: {result['date']}")
        print(f"파일: {result['pdf_path']}")


if __name__ == "__main__":
    main()