"""
정부 지원 사업 크롤러 - Base Scraper
모든 사이트별 크롤러가 상속받는 추상 부모 클래스

Strategy Pattern을 사용하여 확장 가능한 구조 구현
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import logging


class BaseScraper(ABC):
    """
    모든 정부 지원 사업 크롤러의 부모 클래스
    
    새로운 사이트를 추가할 때는:
    1. 이 클래스를 상속받아 새로운 Scraper 클래스 생성
    2. fetch_announcements()와 parse_announcement() 메소드 구현
    3. config.yaml에 사이트 정보 추가
    """
    
    def __init__(self, config: Dict, site_name: str):
        """
        Args:
            config: config.yaml에서 로드된 전체 설정
            site_name: 사이트 식별자 (예: 'k_startup', 'iris')
        """
        self.config = config
        self.site_name = site_name
        self.site_config = config['sites'][site_name]
        
        self.name = self.site_config['name']
        self.url = self.site_config['url']
        self.filter_strategy = self.site_config['filter_strategy']
        
        self.logger = logging.getLogger(f"Scraper.{self.name}")
        
    @abstractmethod
    def fetch_announcements(self) -> List[Dict]:
        """
        사이트에서 공고 목록을 가져오는 메소드 (각 Scraper가 구현 필수)
        
        Returns:
            List[Dict]: 공고 정보 리스트
            각 Dict는 다음 키를 포함해야 함:
            {
                'title': str,           # 공고 제목
                'url': str,             # 공고 상세 URL
                'deadline': str,        # 마감일 (YYYY-MM-DD)
                'organization': str,    # 주관 기관
                'description': str,     # 공고 설명/내용
                'tags': List[str],      # 분야/카테고리 태그
                'scraped_at': str,      # 크롤링 시각
            }
        """
        pass
    
    @abstractmethod
    def parse_announcement(self, raw_data: Dict) -> Optional[Dict]:
        """
        개별 공고 데이터를 표준 포맷으로 파싱하는 메소드
        
        Args:
            raw_data: 사이트별 원본 데이터
            
        Returns:
            Optional[Dict]: 표준화된 공고 정보 또는 None (파싱 실패 시)
        """
        pass
    
    def scrape(self) -> List[Dict]:
        """
        전체 크롤링 프로세스 실행 (공통 로직)
        
        Returns:
            List[Dict]: 크롤링된 공고 리스트
        """
        self.logger.info(f"[{self.name}] 크롤링 시작...")
        
        try:
            # 1. 공고 목록 가져오기
            announcements = self.fetch_announcements()
            self.logger.info(f"[{self.name}] {len(announcements)}개 공고 발견")
            
            # 2. 각 공고를 표준 포맷으로 파싱
            parsed_announcements = []
            for raw_data in announcements:
                parsed = self.parse_announcement(raw_data)
                if parsed:
                    parsed['source'] = self.name
                    parsed['source_site'] = self.site_name
                    parsed['filter_strategy'] = self.filter_strategy
                    parsed_announcements.append(parsed)
            
            self.logger.info(f"[{self.name}] {len(parsed_announcements)}개 공고 파싱 완료")
            return parsed_announcements
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 크롤링 실패: {str(e)}", exc_info=True)
            return []
    
    def validate_announcement(self, announcement: Dict) -> bool:
        """
        공고 데이터 유효성 검사
        
        Args:
            announcement: 검사할 공고 데이터
            
        Returns:
            bool: 유효하면 True
        """
        required_fields = ['title', 'url', 'deadline', 'description']
        
        for field in required_fields:
            if field not in announcement or not announcement[field]:
                self.logger.warning(f"필수 필드 누락: {field}")
                return False
        
        return True
    
    def get_headers(self) -> Dict[str, str]:
        """
        HTTP 요청에 사용할 기본 헤더
        
        Returns:
            Dict: 헤더 딕셔너리
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(site={self.name}, strategy={self.filter_strategy})>"