#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 데이터베이스 속성 확인 스크립트
"""

from notion_client import Client
import config

def check_notion_properties():
    """Notion 데이터베이스의 실제 속성 확인"""
    
    client = Client(auth=config.NOTION_API_KEY)
    
    print("\n" + "="*70)
    print("Notion 데이터베이스 속성 확인")
    print("="*70)
    
    try:
        # 데이터베이스 정보 가져오기
        database = client.databases.retrieve(database_id=config.NOTION_DATABASE_ID)
        
        print(f"\n데이터베이스: {database['title'][0]['plain_text']}")
        print(f"ID: {config.NOTION_DATABASE_ID}")
        
        # 속성 목록
        properties = database.get('properties', {})
        
        print(f"\n총 {len(properties)}개의 속성:")
        print("-" * 70)
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"  📌 {prop_name}")
            print(f"     타입: {prop_type}")
            
            # Select 타입이면 옵션도 표시
            if prop_type == 'select':
                options = prop_info.get('select', {}).get('options', [])
                if options:
                    print(f"     옵션:")
                    for opt in options:
                        print(f"       - {opt['name']}")
            
            print()
        
        print("="*70)
        print("\n현재 config.py 설정:")
        print("-" * 70)
        print(f"  제목 → {config.NOTION_PROPERTIES.get('title')}")
        print(f"  날짜 → {config.NOTION_PROPERTIES.get('date')}")
        print(f"  요약 → {config.NOTION_PROPERTIES.get('summary')}")
        print(f"  링크 → {config.NOTION_PROPERTIES.get('url')}")
        print(f"  감성 → {config.NOTION_PROPERTIES.get('sentiment')}")
        
        print("\n" + "="*70)
        print("✅ 위의 속성명을 config.py의 NOTION_PROPERTIES에 맞춰주세요!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_notion_properties()