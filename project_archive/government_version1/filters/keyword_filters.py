"""
키워드 필터링 로직
Type A: 기술 중심 (IRIS) - 핵심 기술 키워드 필수
Type B: 지원 중심 (K-Startup, Bizinfo) - 유연한 매칭
"""

from typing import Dict, List
import logging


class KeywordFilter:
    """
    공고 필터링을 담당하는 클래스
    config.yaml의 필터 전략에 따라 다른 로직 적용
    """
    
    def __init__(self, config: Dict):
        """
        Args:
            config: config.yaml에서 로드된 전체 설정
        """
        self.config = config
        self.keywords = config['keywords']
        self.logger = logging.getLogger('KeywordFilter')
        
    def filter_announcements(self, announcements: List[Dict]) -> List[Dict]:
        """
        공고 리스트를 필터링하여 관련 공고만 반환
        
        Args:
            announcements: 크롤링된 전체 공고 리스트
            
        Returns:
            List[Dict]: 필터링된 공고 리스트 (각 공고에 match_score와 matched_keywords 추가)
        """
        filtered = []
        
        for announcement in announcements:
            strategy = announcement.get('filter_strategy', 'type_b')
            
            if strategy == 'type_a':
                result = self._apply_type_a_filter(announcement)
            else:  # type_b
                result = self._apply_type_b_filter(announcement)
            
            if result['is_match']:
                announcement['match_score'] = result['score']
                announcement['matched_keywords'] = result['matched_keywords']
                announcement['match_reason'] = result['reason']
                filtered.append(announcement)
        
        # 매칭 점수 순으로 정렬
        filtered.sort(key=lambda x: x['match_score'], reverse=True)
        
        self.logger.info(f"필터링 완료: {len(announcements)}개 중 {len(filtered)}개 선택")
        return filtered
    
    def _apply_type_a_filter(self, announcement: Dict) -> Dict:
        """
        Type A 필터 적용: 기술 중심 (Strict)
        핵심 기술 키워드가 반드시 1개 이상 포함되어야 함
        
        Args:
            announcement: 공고 정보
            
        Returns:
            Dict: {'is_match': bool, 'score': int, 'matched_keywords': List[str], 'reason': str}
        """
        text = f"{announcement['title']} {announcement['description']}".lower()
        
        matched_tech = []
        
        # 기술 키워드 매칭
        for keyword in self.keywords['tech']:
            if keyword.lower() in text:
                matched_tech.append(keyword)
        
        # 기술 키워드가 1개 이상 있어야 통과
        is_match = len(matched_tech) > 0
        
        score = len(matched_tech) * 10  # 기술 키워드 1개당 10점
        
        reason = ""
        if is_match:
            reason = f"기술 키워드 매칭: {', '.join(matched_tech)}"
        else:
            reason = "기술 키워드 없음"
        
        return {
            'is_match': is_match,
            'score': score,
            'matched_keywords': matched_tech,
            'reason': reason
        }
    
    def _apply_type_b_filter(self, announcement: Dict) -> Dict:
        """
        Type B 필터 적용: 지원 중심 (Flexible)
        (기술 키워드) OR (지원 키워드 AND 자격 키워드)
        
        Args:
            announcement: 공고 정보
            
        Returns:
            Dict: {'is_match': bool, 'score': int, 'matched_keywords': List[str], 'reason': str}
        """
        text = f"{announcement['title']} {announcement['description']}".lower()
        
        matched_tech = []
        matched_support = []
        matched_qualification = []
        
        # 1. 기술 키워드 매칭
        for keyword in self.keywords['tech']:
            if keyword.lower() in text:
                matched_tech.append(keyword)
        
        # 2. 지원 키워드 매칭
        for keyword in self.keywords['support']:
            if keyword.lower() in text:
                matched_support.append(keyword)
        
        # 3. 자격 키워드 매칭
        for keyword in self.keywords['qualification']:
            if keyword.lower() in text:
                matched_qualification.append(keyword)
        
        # 필터링 로직: (기술 키워드) OR (지원 키워드 AND 자격 키워드)
        tech_match = len(matched_tech) > 0
        support_and_qualification_match = (len(matched_support) > 0 and 
                                          len(matched_qualification) > 0)
        
        is_match = tech_match or support_and_qualification_match
        
        # 점수 계산
        score = 0
        if tech_match:
            score += len(matched_tech) * 15  # 기술 키워드는 높은 가중치
        if len(matched_support) > 0:
            score += len(matched_support) * 5
        if len(matched_qualification) > 0:
            score += len(matched_qualification) * 3
        
        # 매칭 이유 생성
        reasons = []
        if matched_tech:
            reasons.append(f"기술: {', '.join(matched_tech)}")
        if matched_support:
            reasons.append(f"지원: {', '.join(matched_support)}")
        if matched_qualification:
            reasons.append(f"자격: {', '.join(matched_qualification)}")
        
        reason = " | ".join(reasons) if reasons else "키워드 매칭 없음"
        
        all_matched = matched_tech + matched_support + matched_qualification
        
        return {
            'is_match': is_match,
            'score': score,
            'matched_keywords': all_matched,
            'reason': reason
        }
    
    def get_keyword_statistics(self, filtered_announcements: List[Dict]) -> Dict:
        """
        필터링된 공고들의 키워드 통계
        
        Args:
            filtered_announcements: 필터링된 공고 리스트
            
        Returns:
            Dict: 키워드별 등장 횟수
        """
        stats = {}
        
        for announcement in filtered_announcements:
            for keyword in announcement.get('matched_keywords', []):
                stats[keyword] = stats.get(keyword, 0) + 1
        
        # 내림차순 정렬
        sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_stats


# 테스트 코드
if __name__ == '__main__':
    import yaml
    
    # 설정 로드
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 테스트 공고 데이터
    test_announcements = [
        {
            'title': '수소연료전지 기술개발 지원사업',
            'description': '그린수소 생산기술 개발을 위한 R&D 지원',
            'filter_strategy': 'type_a',
        },
        {
            'title': '경기도 청년 스타트업 마케팅 지원',
            'description': '창업 3년 이내 기업 대상 해외진출 및 마케팅 비용 지원',
            'filter_strategy': 'type_b',
        },
        {
            'title': '일반 제조업 시설 투자 지원',
            'description': '제조업 설비 투자 자금 지원',
            'filter_strategy': 'type_b',
        }
    ]
    
    # 필터 적용
    filter_engine = KeywordFilter(config)
    filtered = filter_engine.filter_announcements(test_announcements)
    
    print(f"\n=== 필터링 결과: {len(filtered)}개 선택 ===")
    for ann in filtered:
        print(f"\n제목: {ann['title']}")
        print(f"점수: {ann['match_score']}")
        print(f"매칭 키워드: {ann['matched_keywords']}")
        print(f"매칭 이유: {ann['match_reason']}")
    
    # 통계
    print("\n=== 키워드 통계 ===")
    stats = filter_engine.get_keyword_statistics(filtered)
    for keyword, count in stats.items():
        print(f"{keyword}: {count}회")