"""
정부 지원 사업 추천 시스템 - 메인 실행 스크립트

사용법:
    python main.py
"""

import yaml
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 각 모듈 import
from scrapers.base_scraper import BaseScraper
from scrapers.k_startup_scraper import KStartupScraper
from filters.keyword_filter import KeywordFilter


class GovernmentSupportTracker:
    """
    정부 지원 사업 추천 시스템 메인 클래스
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Args:
            config_path: 설정 파일 경로
        """
        # 설정 로드
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 로깅 설정
        self._setup_logging()
        
        # 필터 엔진 초기화
        self.filter_engine = KeywordFilter(self.config)
        
        # 히스토리 파일 경로
        self.history_path = Path(self.config['system']['history_file'])
        self.history_path.parent.mkdir(exist_ok=True)
        
        # 크롤러 레지스트리 (Strategy Pattern)
        self.scraper_registry = {
            'KStartupScraper': KStartupScraper,
            # 추후 추가: 'IRISScraper': IRISScraper,
            # 추후 추가: 'BizinfoScraper': BizinfoScraper,
        }
        
        self.logger = logging.getLogger('Main')
        
    def _setup_logging(self):
        """로깅 설정"""
        log_level = self.config['system'].get('log_level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tracker.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def run(self):
        """
        전체 시스템 실행
        1. 활성화된 사이트들 크롤링
        2. 키워드 필터링
        3. 중복 제거
        4. 알림 발송
        """
        self.logger.info("=" * 60)
        self.logger.info("정부 지원 사업 추천 시스템 시작")
        self.logger.info("=" * 60)
        
        # 1. 크롤링
        all_announcements = self._scrape_all_sites()
        self.logger.info(f"총 {len(all_announcements)}개 공고 수집 완료")
        
        if not all_announcements:
            self.logger.warning("수집된 공고가 없습니다.")
            return
        
        # 2. 필터링
        filtered_announcements = self.filter_engine.filter_announcements(all_announcements)
        self.logger.info(f"필터링 후: {len(filtered_announcements)}개 공고 선택")
        
        if not filtered_announcements:
            self.logger.info("필터 조건에 맞는 공고가 없습니다.")
            return
        
        # 3. 중복 제거 (히스토리 기반)
        new_announcements = self._remove_duplicates(filtered_announcements)
        self.logger.info(f"신규 공고: {len(new_announcements)}개")
        
        if not new_announcements:
            self.logger.info("새로운 공고가 없습니다.")
            return
        
        # 4. 결과 출력
        self._print_results(new_announcements)
        
        # 5. 히스토리 업데이트
        self._update_history(new_announcements)
        
        # 6. Slack 알림 (옵션)
        if self.config['slack']['enabled']:
            self._send_slack_notification(new_announcements)
        
        self.logger.info("=" * 60)
        self.logger.info("작업 완료")
        self.logger.info("=" * 60)
    
    def _scrape_all_sites(self) -> List[Dict]:
        """
        활성화된 모든 사이트 크롤링
        
        Returns:
            List[Dict]: 수집된 전체 공고 리스트
        """
        all_announcements = []
        
        for site_name, site_config in self.config['sites'].items():
            if not site_config.get('enabled', True):
                self.logger.info(f"[{site_config['name']}] 비활성화됨 - 스킵")
                continue
            
            scraper_class_name = site_config['scraper_class']
            
            # 크롤러 클래스 가져오기
            if scraper_class_name not in self.scraper_registry:
                self.logger.warning(f"[{site_config['name']}] 크롤러 클래스 '{scraper_class_name}' 미구현 - 스킵")
                continue
            
            # 크롤러 인스턴스 생성
            scraper_class = self.scraper_registry[scraper_class_name]
            scraper = scraper_class(self.config)
            
            # 크롤링 실행
            announcements = scraper.scrape()
            all_announcements.extend(announcements)
        
        return all_announcements
    
    def _remove_duplicates(self, announcements: List[Dict]) -> List[Dict]:
        """
        히스토리 파일을 기반으로 중복 공고 제거
        
        Args:
            announcements: 필터링된 공고 리스트
            
        Returns:
            List[Dict]: 신규 공고만 포함된 리스트
        """
        # 히스토리 로드
        history = self._load_history()
        
        new_announcements = []
        
        for announcement in announcements:
            url = announcement['url']
            
            # URL이 히스토리에 없으면 신규 공고
            if url not in history:
                new_announcements.append(announcement)
        
        return new_announcements
    
    def _load_history(self) -> Dict[str, Dict]:
        """
        히스토리 파일 로드
        
        Returns:
            Dict[str, Dict]: {url: {title, scraped_at, ...}}
        """
        if not self.history_path.exists():
            return {}
        
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"히스토리 로드 실패: {str(e)}")
            return {}
    
    def _update_history(self, new_announcements: List[Dict]):
        """
        히스토리 파일 업데이트
        
        Args:
            new_announcements: 신규 공고 리스트
        """
        history = self._load_history()
        
        # 신규 공고 추가
        for announcement in new_announcements:
            history[announcement['url']] = {
                'title': announcement['title'],
                'scraped_at': announcement['scraped_at'],
                'source': announcement['source'],
            }
        
        # 파일 저장
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"히스토리 업데이트 완료: {len(history)}개 공고")
    
    def _print_results(self, announcements: List[Dict]):
        """
        결과를 콘솔에 출력
        
        Args:
            announcements: 출력할 공고 리스트
        """
        print("\n" + "=" * 80)
        print(f"🎯 추천 공고: {len(announcements)}건")
        print("=" * 80)
        
        for i, ann in enumerate(announcements, 1):
            print(f"\n[{i}] {ann['title']}")
            print(f"    출처: {ann['source']}")
            print(f"    마감일: {ann['deadline']}")
            print(f"    매칭 점수: {ann['match_score']}점")
            print(f"    매칭 키워드: {', '.join(ann['matched_keywords'])}")
            print(f"    URL: {ann['url']}")
        
        # 키워드 통계
        print("\n" + "=" * 80)
        print("📊 키워드 통계")
        print("=" * 80)
        stats = self.filter_engine.get_keyword_statistics(announcements)
        for keyword, count in list(stats.items())[:10]:  # 상위 10개
            print(f"  {keyword}: {count}회")
    
    def _send_slack_notification(self, announcements: List[Dict]):
        """
        Slack으로 알림 발송
        
        Args:
            announcements: 알림 보낼 공고 리스트
        """
        # TODO: Slack SDK를 사용한 알림 구현
        self.logger.info("Slack 알림 발송 예정 (미구현)")
        pass


def main():
    """메인 실행 함수"""
    tracker = GovernmentSupportTracker()
    tracker.run()


if __name__ == '__main__':
    main()