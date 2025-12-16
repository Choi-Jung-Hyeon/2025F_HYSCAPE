
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Optional
from scrapers.base_scraper import BaseScraper

class KStartupScraper(BaseScraper):
    """K-Startup 사업공고 크롤러"""

    def __init__(self, config: dict, site_name: str = 'k_startup'):
        super().__init__(config, site_name)
        self.base_url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
        self.detail_url_template = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing-detail.do?schPbanc={id}"
    
    def fetch_page(self, page: int = 1) -> Optional[str]:
        """
        K-Startup API 페이지 가져오기
        
        Args:
            page: 페이지 번호 (1부터 시작)
        
        Returns:
            HTML 텍스트 또는 None
        """
        params = {
            'page': page,
            'pbancClssCd': 'PBC020'  # 진행중인 공고
        }
        
        try:
            self.logger.info(f"K-Startup 페이지 {page} 요청 중...")
            response = requests.get(
                self.base_url,
                params=params,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            self.logger.info(f"✓ 페이지 {page} 가져오기 성공 (크기: {len(response.text)} bytes)")
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ 페이지 {page} 가져오기 실패: {e}")
            return None
    
    def extract_id_from_href(self, href: str) -> Optional[str]:
        """
        javascript:go_view(ID) 형태에서 ID 추출
        
        Args:
            href: 링크 속성 값
        
        Returns:
            추출된 ID 또는 None
        """
        if not href:
            return None
        
        # javascript:go_view(175755) → 175755
        match = re.search(r'go_view\((\d+)\)', href)
        if match:
            return match.group(1)
        return None
    
    def parse_notices(self, html: str) -> List[Dict]:
        """
        HTML에서 공고 목록 파싱
        
        Args:
            html: HTML 텍스트
        
        Returns:
            공고 딕셔너리 리스트
        """
        soup = BeautifulSoup(html, 'html.parser')
        notices = []
        
        # 모든 <li class="notice"> 찾기
        items = soup.find_all('li', class_='notice')
        self.logger.info(f"파싱 시작: {len(items)}개 공고 발견")
        
        for idx, item in enumerate(items, 1):
            try:
                # 제목
                tit_elem = item.find('p', class_='tit')
                title = tit_elem.get_text(strip=True) if tit_elem else None
                
                if not title:
                    self.logger.debug(f"  공고 {idx}: 제목 없음, 건너뜀")
                    continue
                
                # ID 추출 (링크에서)
                link_elem = item.find('a', href=True)
                href = link_elem['href'] if link_elem else None
                notice_id = self.extract_id_from_href(href)
                
                # 상세 URL 생성
                url = self.detail_url_template.format(id=notice_id) if notice_id else None
                
                # 카테고리
                category_elem = item.find('span', class_='flag')
                category = category_elem.get_text(strip=True) if category_elem else ''
                
                # D-day
                dday_elem = item.find('span', class_='day')
                dday = dday_elem.get_text(strip=True) if dday_elem else ''
                
                # 하단 정보 (기관명, 날짜 등)
                bottom_div = item.find('div', class_='bottom')
                agency = ''
                dates = []
                
                if bottom_div:
                    info_spans = bottom_div.find_all('span', class_='list')
                    for span in info_spans:
                        text = span.get_text(strip=True)
                        # 두 번째 span이 보통 기관명
                        if '등록일자' not in text and '시작일자' not in text and '마감일자' not in text and '조회' not in text:
                            if not agency or len(text) > len(agency):  # 더 긴 텍스트를 기관명으로
                                agency = text
                        # 날짜 정보
                        if '마감일자' in text:
                            dates.append(text.replace('마감일자', '').strip())
                
                notice = {
                    'title': title,
                    'url': url,
                    'category': category,
                    'agency': agency,
                    'dday': dday,
                    'source': 'K-Startup'
                }
                
                notices.append(notice)
                self.logger.debug(f"  ✓ 공고 {idx}: {title[:30]}...")
                
            except Exception as e:
                self.logger.error(f"  ✗ 공고 {idx} 파싱 실패: {e}")
                continue
        
        self.logger.info(f"✓ 파싱 완료: {len(notices)}개 공고 추출")
        return notices
    
    def fetch_announcements(self, max_pages: int = 3) -> List[Dict]:
        """
        사이트에서 공고 목록을 가져오는 메소드 (BaseScraper 추상 메소드 구현)

        Args:
            max_pages: 최대 크롤링 페이지 수

        Returns:
            공고 딕셔너리 리스트 (원시 데이터)
        """
        all_notices = []

        for page in range(1, max_pages + 1):
            html = self.fetch_page(page)
            if not html:
                self.logger.warning(f"페이지 {page} 건너뜀")
                continue

            notices = self.parse_notices(html)
            all_notices.extend(notices)

            self.logger.info(f"페이지 {page}: {len(notices)}개 공고 수집 (누적: {len(all_notices)}개)")

        self.logger.info(f"=" * 60)
        self.logger.info(f"K-Startup 크롤링 완료: 총 {len(all_notices)}개 공고")
        self.logger.info(f"=" * 60)

        return all_notices

    def parse_announcement(self, raw_data: Dict) -> Optional[Dict]:
        """
        개별 공고 데이터를 표준 포맷으로 파싱하는 메소드 (BaseScraper 추상 메소드 구현)

        Args:
            raw_data: 사이트별 원본 데이터

        Returns:
            표준화된 공고 정보 또는 None (파싱 실패 시)
        """
        try:
            # raw_data를 표준 포맷으로 변환
            return {
                'title': raw_data.get('title', ''),
                'url': raw_data.get('url', ''),
                'deadline': raw_data.get('dday', ''),  # D-day를 deadline으로 매핑
                'organization': raw_data.get('agency', ''),
                'description': raw_data.get('category', ''),  # 카테고리를 description으로 임시 매핑
                'tags': [raw_data.get('category', '')],
                'scraped_at': raw_data.get('source', 'K-Startup')
            }
        except Exception as e:
            self.logger.error(f"공고 파싱 실패: {e}")
            return None


if __name__ == '__main__':
    # 간단한 테스트
    import yaml

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 설정 로드
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    scraper = KStartupScraper(config, 'k_startup')
    notices = scraper.scrape()
    
    print("\n" + "=" * 80)
    print("수집된 공고 샘플 (최대 3개)")
    print("=" * 80)
    for notice in notices[:3]:
        print(f"제목: {notice['title']}")
        print(f"URL: {notice['url']}")
        print(f"마감일: {notice['deadline']}")
        print(f"기관: {notice['organization']}")
        print(f"설명: {notice['description']}")
        print(f"태그: {notice['tags']}")
        print(f"출처: {notice['source']}")
        print("-" * 80)