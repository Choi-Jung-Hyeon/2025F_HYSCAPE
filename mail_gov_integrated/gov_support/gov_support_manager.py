"""
정부지원사업 크롤링 통합 관리자
"""

import yaml
import logging
from typing import List, Dict, Optional
from datetime import datetime

from gov_support.k_startup_scraper import KStartupScraper
from gov_support.filter_strategy import FilterStrategy


class GovSupportManager:
    """
    정부지원사업 크롤링 통합 관리자

    여러 정부지원사업 사이트에서 공고를 수집하고,
    필터링 전략을 적용하여 추천 공고를 선별합니다.
    """

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Args:
            config_path: config.yaml 파일 경로
        """
        self.logger = logging.getLogger(__name__)

        # config.yaml 로드
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 필터 전략 초기화
        self.filter_strategy = FilterStrategy(config_path)

        # 스크래퍼 초기화
        self.scrapers = self._initialize_scrapers()

        self.logger.info(f"GovSupportManager 초기화: {len(self.scrapers)}개 스크래퍼 활성화")

    def _initialize_scrapers(self) -> Dict[str, object]:
        """
        활성화된 스크래퍼 초기화

        Returns:
            Dict: {site_name: scraper_instance}
        """
        scrapers = {}

        for site_name, site_config in self.config['sites'].items():
            if not site_config.get('enabled', False):
                self.logger.info(f"[{site_name}] 비활성화됨 - 건너뜀")
                continue

            try:
                # 현재는 K-Startup만 구현되어 있음
                if site_name == 'k_startup':
                    scraper = KStartupScraper(self.config)
                    scrapers[site_name] = scraper
                    self.logger.info(f"[{site_name}] 스크래퍼 초기화 완료")
                else:
                    self.logger.warning(f"[{site_name}] 스크래퍼 미구현 - 건너뜀")

            except Exception as e:
                self.logger.error(f"[{site_name}] 스크래퍼 초기화 실패: {e}")

        return scrapers

    def collect_all_notices(self) -> List[Dict]:
        """
        모든 활성화된 소스에서 공고 수집

        Returns:
            List[Dict]: 수집된 모든 공고 리스트
        """
        all_notices = []

        self.logger.info("=" * 60)
        self.logger.info("정부지원사업 공고 수집 시작")
        self.logger.info("=" * 60)

        for site_name, scraper in self.scrapers.items():
            try:
                self.logger.info(f"\n[{site_name}] 크롤링 시작...")
                notices = scraper.scrape()
                all_notices.extend(notices)
                self.logger.info(f"[{site_name}] {len(notices)}개 공고 수집 완료")

            except Exception as e:
                self.logger.error(f"[{site_name}] 크롤링 실패: {e}", exc_info=True)

        self.logger.info("=" * 60)
        self.logger.info(f"전체 수집 완료: 총 {len(all_notices)}개 공고")
        self.logger.info("=" * 60)

        return all_notices

    def get_recommended_notices(
        self,
        top_n: int = 5,
        min_score: int = 30
    ) -> List[Dict]:
        """
        추천 공고 수집 및 필터링

        Args:
            top_n: 반환할 최대 개수
            min_score: 최소 관련도 점수

        Returns:
            List[Dict]: 추천 공고 리스트 (관련도 순 정렬)
        """
        # 1. 모든 공고 수집
        all_notices = self.collect_all_notices()

        if not all_notices:
            self.logger.warning("수집된 공고가 없습니다.")
            return []

        # 2. 필터링 및 점수 계산
        recommended = self.filter_strategy.filter_notices(
            notices=all_notices,
            min_score=min_score,
            top_n=top_n
        )

        self.logger.info(f"\n추천 공고 {len(recommended)}개 선정 완료")
        for i, notice in enumerate(recommended, 1):
            self.logger.info(f"  {i}. [{notice['relevance_score']}점] {notice['title'][:40]}...")

        return recommended

    def generate_html_section(
        self,
        notices: Optional[List[Dict]] = None,
        top_n: int = 5
    ) -> str:
        """
        이메일용 HTML 섹션 생성

        Args:
            notices: 공고 리스트 (None이면 자동으로 수집)
            top_n: 표시할 최대 개수

        Returns:
            str: HTML 문자열 (이메일 본문에 삽입 가능)
        """
        if notices is None:
            notices = self.get_recommended_notices(top_n=top_n)

        if not notices:
            return """
            <div style="margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                <h2 style="color: #495057;">🎯 정부지원사업 추천</h2>
                <p style="color: #6c757d;">추천할 공고가 없습니다.</p>
            </div>
            """

        # HTML 생성
        html_parts = [
            '<div style="margin: 20px 0;">',
            '  <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">',
            '    🎯 정부지원사업 추천 (AI 분석)',
            '  </h2>',
            '  <p style="color: #7f8c8d; margin: 10px 0;">',
            f'    수소·재생에너지 분야에 적합한 {len(notices)}개 사업을 추천합니다.',
            '  </p>',
            ''
        ]

        for i, notice in enumerate(notices, 1):
            score = notice.get('relevance_score', 0)
            title = notice.get('title', '제목 없음')
            url = notice.get('url', '#')
            organization = notice.get('organization', '미확인')
            deadline = notice.get('deadline', '미정')
            tags = notice.get('tags', [])
            source = notice.get('source', '출처 미상')

            # 점수에 따른 배지 색상
            if score >= 70:
                badge_color = '#27ae60'  # 초록
                badge_text = '매우 적합'
            elif score >= 50:
                badge_color = '#3498db'  # 파랑
                badge_text = '적합'
            elif score >= 30:
                badge_color = '#f39c12'  # 주황
                badge_text = '검토 추천'
            else:
                badge_color = '#95a5a6'  # 회색
                badge_text = '참고'

            # 카드 HTML
            card_html = f"""
  <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <div style="background-color: white; padding: 20px; border-radius: 8px;">
      <!-- 헤더: 순위 + 점수 배지 -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-size: 24px; font-weight: bold; color: #667eea;">#{i}</span>
        <span style="background-color: {badge_color}; color: white; padding: 6px 12px;
                     border-radius: 20px; font-size: 12px; font-weight: bold;">
          {badge_text} ({score}점)
        </span>
      </div>

      <!-- 제목 -->
      <h3 style="margin: 10px 0; color: #2c3e50; font-size: 18px;">
        <a href="{url}" style="color: #2c3e50; text-decoration: none;">
          {title}
        </a>
      </h3>

      <!-- 메타 정보 -->
      <div style="margin: 12px 0; padding: 10px; background-color: #f8f9fa; border-radius: 6px;">
        <p style="margin: 5px 0; color: #495057; font-size: 14px;">
          <strong>📍 기관:</strong> {organization}
        </p>
        <p style="margin: 5px 0; color: #495057; font-size: 14px;">
          <strong>⏰ 마감:</strong> {deadline}
        </p>
        <p style="margin: 5px 0; color: #495057; font-size: 14px;">
          <strong>🏷️ 출처:</strong> {source}
        </p>
      </div>

      <!-- 태그 -->
      {"<div style='margin: 10px 0;'>" + "".join([f"<span style='display: inline-block; background-color: #e3f2fd; color: #1976d2; padding: 4px 10px; margin: 3px; border-radius: 12px; font-size: 12px;'>#{tag}</span>" for tag in tags[:5]]) + "</div>" if tags else ""}

      <!-- 상세보기 버튼 -->
      <div style="margin-top: 15px; text-align: right;">
        <a href="{url}" style="display: inline-block; background-color: #667eea; color: white;
                                padding: 10px 20px; text-decoration: none; border-radius: 6px;
                                font-weight: bold; font-size: 14px;">
          상세보기 →
        </a>
      </div>
    </div>
  </div>
"""
            html_parts.append(card_html)

        html_parts.append('</div>')

        return '\n'.join(html_parts)


# 테스트 코드
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 관리자 초기화
    manager = GovSupportManager('config.yaml')

    # 추천 공고 수집
    print("\n\n" + "=" * 80)
    print("정부지원사업 추천 시스템 테스트")
    print("=" * 80)

    recommended = manager.get_recommended_notices(top_n=5, min_score=30)

    print(f"\n\n추천 공고 {len(recommended)}개:")
    for i, notice in enumerate(recommended, 1):
        print(f"\n{i}. [{notice['relevance_score']}점] {notice['title']}")
        print(f"   기관: {notice['organization']}")
        print(f"   마감: {notice['deadline']}")
        print(f"   URL: {notice['url'][:80]}...")

    # HTML 생성 테스트
    print("\n\n" + "=" * 80)
    print("HTML 생성 테스트")
    print("=" * 80)
    html = manager.generate_html_section(notices=recommended)
    print(f"\n생성된 HTML 길이: {len(html)} 문자")
    print("\nHTML 미리보기 (처음 500자):")
    print(html[:500] + "...")
