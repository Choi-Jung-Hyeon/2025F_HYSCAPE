#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 API 디버깅 스크립트
위치: version7/debug_naver_api.py

네이버 뉴스 API의 문제를 진단합니다.
"""

import requests
from config import NAVER_CONFIG

def check_naver_api():
    """네이버 API 설정 및 응답 확인"""
    print("=" * 70)
    print("🔍 네이버 API 디버깅")
    print("=" * 70)
    
    # 1. API 키 확인
    print("\n[1단계] API 키 확인")
    client_id = NAVER_CONFIG.get('client_id', '')
    client_secret = NAVER_CONFIG.get('client_secret', '')
    
    if not client_id:
        print("❌ NAVER_CLIENT_ID가 설정되지 않았습니다!")
        print("   config.py에서 다음을 설정하세요:")
        print("   NAVER_CLIENT_ID = 'your_client_id'")
        return False
    
    if not client_secret:
        print("❌ NAVER_CLIENT_SECRET가 설정되지 않았습니다!")
        print("   config.py에서 다음을 설정하세요:")
        print("   NAVER_CLIENT_SECRET = 'your_client_secret'")
        return False
    
    print(f"✅ Client ID: {client_id[:10]}...")
    print(f"✅ Client Secret: {client_secret[:10]}...")
    
    # 2. API 호출 테스트
    print("\n[2단계] API 호출 테스트")
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
        response = requests.get(url, headers=headers, params=params)
        
        print(f"\n📡 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 호출 성공!")
            print(f"\n📊 응답 데이터:")
            print(f"   - total: {data.get('total', 0)}건")
            print(f"   - start: {data.get('start', 0)}")
            print(f"   - display: {data.get('display', 0)}")
            print(f"   - items: {len(data.get('items', []))}개")
            
            # 3. 첫 번째 기사 출력
            items = data.get('items', [])
            if items:
                print(f"\n[3단계] 첫 번째 기사 예시:")
                first = items[0]
                print(f"   제목: {first.get('title', '')}")
                print(f"   링크: {first.get('link', '')}")
                print(f"   설명: {first.get('description', '')[:100]}...")
                print(f"   날짜: {first.get('pubDate', '')}")
                
                print("\n✅ 네이버 API가 정상 작동합니다!")
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
        
        else:
            print(f"❌ 알 수 없는 에러: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
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
        print("  1. config.py에서 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 확인")
        print("  2. 네이버 개발자 센터에서 API 키 재발급")
        print("     https://developers.naver.com/apps/#/list")
        print("  3. API 할당량 확인")
    print("=" * 70)

if __name__ == "__main__":
    main()