#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notion 업로드 모듈"""

import logging
from typing import Dict

from notion_client import Client

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotionUploader:
    """Notion 데이터베이스 업로드 클래스"""
    
    def __init__(self):
        self.client = Client(auth=config.NOTION_API_KEY)
        self.database_id = config.NOTION_DATABASE_ID
        logger.info(f"NotionUploader 초기화 (DB: {self.database_id[:12]}...)")
    
    def test_connection(self):
        """Notion API 연결 테스트"""
        try:
            logger.info("Notion API 연결 테스트 중...")
            database = self.client.databases.retrieve(database_id=self.database_id)
            
            db_title = database.get('title', [{}])[0].get('plain_text', 'Unknown')
            properties = list(database.get('properties', {}).keys())
            
            logger.info(f"✅ 연결 성공! DB: {db_title}")
            logger.info(f"   속성: {properties}")
            return True
        except Exception as e:
            logger.error(f"❌ 연결 실패: {e}")
            return False
    
    def upload_briefing(self, briefing_data: Dict) -> bool:
        """브리핑 데이터를 Notion에 업로드"""
        logger.info(f"\n📤 Notion 업로드: {briefing_data.get('title', 'Unknown')}")
        
        try:
            properties = self._build_properties(briefing_data)
            
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"  ✅ 업로드 성공")
            return True
        except Exception as e:
            logger.error(f"  ❌ 업로드 실패: {e}")
            return False
    
    def _build_properties(self, data: Dict) -> Dict:
        """Notion 페이지 속성 생성"""
        properties = {}
        
        # 제목 (Title)
        title_prop = config.NOTION_PROPERTIES.get('title', '제목')
        properties[title_prop] = {
            "title": [{"text": {"content": data.get('title', 'Untitled')}}]
        }
        
        # 날짜 (Date)
        if 'date' in data and data['date']:
            date_prop = config.NOTION_PROPERTIES.get('date', 'date')
            properties[date_prop] = {"date": {"start": data['date']}}
        
        # 요약 (Rich Text)
        if 'summary' in data and data['summary']:
            summary_prop = config.NOTION_PROPERTIES.get('summary', '요약')
            properties[summary_prop] = {
                "rich_text": [{"text": {"content": data['summary'][:2000]}}]
            }
        
        # URL (URL)
        if 'url' in data and data['url']:
            url_prop = config.NOTION_PROPERTIES.get('url', 'url')
            properties[url_prop] = {"url": data['url']}
        
        # 기술전망 (Select) - sentiment
        if 'sentiment' in data and data['sentiment']:
            sentiment_prop = config.NOTION_PROPERTIES.get('sentiment', '기술전망')
            sentiment_value = config.SENTIMENT_TAGS.get(data['sentiment'], data['sentiment'])
            properties[sentiment_prop] = {"select": {"name": sentiment_value}}
        
        # category (Select)
        if 'category' in data and data['category']:
            category_prop = config.NOTION_PROPERTIES.get('category', 'category')
            category_value = config.CATEGORY_TAGS.get(data['category'], data['category'])
            properties[category_prop] = {"select": {"name": category_value}}
        
        # keywords (Multi-select)
        if 'keywords' in data and data['keywords']:
            keywords_prop = config.NOTION_PROPERTIES.get('keywords', '키워드')
            keywords_list = data['keywords'] if isinstance(data['keywords'], list) else [data['keywords']]
            properties[keywords_prop] = {
                "multi_select": [{"name": kw} for kw in keywords_list[:5]]
            }
        
        return properties


def main():
    """테스트용"""
    uploader = NotionUploader()
    
    if uploader.test_connection():
        print("\n✅ Notion 연결 성공!")
        
        # 테스트 데이터 업로드
        sample_data = {
            'title': 'TEST - 일간 수소 이슈 브리핑',
            'date': '2025-12-02',
            'summary': '테스트 요약 내용입니다.',
            'url': 'https://h2hub.or.kr/test',
            'sentiment': 'Positive',
            'category': '기관',
            'keywords': ['수소', '수전해', '테스트']
        }
        
        print("\n테스트 데이터 업로드 중...")
        if uploader.upload_briefing(sample_data):
            print("✅ 테스트 성공!")
        else:
            print("❌ 테스트 실패")
    else:
        print("\n❌ Notion 연결 실패")


if __name__ == "__main__":
    main()