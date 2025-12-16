"""
정부지원사업 필터링 및 관련도 점수 계산 모듈
"""

import yaml
import logging
from typing import List, Dict


class FilterStrategy:
    """
    정부지원사업 필터링 및 관련도 점수 계산

    config.yaml의 키워드를 기반으로 공고의 관련도를 점수화하고
    필터링하여 추천 공고를 선별합니다.
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

        # 키워드 로드
        self.tech_keywords = self.config['keywords']['tech']
        self.support_keywords = self.config['keywords']['support']
        self.qualification_keywords = self.config['keywords']['qualification']

        self.logger.info(f"필터 전략 초기화: tech={len(self.tech_keywords)}, "
                        f"support={len(self.support_keywords)}, "
                        f"qual={len(self.qualification_keywords)}개 키워드")

    def calculate_relevance(self, notice: Dict, filter_type: str = 'B') -> int:
        """
        공고의 관련도 점수 계산 (개선 버전)

        채점 기준:
        - 기본 점수: 5점 (모든 공고)
        - tech_keywords 매칭: 20점/개 (완화)
        - support_keywords 매칭: 10점/개
        - 카테고리 보너스: 5-20점 (대폭 강화)

        Args:
            notice: 공고 정보 딕셔너리
            filter_type: 'A' (엄격) 또는 'B' (유연)

        Returns:
            int: 관련도 점수 (0-100점)
        """
        title = notice.get('title', '').lower()
        description = notice.get('description', '').lower()
        tags = ' '.join(notice.get('tags', [])).lower()
        organization = notice.get('organization', '').lower()

        search_text = f"{title} {description} {tags} {organization}"

        # 기본 점수 (모든 공고에 최소 5점)
        score = 5

        # 1. 기술 키워드 매칭 (가중치 낮춤: 30 → 20)
        tech_matches = sum(1 for kw in self.tech_keywords if kw.lower() in search_text)
        score += tech_matches * 20

        # 2. 지원 키워드 매칭
        support_matches = sum(1 for kw in self.support_keywords if kw.lower() in search_text)
        score += support_matches * 10

        # 3. 자격 키워드 매칭 (보너스)
        qualification_matches = sum(1 for kw in self.qualification_keywords if kw.lower() in search_text)
        score += qualification_matches * 5

        # 4. 카테고리 보너스 점수 (대폭 강화)
        category_bonuses = {
            '창업': 20,
            '스타트업': 20,
            '벤처': 15,
            'r&d': 15,
            '연구': 15,
            '기술': 10,
            '사업화': 10,
            '실증': 10,
            '시설': 5,
            '공간': 5,
            '보육': 5,
            '중소기업': 10,
            '지원금': 8,
            '보조금': 8
        }

        for keyword, bonus in category_bonuses.items():
            if keyword in search_text:
                score += bonus
                break  # 하나만 적용

        # 5. Type A (엄격) 필터링: 기술 키워드 필수
        if filter_type == 'A' and tech_matches == 0:
            return 0

        # 최대 100점으로 제한
        score = min(score, 100)

        # 매칭 정보 로깅
        if score >= 10:
            self.logger.debug(f"[{score}점] {notice.get('title', '')[:40]}... | "
                            f"tech={tech_matches}, support={support_matches}")

        return score

    def filter_notices(
        self,
        notices: List[Dict],
        filter_type: str = 'B',
        min_score: int = 10,
        top_n: int = 5
    ) -> List[Dict]:
        """
        공고 목록을 필터링하여 관련도 높은 상위 N개 반환

        Args:
            notices: 공고 딕셔너리 리스트
            filter_type: 'A' (엄격) 또는 'B' (유연)
            min_score: 최소 점수 (기본값 10으로 완화)
            top_n: 반환할 최대 개수

        Returns:
            List[Dict]: 필터링 및 정렬된 공고 리스트
                       각 공고에 'relevance_score' 키가 추가됨
        """
        # 각 공고에 관련도 점수 계산 및 추가
        scored_notices = []
        for notice in notices:
            score = self.calculate_relevance(notice, filter_type=filter_type)
            if score >= min_score:
                notice_with_score = notice.copy()
                notice_with_score['relevance_score'] = score
                scored_notices.append(notice_with_score)

        # 점수 내림차순 정렬
        scored_notices.sort(key=lambda x: x['relevance_score'], reverse=True)

        # 상위 N개 선택
        result = scored_notices[:top_n]

        self.logger.info(f"필터링 결과: {len(notices)}개 → {len(scored_notices)}개 (min_score={min_score}) "
                        f"→ 상위 {len(result)}개 선택")

        return result

    def get_keyword_matches(self, notice: Dict) -> Dict[str, List[str]]:
        """
        공고에 매칭된 키워드 목록 반환 (디버깅 및 상세 정보용)

        Args:
            notice: 공고 정보 딕셔너리

        Returns:
            Dict: {'tech': [...], 'support': [...], 'qualification': [...]}
        """
        matched = {
            'tech': [],
            'support': [],
            'qualification': []
        }

        search_text = ' '.join([
            notice.get('title', ''),
            notice.get('description', ''),
            ' '.join(notice.get('tags', [])),
            notice.get('organization', '')
        ]).lower()

        for keyword in self.tech_keywords:
            if keyword.lower() in search_text:
                matched['tech'].append(keyword)

        for keyword in self.support_keywords:
            if keyword.lower() in search_text:
                matched['support'].append(keyword)

        for keyword in self.qualification_keywords:
            if keyword.lower() in search_text:
                matched['qualification'].append(keyword)

        return matched


# 테스트 코드
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 필터 전략 초기화
    filter_strategy = FilterStrategy('config.yaml')

    # 테스트 공고 데이터
    test_notices = [
        {
            'title': '수소 연료전지 R&D 사업',
            'description': '수소 생산 및 저장 기술 개발',
            'tags': ['수소', 'R&D'],
            'organization': '과학기술정보통신부'
        },
        {
            'title': '스타트업 마케팅 지원 사업',
            'description': '성남 소재 창업기업 대상',
            'tags': ['창업지원'],
            'organization': '성남시'
        },
        {
            'title': '일반 행정 공고',
            'description': '행정 관련 공고',
            'tags': [],
            'organization': '행정안전부'
        }
    ]

    print("\n=== 관련도 점수 계산 테스트 ===")
    for notice in test_notices:
        score = filter_strategy.calculate_relevance(notice)
        matches = filter_strategy.get_keyword_matches(notice)
        print(f"\n제목: {notice['title']}")
        print(f"점수: {score}점")
        print(f"매칭: {matches}")

    print("\n\n=== 필터링 테스트 (min_score=30, top_n=2) ===")
    filtered = filter_strategy.filter_notices(test_notices, min_score=30, top_n=2)
    for i, notice in enumerate(filtered, 1):
        print(f"{i}. [{notice['relevance_score']}점] {notice['title']}")
