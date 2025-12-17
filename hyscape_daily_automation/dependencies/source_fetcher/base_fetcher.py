# source_fetcher/base_fetcher.py
"""
모든 Source Fetcher의 추상 베이스 클래스
- SOLID 원칙에 따른 설계
- 확장 가능한 인터페이스 제공
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from datetime import datetime

class BaseSourceFetcher(ABC):
    """
    추상 베이스 클래스: 모든 Fetcher가 상속받아야 함
    """
    
    def __init__(self, source_name: str, url: str, **kwargs):
        """
        Args:
            source_name: 소스 이름 (예: "월간수소경제")
            url: 소스 URL
            **kwargs: 추가 설정 (헤더, 타임아웃 등)
        """
        self.source_name = source_name
        self.url = url
        self.config = kwargs
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(f"Fetcher.{self.source_name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    def fetch_articles(self, max_articles: int = 5) -> List[Dict]:
        """
        기사 목록을 가져오는 메인 메서드 (하위 클래스에서 반드시 구현)
        
        Returns:
            List[Dict]: [
                {
                    'title': '기사 제목',
                    'url': '기사 URL',
                    'published': '발행일시',  # Optional
                    'source': '소스명'
                },
                ...
            ]
        """
        pass
    
    def validate_article(self, article: Dict) -> bool:
        """
        기사 데이터 유효성 검사 (공통 로직)
        
        Args:
            article: 검증할 기사 데이터
            
        Returns:
            bool: 유효하면 True, 아니면 False
        """
        required_fields = ['title', 'url', 'source']
        
        # 필수 필드 체크
        for field in required_fields:
            if field not in article or not article[field]:
                self.logger.warning(f"Invalid article: missing {field}")
                return False
        
        # URL 형식 체크 (간단한 검증)
        if not article['url'].startswith(('http://', 'https://')):
            self.logger.warning(f"Invalid URL: {article['url']}")
            return False
        
        return True
    
    def log_success(self, count: int):
        """성공 로그"""
        self.logger.info(f"✅ {self.source_name}: {count}개 기사 수집 성공")
    
    def log_error(self, error: Exception):
        """
        에러 로그 및 실패 파일에 기록
        
        Args:
            error: 발생한 예외
        """
        error_msg = str(error)
        self.logger.error(f"❌ {self.source_name}: {error_msg}")
        
        # 실패 로그 파일에 기록
        try:
            with open("logs/failed_sources.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {self.source_name}|{self.url}|{error_msg}\n")
        except Exception as log_error:
            self.logger.error(f"로그 기록 실패: {log_error}")
    
    def __repr__(self) -> str:
        """디버깅용 문자열 표현"""
        return f"<{self.__class__.__name__}(source='{self.source_name}')>"