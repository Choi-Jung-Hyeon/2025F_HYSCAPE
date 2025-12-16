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

    def calculate_relevance(self, notice: Dict) -> int:
        """
        공고의 관련도 점수 계산 (0-100점)

        채점 기준:
        - tech_keywords 매칭: 30점/개
        - support_keywords 매칭: 10점/개
        - R&D/연구 카테고리: +15점
        - 스타트업/창업 카테고리: +10점

        Args:
            notice: 공고 정보 딕셔너리
                   (title, description, tags, organization 등 포함)

        Returns:
            int: 관련도 점수 (0-100점)
        """
        score = 0
        matched_keywords = {
            'tech': [],
            'support': [],
            'qualification': []
        }

        # 검색 대상 텍스트 결합 (제목 + 설명 + 태그 + 기관명)
        search_text = ' '.join([
            notice.get('title', ''),
            notice.get('description', ''),
            ' '.join(notice.get('tags', [])),
            notice.get('organization', '')
        ]).lower()

        # 1. tech_keywords 매칭: 30점/개
        for keyword in self.tech_keywords:
            if keyword.lower() in search_text:
                score += 30
                matched_keywords['tech'].append(keyword)

        # 2. support_keywords 매칭: 10점/개
        for keyword in self.support_keywords:
            if keyword.lower() in search_text:
                score += 10
                matched_keywords['support'].append(keyword)

        # 3. qualification_keywords 매칭: 5점/개 (보너스)
        for keyword in self.qualification_keywords:
            if keyword.lower() in search_text:
                score += 5
                matched_keywords['qualification'].append(keyword)

        # 4. R&D/연구 카테고리: +15점
        rd_keywords = ['r&d', 'r＆d', '연구개발', '연구 개발', '연구', '개발과제']
        if any(kw in search_text for kw in rd_keywords):
            score += 15

        # 5. 스타트업/창업 카테고리: +10점
        startup_keywords = ['스타트업', '창업', 'startup', '초기기업', '벤처']
        if any(kw in search_text for kw in startup_keywords):
            score += 10

        # 최대 100점으로 제한
        score = min(score, 100)

        # 매칭된 키워드 정보 로깅
        if score > 0:
            self.logger.debug(f"[{score}점] {notice['title'][:30]}... | "
                            f"tech={matched_keywords['tech']}, "
                            f"support={matched_keywords['support']}")

        return score

    def filter_notices(
        self,
        notices: List[Dict],
        min_score: int = 30,
        top_n: int = 5
    ) -> List[Dict]:
        """
        공고 목록을 필터링하여 관련도 높은 상위 N개 반환

        Args:
            notices: 공고 딕셔너리 리스트
            min_score: 최소 점수 (이 점수 이상만 포함)
            top_n: 반환할 최대 개수

        Returns:
            List[Dict]: 필터링 및 정렬된 공고 리스트
                       각 공고에 'relevance_score' 키가 추가됨
        """
        # 각 공고에 관련도 점수 계산 및 추가
        scored_notices = []
        for notice in notices:
            score = self.calculate_relevance(notice)
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
