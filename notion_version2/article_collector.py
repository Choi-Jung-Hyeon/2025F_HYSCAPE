#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국수소연합(H2HUB) PDF 브리핑 수집 모듈
게시판에서 "브리핑" 키워드가 포함된 게시글의 PDF를 다운로드합니다.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import time

import config

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class H2HUBBriefingCollector:
    """
    한국수소연합(H2HUB) 게시판에서 브리핑 PDF를 자동 수집하는 클래스
    
    주요 기능:
    1. 게시판 목록 페이지 크롤링
    2. "브리핑" 키워드 필터링
    3. 게시글 상세 페이지에서 PDF 다운로드
    """
    
    def __init__(self):
        self.base_url = config.H2HUB_BASE_URL
        self.periodicals_url = config.H2HUB_PERIODICALS_URL
        self.headers = config.DEFAULT_HEADERS
        self.downloads_dir = config.DOWNLOADS_DIR
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info(f"H2HUB Collector 초기화 완료")
        logger.info(f"다운로드 경로: {self.downloads_dir}")
    
    def collect_briefings(self, max_pages: int = 3) -> List[Dict]:
        """
        브리핑 PDF를 수집하는 메인 메서드
        
        Args:
            max_pages: 수집할 최대 페이지 수
            
        Returns:
            List[Dict]: 수집된 브리핑 정보 리스트
                [
                    {
                        'title': '제목',
                        'date': '날짜',
                        'url': '원문 URL',
                        'pdf_path': 'PDF 로컬 경로'
                    },
                    ...
                ]
        """
        logger.info("=" * 70)
        logger.info("한국수소연합 브리핑 수집 시작")
        logger.info("=" * 70)
        
        all_briefings = []
        
        for page in range(max_pages):
            logger.info(f"\n📄 {page + 1}페이지 수집 중...")
            
            # 게시판 목록 가져오기
            articles = self._fetch_article_list(page)
            
            if not articles:
                logger.warning(f"{page + 1}페이지에서 게시글을 찾을 수 없습니다.")
                break
            
            # 브리핑 필터링 및 다운로드
            for article in articles:
                if self._is_briefing(article['title']):
                    logger.info(f"✅ 브리핑 발견: {article['title']}")
                    
                    # PDF 다운로드
                    pdf_info = self._download_pdf(article)
                    
                    if pdf_info:
                        all_briefings.append(pdf_info)
                        time.sleep(1)  # 서버 부하 방지
            
            time.sleep(2)  # 페이지 간 딜레이
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ 수집 완료: 총 {len(all_briefings)}개의 브리핑 다운로드")
        logger.info("=" * 70)
        
        return all_briefings
    
    def _fetch_article_list(self, page: int = 0) -> List[Dict]:
        """
        게시판 목록 페이지에서 게시글 정보 추출
        
        Args:
            page: 페이지 번호 (0부터 시작)
            
        Returns:
            List[Dict]: 게시글 정보 리스트
        """
        try:
            # 페이징 파라미터 추가
            params = {
                'article.offset': page * 10,
                'articleLimit': 10
            }
            
            response = self.session.get(
                self.periodicals_url,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # 게시판 테이블에서 게시글 추출
            # (실제 HTML 구조에 맞게 선택자 조정 필요)
            article_rows = soup.select('table.board-list tbody tr')
            
            if not article_rows:
                # 다른 구조 시도
                article_rows = soup.select('div.board-list li')
            
            for row in article_rows:
                try:
                    # 제목과 링크 추출 (구조에 따라 다를 수 있음)
                    title_elem = row.select_one('a.title, td.title a, div.title a')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    if not link:
                        continue
                    
                    # 절대 URL 생성
                    full_url = urljoin(self.base_url, link)
                    
                    # 날짜 추출 (있는 경우)
                    date_elem = row.select_one('td.date, span.date, div.date')
                    date = date_elem.get_text(strip=True) if date_elem else None
                    
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'date': date
                    })
                    
                except Exception as e:
                    logger.debug(f"게시글 파싱 오류: {e}")
                    continue
            
            logger.info(f"  ➜ {len(articles)}개의 게시글 발견")
            return articles
            
        except Exception as e:
            logger.error(f"게시판 목록 가져오기 실패: {e}")
            return []
    
    def _is_briefing(self, title: str) -> bool:
        """
        제목에 브리핑 키워드가 포함되어 있는지 확인
        
        Args:
            title: 게시글 제목
            
        Returns:
            bool: 브리핑 여부
        """
        for keyword in config.BRIEFING_KEYWORDS:
            if keyword in title:
                return True
        return False
    
    def _download_pdf(self, article: Dict) -> Optional[Dict]:
        """
        게시글 상세 페이지에서 PDF 다운로드
        
        Args:
            article: 게시글 정보
            
        Returns:
            Dict: 다운로드된 PDF 정보 (실패 시 None)
        """
        try:
            # 상세 페이지 접근
            response = self.session.get(article['url'], timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # PDF 첨부파일 링크 찾기
            pdf_link = self._find_pdf_link(soup)
            
            if not pdf_link:
                logger.warning(f"  ⚠️ PDF 링크를 찾을 수 없음: {article['title']}")
                return None
            
            # PDF 다운로드
            pdf_path = self._download_file(pdf_link, article['title'])
            
            if not pdf_path:
                return None
            
            # 날짜 파싱
            date = self._parse_date(article.get('date'), soup)
            
            return {
                'title': article['title'],
                'date': date,
                'url': article['url'],
                'pdf_path': str(pdf_path)
            }
            
        except Exception as e:
            logger.error(f"  ❌ PDF 다운로드 실패 ({article['title']}): {e}")
            return None
    
    def _find_pdf_link(self, soup: BeautifulSoup) -> Optional[str]:
        """
        상세 페이지에서 PDF 첨부파일 링크 찾기
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            str: PDF 링크 (없으면 None)
        """
        # 첨부파일 영역에서 PDF 링크 찾기
        # (실제 구조에 맞게 선택자 조정 필요)
        
        # 방법 1: 첨부파일 영역에서 찾기
        attach_area = soup.select_one('div.attach, div.file-list, ul.attach-list')
        
        if attach_area:
            pdf_links = attach_area.select('a[href*=".pdf"], a[href*="download"]')
            
            for link in pdf_links:
                href = link.get('href', '')
                if '.pdf' in href.lower() or 'download' in href.lower():
                    return urljoin(self.base_url, href)
        
        # 방법 2: 전체 페이지에서 PDF 링크 찾기
        all_links = soup.select('a[href*=".pdf"]')
        
        if all_links:
            return urljoin(self.base_url, all_links[0].get('href', ''))
        
        # 방법 3: download 파라미터가 있는 링크 찾기
        download_links = soup.select('a[href*="download"], a[href*="fileDown"]')
        
        if download_links:
            return urljoin(self.base_url, download_links[0].get('href', ''))
        
        return None
    
    def _download_file(self, url: str, title: str) -> Optional[Path]:
        """
        파일 다운로드 및 저장
        
        Args:
            url: 다운로드 URL
            title: 게시글 제목 (파일명 생성용)
            
        Returns:
            Path: 저장된 파일 경로 (실패 시 None)
        """
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 파일명 생성 (특수문자 제거)
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{safe_title[:50]}.pdf"
            
            filepath = self.downloads_dir / filename
            
            # 파일 저장
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = filepath.stat().st_size / 1024  # KB
            logger.info(f"  ✅ 다운로드 완료: {filename} ({file_size:.1f} KB)")
            
            return filepath
            
        except Exception as e:
            logger.error(f"  ❌ 파일 다운로드 실패: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str], soup: BeautifulSoup) -> str:
        """
        날짜 파싱 및 포맷팅
        
        Args:
            date_str: 날짜 문자열
            soup: 상세 페이지 BeautifulSoup (날짜 추출용)
            
        Returns:
            str: YYYY-MM-DD 형식의 날짜
        """
        # 날짜 문자열이 있으면 파싱 시도
        if date_str:
            try:
                # 다양한 날짜 형식 처리
                for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%Y%m%d']:
                    try:
                        dt = datetime.strptime(date_str.replace('.', '-').replace('/', '-')[:10], fmt)
                        return dt.strftime('%Y-%m-%d')
                    except:
                        continue
            except:
                pass
        
        # 상세 페이지에서 날짜 찾기
        if soup:
            date_elem = soup.select_one('span.date, td.date, div.date, p.date')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # 숫자만 추출 (YYYYMMDD 형식)
                date_numbers = re.findall(r'\d+', date_text)
                if len(date_numbers) >= 3:
                    try:
                        year = int(date_numbers[0])
                        month = int(date_numbers[1])
                        day = int(date_numbers[2])
                        return f"{year:04d}-{month:02d}-{day:02d}"
                    except:
                        pass
        
        # 파싱 실패 시 오늘 날짜 반환
        return datetime.now().strftime('%Y-%m-%d')


def main():
    """테스트용 메인 함수"""
    collector = H2HUBBriefingCollector()
    briefings = collector.collect_briefings(max_pages=2)
    
    print("\n" + "=" * 70)
    print("수집 결과:")
    print("=" * 70)
    
    for i, briefing in enumerate(briefings, 1):
        print(f"\n{i}. {briefing['title']}")
        print(f"   날짜: {briefing['date']}")
        print(f"   URL: {briefing['url']}")
        print(f"   PDF: {briefing['pdf_path']}")


if __name__ == "__main__":
    main()
