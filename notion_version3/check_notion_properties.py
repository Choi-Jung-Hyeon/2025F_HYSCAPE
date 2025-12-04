#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notion 데이터베이스 속성 확인 스크립트"""

from notion_client import Client
import config

def check_notion_properties():
    """Notion 데이터베이스의 실제 속성 확인"""
    
    client = Client(auth=config.NOTION_API_KEY)
    
    print("\n" + "="*70)
    print("Notion 데이터베이스 속성 확인")
    print("="*70)
    
    try:
        database = client.databases.retrieve(database_id=config.NOTION_DATABASE_ID)
        
        db_title = database['title'][0]['plain_text']
        properties = database.get('properties', {})
        
        print(f"\n데이터베이스: {db_title}")
        print(f"ID: {config.NOTION_DATABASE_ID}")
        print(f"\n총 {len(properties)}개의 속성:")
        print("-" * 70)
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"  📌 {prop_name} ({prop_type})")
            
            # Select 옵션 표시
            if prop_type == 'select':
                options = prop_info.get('select', {}).get('options', [])
                if options:
                    for opt in options:
                        print(f"       - {opt['name']}")
        
        print("\n" + "="*70)
        print("✅ 위의 속성명을 config.py의 NOTION_PROPERTIES에 맞춰주세요!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")

if __name__ == "__main__":
    check_notion_properties()