"""
K-Startup 크롤러 구현체
https://www.k-startup.go.kr/ 사업공고 크롤링
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
import time

from scrapers.base_scraper import BaseScraper


class KStartupScraper(BaseScraper):
    """
    K-Startup (창업넷) 사업공고 크롤러
    
    필터 전략: Type B (지원 중심)
    - 기술 키워드 OR (지원 키워드 AND 자격 키워드)
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, site_name='k_startup')
        
        # K-Startup 특화 설정
        self.base_url = "https://www.k-startup.go.kr"
        self.list_url = f"{self.base_url}/web/contents/biznotify.do"
        self.max_pages = 3  # 최근 3페이지만 크롤링
        
    def fetch_announcements(self) -> List[Dict]:
        """
        K-Startup 공고 목록 페이지에서 데이터 수집
        
        Returns:
            List[Dict]: 원본 공고 데이터 리스트
        """
        all_announcements = []
        
        for page in range(1, self.max_pages + 1):
            self.logger.info(f"페이지 {page}/{self.max_pages} 크롤링 중...")
            
            try:
                # 페이지 요청
                params = {
                    'schM': 'list',
                    'page': page,
                    'schBzType': '',  # 사업 유형 (전체)
                    'schStts': 'R',   # 모집중(R) / 마감(D)
                }
                
                response = requests.get(
                    self.list_url,
                    params=params,
                    headers=self.get_headers(),
                    timeout=10
                )
                response.raise_for_status()
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 공고 리스트 찾기 (실제 HTML 구조에 맞게 수정 필요)
                # 예시: <div class="board-list"> 내부의 각 항목
                announcements = self._parse_list_page(soup)
                all_announcements.extend(announcements)
                
                self.logger.info(f"페이지 {page}: {len(announcements)}개 공고 수집")
                
                # 서버 부하 방지
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"페이지 {page} 크롤링 실패: {str(e)}")
                continue
        
        return all_announcements
    
    def _parse_list_page(self, soup: BeautifulSoup) -> List[Dict]:
        """
        목록 페이지 HTML 파싱
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            List[Dict]: 공고 원본 데이터
        """
        announcements = []
        
        # 실제 K-Startup HTML 구조에 맞게 수정 필요
        # 아래는 일반적인 게시판 구조 예시
        
        # 방법 1: 테이블 형식인 경우
        rows = soup.select('table.board-list tbody tr')
        
        # 방법 2: 리스트 형식인 경우
        if not rows:
            rows = soup.select('div.board-list ul li')
        
        for row in rows:
            try:
                # 제목과 URL 추출
                title_elem = row.select_one('a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 상대 URL을 절대 URL로 변환
                url = title_elem.get('href', '')
                if url and not url.startswith('http'):
                    url = self.base_url + url
                
                # 마감일 추출 (예: "2024-12-31")
                deadline = self._extract_deadline(row)
                
                # 주관기관 추출
                organization = self._extract_organization(row)
                
                announcements.append({
                    'title': title,
                    'url': url,
                    'deadline': deadline,
                    'organization': organization,
                    'raw_html': str(row),  # 추가 파싱이 필요할 수 있음
                })
                
            except Exception as e:
                self.logger.warning(f"항목 파싱 실패: {str(e)}")
                continue
        
        return announcements
    
    def _extract_deadline(self, element) -> str:
        """
        마감일 추출 및 표준화
        
        Args:
            element: HTML 요소
            
        Returns:
            str: YYYY-MM-DD 형식 날짜
        """
        # 예: <span class="date">2024-12-31</span>
        date_elem = element.select_one('.date, .deadline, td:nth-child(4)')
        
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            
            # 날짜 패턴 추출 (YYYY-MM-DD 또는 YYYY.MM.DD)
            match = re.search(r'(\d{4})[-.](\d{2})[-.](\d{2})', date_text)
            if match:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
        return "미정"
    
    def _extract_organization(self, element) -> str:
        """
        주관기관 추출
        
        Args:
            element: HTML 요소
            
        Returns:
            str: 기관명
        """
        # 예: <span class="organ">중소벤처기업부</span>
        org_elem = element.select_one('.organ, .organization, td:nth-child(3)')
        
        if org_elem:
            return org_elem.get_text(strip=True)
        
        return "미확인"
    
    def parse_announcement(self, raw_data: Dict) -> Optional[Dict]:
        """
        원본 공고 데이터를 표준 포맷으로 변환
        
        Args:
            raw_data: fetch_announcements()에서 반환된 원본 데이터
            
        Returns:
            Optional[Dict]: 표준화된 공고 정보
        """
        try:
            # 상세 페이지에서 추가 정보 수집 (선택사항)
            description = self._fetch_detail_page(raw_data['url'])
            
            announcement = {
                'title': raw_data['title'],
                'url': raw_data['url'],
                'deadline': raw_data['deadline'],
                'organization': raw_data['organization'],
                'description': description or raw_data['title'],  # 상세 정보 없으면 제목 사용
                'tags': self._extract_tags(raw_data['title'], description),
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 유효성 검사
            if self.validate_announcement(announcement):
                return announcement
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"공고 파싱 실패: {str(e)}")
            return None
    
    def _fetch_detail_page(self, url: str) -> Optional[str]:
        """
        상세 페이지에서 공고 내용 수집
        
        Args:
            url: 상세 페이지 URL
            
        Returns:
            Optional[str]: 공고 상세 내용
        """
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 본문 내용 추출 (실제 구조에 맞게 수정)
            content = soup.select_one('.content, .view-content, #content')
            
            if content:
                # HTML 태그 제거하고 텍스트만 추출
                text = content.get_text(separator=' ', strip=True)
                # 과도한 공백 제거
                text = re.sub(r'\s+', ' ', text)
                return text[:2000]  # 처음 2000자만 저장
            
            return None
            
        except Exception as e:
            self.logger.warning(f"상세 페이지 로드 실패: {url}")
            return None
    
    def _extract_tags(self, title: str, description: Optional[str]) -> List[str]:
        """
        제목과 내용에서 태그 추출
        
        Args:
            title: 공고 제목
            description: 공고 내용
            
        Returns:
            List[str]: 태그 리스트
        """
        tags = []
        text = f"{title} {description or ''}"
        
        # 간단한 키워드 매칭으로 태그 생성
        tag_keywords = {
            '수소': '수소',
            '연료전지': '연료전지',
            '마케팅': '마케팅지원',
            '수출': '글로벌',
            '성남': '지역-성남',
            '경기': '지역-경기',
            '창업': '창업지원',
        }
        
        for keyword, tag in tag_keywords.items():
            if keyword in text:
                tags.append(tag)
        
        return tags


# 스크립트로 직접 실행 시 테스트
if __name__ == '__main__':
    import yaml
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 설정 로드
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 크롤러 실행
    scraper = KStartupScraper(config)
    results = scraper.scrape()
    
    print(f"\n=== 크롤링 결과: {len(results)}개 공고 ===")
    for i, announcement in enumerate(results[:3], 1):  # 처음 3개만 출력
        print(f"\n{i}. {announcement['title']}")
        print(f"   마감일: {announcement['deadline']}")
        print(f"   URL: {announcement['url']}")