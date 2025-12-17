"""
K-Startup 크롤러 구현체 (디버깅 모드 추가)
https://www.k-startup.go.kr/ 사업공고 크롤링
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
import time

from .base_scraper import BaseScraper


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
        self.list_url = f"{self.base_url}/web/contents/bizpbanc-ongoing.do"  # 모집중인 공고
        self.detail_url_template = f"{self.base_url}/web/contents/bizpbanc-ongoing-detail.do?schPbanc={{id}}"
        self.max_pages = 3  # 최근 3페이지만 크롤링
        
        # 🐛 디버깅 모드 설정
        self.debug_mode = True  # HTML 파일 저장 여부
        
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
                # 페이지 요청 (bizpbanc-ongoing.do는 GET 파라미터 없이 동작)
                params = {
                    'page': page,
                    'pbancClssCd': 'PBC020'  # 진행중인 공고
                }
                
                response = requests.get(
                    self.list_url,
                    params=params,
                    headers=self.get_headers(),
                    timeout=10
                )
                response.raise_for_status()
                
                # 🐛 디버깅: HTML 파일로 저장
                if self.debug_mode and page == 1:
                    debug_file = f"debug_kstartup_page{page}.html"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.logger.info(f"🐛 디버그 HTML 저장: {debug_file}")
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 공고 리스트 찾기
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
        
        # 🔍 여러 가능한 HTML 구조 시도
        selectors = [
            'li.notice',                            # K-Startup 공고 리스트 (실제 구조)
            'table.board-list tbody tr',           # 테이블 형식 1
            'table tbody tr',                       # 테이블 형식 2
            'div.board-list ul li',                 # 리스트 형식 1
            'ul.notice-list li',                    # 리스트 형식 2
            'div.list-wrap div.item',               # 카드 형식 1
            'div.notice-item',                      # 카드 형식 2
        ]
        
        rows = []
        for selector in selectors:
            rows = soup.select(selector)
            if rows:
                self.logger.info(f"✅ 매칭된 셀렉터: '{selector}' ({len(rows)}개 항목)")
                break
        
        if not rows:
            self.logger.warning("⚠️ 공고 목록을 찾을 수 없습니다. HTML 구조 확인 필요")
            # 🐛 디버깅: 페이지 구조 출력
            self._debug_html_structure(soup)
            return []
        
        for row in rows:
            try:
                # K-Startup 전용: p.tit에서 제목 추출
                title_elem = row.select_one('p.tit')
                if not title_elem:
                    # 대체 셀렉터 시도
                    title_elem = (
                        row.select_one('a') or
                        row.select_one('.title a') or
                        row.select_one('td a')
                    )

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # K-Startup 전용: javascript:go_view(ID) 형태에서 ID 추출
                link_elem = row.select_one('a[href*="go_view"]')
                if link_elem:
                    href = link_elem.get('href', '')
                    # javascript:go_view(175755) → 175755 추출
                    match = re.search(r'go_view\((\d+)\)', href)
                    if match:
                        notice_id = match.group(1)
                        url = self.detail_url_template.format(id=notice_id)
                    else:
                        url = ''
                else:
                    # 일반 링크 처리
                    link_elem = row.select_one('a')
                    if link_elem:
                        url = link_elem.get('href', '')
                        if url and not url.startswith('http'):
                            url = self.base_url + url
                    else:
                        url = ''
                
                # 마감일 추출
                deadline = self._extract_deadline(row)
                
                # 주관기관 추출
                organization = self._extract_organization(row)
                
                announcements.append({
                    'title': title,
                    'url': url,
                    'deadline': deadline,
                    'organization': organization,
                    'raw_html': str(row)[:500],  # 처음 500자만 저장
                })
                
            except Exception as e:
                self.logger.warning(f"항목 파싱 실패: {str(e)}")
                continue
        
        return announcements
    
    def _debug_html_structure(self, soup: BeautifulSoup):
        """
        HTML 구조 디버깅 정보 출력
        
        Args:
            soup: BeautifulSoup 객체
        """
        self.logger.info("=" * 60)
        self.logger.info("🐛 HTML 구조 디버깅")
        self.logger.info("=" * 60)
        
        # 주요 태그 개수 확인
        tags_to_check = ['table', 'ul', 'div.list', 'div.board', 'article', 'section']
        for tag in tags_to_check:
            count = len(soup.select(tag))
            if count > 0:
                self.logger.info(f"  {tag}: {count}개")
        
        # 링크 개수 확인
        links = soup.find_all('a', href=True)
        self.logger.info(f"  전체 링크(<a>): {len(links)}개")
        
        # 첫 번째 링크 샘플
        if links:
            sample = links[0]
            self.logger.info(f"  링크 샘플: {sample.get_text(strip=True)[:50]}")
        
        self.logger.info("=" * 60)
        self.logger.info("💡 debug_kstartup_page1.html 파일을 열어서 구조를 확인하세요!")
        self.logger.info("=" * 60)
    
    def _extract_deadline(self, element) -> str:
        """
        마감일 추출 및 표준화

        Args:
            element: HTML 요소

        Returns:
            str: YYYY-MM-DD 형식 날짜
        """
        # K-Startup 전용: div.bottom span.list에서 마감일자 찾기
        bottom_div = element.select_one('div.bottom')
        if bottom_div:
            info_spans = bottom_div.find_all('span', class_='list')
            for span in info_spans:
                text = span.get_text(strip=True)
                if '마감일자' in text:
                    # "마감일자2025-01-15" 형태에서 날짜 추출
                    match = re.search(r'(\d{4})[-.]?(\d{2})[-.]?(\d{2})', text)
                    if match:
                        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

        # D-day 정보 추출 (대체)
        dday_elem = element.select_one('span.day')
        if dday_elem:
            return dday_elem.get_text(strip=True)  # "D-7" 같은 형태

        return "미정"
    
    def _extract_organization(self, element) -> str:
        """
        주관기관 추출

        Args:
            element: HTML 요소

        Returns:
            str: 기관명
        """
        # K-Startup 전용: div.bottom span.list에서 기관명 찾기
        bottom_div = element.select_one('div.bottom')
        if bottom_div:
            info_spans = bottom_div.find_all('span', class_='list')
            for span in info_spans:
                text = span.get_text(strip=True)
                # 등록일자, 마감일자, 조회 정보가 아닌 것이 기관명
                if all(keyword not in text for keyword in ['등록일자', '시작일자', '마감일자', '조회']):
                    if len(text) > 1:  # 1글자 이상
                        return text

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
                'description': description or raw_data['title'],
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
            
            # 본문 내용 추출 (여러 셀렉터 시도)
            selectors = [
                '.content', '.view-content', '#content',
                '.article-content', '.detail-content',
                'div.cont', 'div.view'
            ]
            
            content = None
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
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
    for i, announcement in enumerate(results[:3], 1):
        print(f"\n{i}. {announcement['title']}")
        print(f"   마감일: {announcement['deadline']}")
        print(f"   URL: {announcement['url']}")