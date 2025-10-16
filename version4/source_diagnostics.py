# source_diagnostics.py
"""
뉴스 소스 진단 도구
각 RSS 피드의 접속 가능 여부를 확인하고 상세 진단 결과를 출력합니다.
"""

import requests
import feedparser
from config import NEWS_SOURCES
import time


def diagnose_rss_source(source_name: str, rss_url: str) -> dict:
    """
    RSS 소스를 진단하고 결과를 반환
    
    Returns:
        {
            'status': 'SUCCESS' | 'FAILED' | 'WARNING',
            'articles_count': int,
            'error_message': str or None,
            'response_time': float
        }
    """
    print(f"\n{'='*60}")
    print(f"진단 중: {source_name}")
    print(f"URL: {rss_url}")
    print(f"{'='*60}")
    
    result = {
        'source_name': source_name,
        'url': rss_url,
        'status': 'UNKNOWN',
        'articles_count': 0,
        'error_message': None,
        'response_time': 0
    }
    
    try:
        # 1단계: HTTP 접속 테스트
        print("  [1/3] HTTP 접속 테스트...", end=" ")
        start_time = time.time()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(rss_url, headers=headers, timeout=10)
        result['response_time'] = round(time.time() - start_time, 2)
        
        print(f"✅ ({result['response_time']}초)")
        print(f"      - HTTP 상태 코드: {response.status_code}")
        print(f"      - Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        response.raise_for_status()
        
        # 2단계: RSS 파싱 테스트
        print("  [2/3] RSS 파싱 테스트...", end=" ")
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            print(f"⚠️ 경고")
            print(f"      - 파싱 오류: {feed.get('bozo_exception', 'Unknown')}")
            result['status'] = 'WARNING'
            result['error_message'] = str(feed.get('bozo_exception', 'Parse warning'))
        else:
            print("✅")
        
        # 3단계: 기사 수집 테스트
        print("  [3/3] 기사 수집 테스트...", end=" ")
        articles_count = len(feed.entries)
        result['articles_count'] = articles_count
        
        if articles_count == 0:
            print("❌ 기사 없음")
            result['status'] = 'FAILED'
            result['error_message'] = "No articles found"
        else:
            print(f"✅ ({articles_count}개)")
            result['status'] = 'SUCCESS'
            
            # 샘플 기사 출력
            print("\n  📰 샘플 기사 (최대 3개):")
            for i, entry in enumerate(feed.entries[:3], 1):
                title = entry.get('title', '제목 없음')
                link = entry.get('link', '링크 없음')
                print(f"      [{i}] {title[:50]}...")
                print(f"          {link[:60]}...")
        
    except requests.exceptions.Timeout:
        print("❌ 타임아웃")
        result['status'] = 'FAILED'
        result['error_message'] = "Connection timeout (10s)"
        
    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패")
        result['status'] = 'FAILED'
        result['error_message'] = "Connection refused or DNS error"
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 오류 ({response.status_code})")
        result['status'] = 'FAILED'
        result['error_message'] = f"HTTP {response.status_code}"
        
    except Exception as e:
        print(f"❌ 알 수 없는 오류")
        result['status'] = 'FAILED'
        result['error_message'] = str(e)
    
    return result


def run_diagnostics():
    """모든 뉴스 소스를 진단하고 결과를 요약"""
    
    print("\n" + "🔍" * 30)
    print("뉴스 소스 진단 도구 v1.0")
    print("🔍" * 30 + "\n")
    
    results = []
    
    for source_name, rss_url in NEWS_SOURCES.items():
        result = diagnose_rss_source(source_name, rss_url)
        results.append(result)
        time.sleep(1)  # 과도한 요청 방지
    
    # 진단 결과 요약
    print("\n" + "="*60)
    print("📊 진단 결과 요약")
    print("="*60 + "\n")
    
    success = [r for r in results if r['status'] == 'SUCCESS']
    warning = [r for r in results if r['status'] == 'WARNING']
    failed = [r for r in results if r['status'] == 'FAILED']
    
    print(f"✅ 정상 작동: {len(success)}개")
    for r in success:
        print(f"   - {r['source_name']}: {r['articles_count']}개 기사")
    
    if warning:
        print(f"\n⚠️ 경고 (작동하지만 문제 있음): {len(warning)}개")
        for r in warning:
            print(f"   - {r['source_name']}: {r['error_message']}")
    
    if failed:
        print(f"\n❌ 접속 불가: {len(failed)}개")
        for r in failed:
            print(f"   - {r['source_name']}: {r['error_message']}")
            print(f"     URL: {r['url']}")
    
    # 권장 사항
    print("\n" + "="*60)
    print("💡 권장 사항")
    print("="*60 + "\n")
    
    if failed:
        print("❌ 접속 불가능한 소스는 config.py에서 제거하세요:")
        print("\n# config.py에서 삭제할 항목:")
        print("NEWS_SOURCES = {")
        for r in success + warning:
            print(f'    "{r["source_name"]}": "{r["url"]}",')
        print("}")
    else:
        print("✅ 모든 소스가 정상 작동합니다!")
    
    print("\n" + "="*60 + "\n")
    
    return results


if __name__ == '__main__':
    run_diagnostics()