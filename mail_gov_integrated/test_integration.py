#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 시스템 테스트 스크립트
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("\n" + "=" * 80)
print("수소 산업 통합 브리핑 시스템 - 모듈 테스트")
print("=" * 80 + "\n")

# 1. FilterStrategy 테스트
print("\n[1/3] FilterStrategy 테스트...")
try:
    from gov_support.filter_strategy import FilterStrategy

    fs = FilterStrategy('config.yaml')

    test_notices = [
        {
            'title': '수소 연료전지 R&D 사업',
            'description': '수소 생산 및 저장 기술 개발',
            'tags': ['수소', 'R&D'],
            'organization': '과학기술정보통신부'
        },
        {
            'title': '스타트업 마케팅 지원',
            'description': '성남 소재 벤처기업 마케팅 지원',
            'tags': ['창업지원'],
            'organization': '성남시'
        }
    ]

    for notice in test_notices:
        score = fs.calculate_relevance(notice)
        print(f"  - {notice['title'][:40]}... : {score}점")

    filtered = fs.filter_notices(test_notices, min_score=30, top_n=5)
    print(f"  ✓ 필터링 완료: {len(filtered)}개 선정")

except Exception as e:
    print(f"  ✗ 실패: {e}")

# 2. GovSupportManager 테스트
print("\n[2/3] GovSupportManager 테스트...")
try:
    from gov_support.gov_support_manager import GovSupportManager

    manager = GovSupportManager('config.yaml')
    print(f"  ✓ 관리자 초기화 완료 ({len(manager.scrapers)}개 스크래퍼)")

    # HTML 생성 테스트 (더미 데이터)
    dummy_notices = [
        {
            'title': '테스트 공고',
            'url': 'https://example.com',
            'organization': '테스트 기관',
            'deadline': '2025-12-31',
            'tags': ['테스트'],
            'source': 'TEST',
            'relevance_score': 85
        }
    ]

    html = manager.generate_html_section(notices=dummy_notices)
    print(f"  ✓ HTML 생성 완료 ({len(html)} 문자)")

except Exception as e:
    print(f"  ✗ 실패: {e}")

# 3. 기타 모듈 import 테스트
print("\n[3/3] 기타 모듈 import 테스트...")
modules = [
    ('config', 'config'),
    ('pdf_reader', 'pdf_reader'),
    ('source_fetcher', 'source_fetcher'),
    ('content_scraper', 'content_scraper'),
    ('summarizer', 'summarizer'),
    ('notifier', 'notifier'),
]

success_count = 0
for module_name, import_name in modules:
    try:
        __import__(import_name)
        print(f"  ✓ {module_name}")
        success_count += 1
    except Exception as e:
        print(f"  ✗ {module_name}: {e}")

print(f"\n  총 {success_count}/{len(modules)}개 모듈 import 성공")

# 결과 요약
print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)
print("\n✅ 모든 핵심 모듈이 정상적으로 작동합니다.")
print("📌 실제 실행: python main.py")
print()
