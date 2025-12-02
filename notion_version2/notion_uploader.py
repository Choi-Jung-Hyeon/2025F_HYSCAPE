#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 업로더 모듈
분석된 브리핑 데이터를 Notion 데이터베이스에 업로드합니다.
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from notion_client import Client

import config

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class NotionUploader:
    """
    Notion 데이터베이스에 브리핑 데이터를 업로드하는 클래스
    
    주요 기능:
    1. Notion API를 통한 페이지 생성
    2. 제목, 날짜, 요약, 링크, 기술전망 속성 매핑
    """
    
    def __init__(self):
        """Notion 클라이언트 초기화"""
        self.client = Client(auth=config.NOTION_API_KEY)
        self.database_id = config.NOTION_DATABASE_ID
        
        logger.info("NotionUploader 초기화 완료")
        logger.info(f"데이터베이스 ID: {self.database_id[:8]}...")
    
    def upload_briefing(self, briefing_data: Dict, analysis_data: Dict) -> bool:
        """
        브리핑 데이터를 Notion에 업로드
        
        Args:
            briefing_data: 수집된 브리핑 정보
                {
                    'title': '제목',
                    'date': '날짜',
                    'url': 'URL',
                    'pdf_path': 'PDF 경로'
                }
            analysis_data: 분석 결과
                {
                    'summary': '요약',
                    'sentiment': 'Positive/Negative/Neutral'
                }
                
        Returns:
            bool: 업로드 성공 여부
        """
        logger.info(f"\n📤 Notion 업로드: {briefing_data['title']}")
        
        try:
            # Notion 페이지 속성 생성
            properties = self._build_properties(briefing_data, analysis_data)
            
            # 페이지 생성
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response['id']
            logger.info(f"  ✅ 업로드 성공 (페이지 ID: {page_id[:8]}...)")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 업로드 실패: {e}")
            return False
    
    def _build_properties(self, briefing_data: Dict, analysis_data: Dict) -> Dict:
        """
        Notion 페이지 속성 객체 생성
        
        Args:
            briefing_data: 브리핑 데이터
            analysis_data: 분석 데이터
            
        Returns:
            Dict: Notion properties 객체
        """
        # Sentiment 태그 매핑
        sentiment_tag = config.SENTIMENT_TAGS.get(
            analysis_data['sentiment'],
            config.SENTIMENT_TAGS['Neutral']
        )
        
        # 날짜 포맷 검증
        date_value = self._validate_date(briefing_data['date'])
        
        properties = {
            # 제목 (Title 속성)
            config.NOTION_PROPERTIES['title']: {
                "title": [
                    {
                        "text": {
                            "content": briefing_data['title']
                        }
                    }
                ]
            },
            
            # 날짜 (Date 속성)
            config.NOTION_PROPERTIES['date']: {
                "date": {
                    "start": date_value
                }
            },
            
            # 요약 (Rich Text 속성)
            config.NOTION_PROPERTIES['summary']: {
                "rich_text": [
                    {
                        "text": {
                            "content": analysis_data['summary'][:2000]  # Notion 제한
                        }
                    }
                ]
            },
            
            # 링크 (URL 속성)
            config.NOTION_PROPERTIES['url']: {
                "url": briefing_data['url']
            },
            
            # 기술전망 (Select 속성)
            config.NOTION_PROPERTIES['sentiment']: {
                "select": {
                    "name": sentiment_tag
                }
            }
        }
        
        return properties
    
    def _validate_date(self, date_str: str) -> str:
        """
        날짜 형식 검증 및 변환
        
        Args:
            date_str: 날짜 문자열
            
        Returns:
            str: YYYY-MM-DD 형식의 날짜
        """
        try:
            # 이미 올바른 형식인지 확인
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except:
            # 파싱 실패 시 오늘 날짜 반환
            logger.warning(f"  ⚠️ 잘못된 날짜 형식: {date_str}, 오늘 날짜로 대체")
            return datetime.now().strftime('%Y-%m-%d')
    
    def test_connection(self) -> bool:
        """
        Notion API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            logger.info("Notion API 연결 테스트 중...")
            
            # 데이터베이스 조회
            response = self.client.databases.retrieve(
                database_id=self.database_id
            )
            
            db_title = response.get('title', [{}])[0].get('plain_text', 'Unknown')
            logger.info(f"✅ 연결 성공! 데이터베이스: {db_title}")
            
            # 속성 확인
            properties = response.get('properties', {})
            logger.info(f"   데이터베이스 속성: {list(properties.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 연결 실패: {e}")
            return False


def main():
    """테스트용 메인 함수"""
    uploader = NotionUploader()
    
    # 연결 테스트
    if not uploader.test_connection():
        print("\n❌ Notion 연결 실패. config.py의 API 키와 Database ID를 확인하세요.")
        return
    
    # 더미 데이터로 업로드 테스트
    print("\n" + "=" * 70)
    print("더미 데이터 업로드 테스트")
    print("=" * 70)
    
    dummy_briefing = {
        'title': '[테스트] 일간 수소 이슈 브리핑',
        'date': '2024-11-25',
        'url': 'https://h2hub.or.kr/test',
        'pdf_path': '/path/to/test.pdf'
    }
    
    dummy_analysis = {
        'summary': '이것은 테스트 요약입니다. 수소 산업의 긍정적 전망을 다루고 있습니다.',
        'sentiment': 'Positive'
    }
    
    success = uploader.upload_briefing(dummy_briefing, dummy_analysis)
    
    if success:
        print("\n✅ 테스트 업로드 성공!")
        print("Notion 데이터베이스를 확인하세요.")
    else:
        print("\n❌ 테스트 업로드 실패")


if __name__ == "__main__":
    main()
