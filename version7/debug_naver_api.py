#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 API 디버깅 스크립트 (수정 버전)
위치: version7/debug_naver_api.py

config.py의 NEWS_SOURCES 구조에 맞춰 수정
"""

import requests
from config import NEWS_SOURCES

def check_naver_api():
    """네이버 API 설정 및 응답 확인"""
    print("=" * 70)
    print("🔍 네이버 API 디버깅")
    print("=" * 70)
    
    # 1. 네이버 뉴스 설정 찾기
    print("\n[1단계] 네이버 뉴스 설정 확인")
    
    naver_config = NEWS_SOURCES.get('네이버뉴스')
    
    if not naver_config:
        print("❌ config.py에 '네이버뉴스' 소스가 없습니다!")
        print("\n   config.py의 NEWS_SOURCES에 다음을 추가하세요:")
        print("""
    "네이버뉴스": {
        "type": "naver",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "keywords": ["수소", "수전해", "수소경제", "그린수소"],
        "status": "active"
    }
        """)
        return False
    
    print(f"✅ 네이버 뉴스 설정 발견")
    print(f"   타입: {naver_config.get('type')}")
    print(f"   상태: {naver_config.get('status')}")
    
    # 2. API 키 확인
    print("\n[2단계] API 키 확인")
    client_id = naver_config.get('client_id', '')
    client_secret = naver_config.get('client_secret', '')
    
    if not client_id or client_id == "your_client_id":
        print("❌ NAVER CLIENT_ID가 설정되지 않았습니다!")
        print("   config.py에서 다음을 수정하세요:")
        print("   'client_id': '실제_클라이언트_아이디'")
        print("\n   네이버 개발자 센터에서 발급:")
        print("   https://developers.naver.com/apps/#/list")
        return False
    
    if not client_secret or client_secret == "your_client_secret":
        print("❌ NAVER CLIENT_SECRET이 설정되지 않았습니다!")
        print("   config.py에서 다음을 수정하세요:")
        print("   'client_secret': '실제_클라이언트_시크릿'")
        return False
    
    print(f"✅ Client ID: {client_id[:10]}... (설정됨)")
    print(f"✅ Client Secret: {client_secret[:10]}... (설정됨)")
    
    # 3. API 호출 테스트
    print("\n[3단계] API 호출 테스트")
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": "수소",
        "display": 5,
        "sort": "date"
    }
    
    try:
        print(f"⏳ 검색어 '수소'로 테스트 중...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"\n📡 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 호출 성공!")
            print(f"\n📊 응답 데이터:")
            print(f"   - total: {data.get('total', 0)}건")
            print(f"   - start: {data.get('start', 0)}")
            print(f"   - display: {data.get('display', 0)}")
            print(f"   - items: {len(data.get('items', []))}개")
            
            # 4. 첫 번째 기사 출력
            items = data.get('items', [])
            if items:
                print(f"\n[4단계] 첫 번째 기사 예시:")
                first = items[0]
                print(f"   제목: {first.get('title', '').replace('<b>', '').replace('</b>', '')}")
                print(f"   링크: {first.get('link', '')}")
                print(f"   날짜: {first.get('pubDate', '')}")
                
                print("\n✅ 네이버 API가 정상 작동합니다!")
                print("\n📋 keywords 확인:")
                keywords = naver_config.get('keywords', [])
                print(f"   설정된 키워드: {keywords}")
                
                return True
            else:
                print("\n⚠️ API는 작동하지만 검색 결과가 없습니다")
                print("   키워드를 변경해보세요")
                return False
        
        elif response.status_code == 401:
            print("❌ 인증 실패 (401 Unauthorized)")
            print("   API 키가 올바르지 않습니다")
            print("   네이버 개발자 센터에서 확인하세요:")
            print("   https://developers.naver.com/apps/#/list")
            return False
        
        elif response.status_code == 403:
            print("❌ 접근 권한 없음 (403 Forbidden)")
            print("   API 사용 권한이 없거나 할당량을 초과했습니다")
            return False
        
        elif response.status_code == 429:
            print("❌ 요청 제한 초과 (429 Too Many Requests)")
            print("   일일 API 호출 제한을 초과했습니다")
            print("   내일 다시 시도하거나 API 플랜을 업그레이드하세요")
            return False
        
        else:
            print(f"❌ 알 수 없는 에러: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 네이버 서버 응답 없음")
        return False
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행"""
    result = check_naver_api()
    
    print("\n" + "=" * 70)
    if result:
        print("✅ 진단 완료: 네이버 API가 정상 작동합니다!")
        print("\n다음 단계:")
        print("  python test_fetchers.py naver")
    else:
        print("❌ 진단 완료: 문제를 해결한 후 다시 시도하세요")
        print("\n해결 방법:")
        print("  1. config.py에서 NEWS_SOURCES['네이버뉴스'] 확인")
        print("  2. client_id와 client_secret을 실제 값으로 변경")
        print("  3. 네이버 개발자 센터에서 API 키 확인/재발급")
        print("     https://developers.naver.com/apps/#/list")
    print("=" * 70)

if __name__ == "__main__":
    main()