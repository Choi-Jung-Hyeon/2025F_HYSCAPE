#!/usr/bin/env python3
# test_fetchers.py
"""
Source Fetcher 모듈 테스트 스크립트
- 각 Fetcher를 개별적으로 테스트
- Factory 패턴 테스트
"""

import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_header(title):
    """예쁜 헤더 출력"""
    print("\n" + "=" * 70)
    print(f"🧪 {title}")
    print("=" * 70)

def print_article(article, index=None):
    """기사 정보 출력"""
    prefix = f"{index}. " if index else ""
    print(f"{prefix}[{article['source']}] {article['title'][:60]}...")
    print(f"   URL: {article['url']}")
    if 'keyword' in article:
        print(f"   키워드: {article['keyword']}")
    if 'published' in article and article['published']:
        print(f"   발행: {article['published']}")
    print()

def test_rss_fetcher():
    """RSS Fetcher 테스트"""
    print_header("RSS Fetcher 테스트")
    
    try:
        from source_fetcher.rss_fetcher import RSSFetcher
        
        # 월간수소경제 테스트
        print("\n📰 월간수소경제 RSS 테스트")
        fetcher = RSSFetcher("월간수소경제", "http://www.h2news.kr/rss/S1N1.xml")
        articles = fetcher.fetch_articles(max_articles=3)
        
        if articles:
            print(f"✅ {len(articles)}개 기사 수집 성공\n")
            for i, article in enumerate(articles, 1):
                print_article(article, i)
        else:
            print("⚠️ 기사 수집 실패")
        
        return True
    except Exception as e:
        print(f"❌ RSS Fetcher 테스트 실패: {e}")
        return False

def test_web_scraper_fetcher():
    """웹 스크래퍼 Fetcher 테스트"""
    print_header("Web Scraper Fetcher 테스트")
    
    try:
        from source_fetcher.web_scraper_fetcher import WebScraperFetcher
        
        # H2 View 테스트
        print("\n🌐 H2 View 웹 크롤링 테스트")
        fetcher = WebScraperFetcher(
            "H2 View",
            "https://www.h2-view.com/news/all-news/",
            article_selector="article.post",
            title_selector="h2.entry-title",
            link_selector="a"
        )
        articles = fetcher.fetch_articles(max_articles=3)
        
        if articles:
            print(f"✅ {len(articles)}개 기사 수집 성공\n")
            for i, article in enumerate(articles, 1):
                print_article(article, i)
        else:
            print("⚠️ 기사 수집 실패 (사이트 구조 변경 가능성)")
        
        return True
    except Exception as e:
        print(f"❌ Web Scraper Fetcher 테스트 실패: {e}")
        return False

def test_naver_fetcher():
    """네이버 Fetcher 테스트"""
    print_header("Naver Fetcher 테스트")
    
    try:
        from source_fetcher.naver_fetcher import NaverFetcher
        
        # 네이버 뉴스 테스트
        print("\n🔍 네이버 뉴스 검색 테스트")
        fetcher = NaverFetcher()
        test_keywords = ["수소", "수전해"]
        articles = fetcher.fetch_articles_by_keywords(test_keywords, max_per_keyword=2)
        
        if articles:
            print(f"✅ {len(articles)}개 기사 수집 성공\n")
            for i, article in enumerate(articles, 1):
                print_article(article, i)
        else:
            print("⚠️ 기사 수집 실패")
        
        return True
    except Exception as e:
        print(f"❌ Naver Fetcher 테스트 실패: {e}")
        return False

def test_google_fetcher():
    """구글 Fetcher 테스트"""
    print_header("Google Fetcher 테스트")
    
    try:
        from source_fetcher.google_fetcher import GoogleFetcher
        
        # 구글 뉴스 테스트
        print("\n🌍 구글 뉴스 검색 테스트")
        fetcher = GoogleFetcher()
        test_keywords = ["hydrogen energy", "green hydrogen"]
        articles = fetcher.fetch_articles_by_keywords(test_keywords, max_per_keyword=2)
        
        if articles:
            print(f"✅ {len(articles)}개 기사 수집 성공\n")
            for i, article in enumerate(articles, 1):
                print_article(article, i)
        else:
            print("⚠️ 기사 수집 실패 (구글 봇 차단 가능성)")
        
        return True
    except Exception as e:
        print(f"❌ Google Fetcher 테스트 실패: {e}")
        return False

def test_factory():
    """Factory 패턴 테스트"""
    print_header("Factory 패턴 테스트")
    
    try:
        from source_fetcher.factory import SourceFetcherFactory
        
        # 1. 단일 Fetcher 생성 테스트
        print("\n[테스트 1] 단일 Fetcher 생성")
        rss_config = {
            'type': 'rss',
            'url': 'http://www.h2news.kr/rss/S1N1.xml',
            'status': 'active'
        }
        fetcher = SourceFetcherFactory.create("월간수소경제", rss_config)
        print(f"✅ 생성됨: {fetcher}")
        
        # 2. Manager 생성 테스트
        print("\n[테스트 2] FetcherManager 생성")
        manager = SourceFetcherFactory.create_manager_from_config()
        print(f"✅ {len(manager.fetchers)}개 Fetcher 등록됨")
        
        # 3. 전체 기사 수집 테스트
        print("\n[테스트 3] 전체 기사 수집 (간단 버전)")
        print("⏳ 수집 중... (최대 2-3분 소요)")
        articles = manager.fetch_all_articles(max_per_source=2, max_per_keyword=2)
        
        if articles:
            print(f"\n✅ 총 {len(articles)}개 기사 수집 성공")
            print("\n📋 수집된 기사 목록 (최대 5개):")
            for i, article in enumerate(articles[:5], 1):
                print_article(article, i)
        else:
            print("⚠️ 기사 수집 실패")
        
        return True
    except Exception as e:
        print(f"❌ Factory 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 70)
    print("🚀 Source Fetcher 모듈 통합 테스트")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 테스트 선택
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        tests = {
            'rss': test_rss_fetcher,
            'web': test_web_scraper_fetcher,
            'naver': test_naver_fetcher,
            'google': test_google_fetcher,
            'factory': test_factory
        }
        
        if test_type in tests:
            tests[test_type]()
        elif test_type == 'all':
            # 전체 테스트 실행
            results = []
            results.append(("RSS Fetcher", test_rss_fetcher()))
            results.append(("Web Scraper", test_web_scraper_fetcher()))
            results.append(("Naver Fetcher", test_naver_fetcher()))
            results.append(("Google Fetcher", test_google_fetcher()))
            results.append(("Factory", test_factory()))
            
            # 결과 요약
            print_header("테스트 결과 요약")
            for name, success in results:
                status = "✅ 성공" if success else "❌ 실패"
                print(f"{status}: {name}")
        else:
            print(f"❌ 알 수 없는 테스트: {test_type}")
            print("\n사용법:")
            print("  python test_fetchers.py [rss|web|naver|google|factory|all]")
    else:
        # 기본: Factory 테스트만 실행
        test_factory()
    
    print("\n" + "=" * 70)
    print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()