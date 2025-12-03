#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# notion_uploader.py (Notion Archive - Phase 3)
# (v1.1: 사용자의 DB 스키마(date, url, category)에 맞게 속성 이름 수정)

import config  # API 키 및 DB ID 로드
from notion_client import Client
import logging
import time
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NotionUploader:
    """
    기획서(PDF) 기반 Notion 자동 업로드 클래스
    [cite_start][cite: 138-139]
    분석 완료된 기사 딕셔너리를 Notion 데이터베이스에 페이지로 생성합니다.
    """

    def __init__(self):
        try:
            self.client = Client(auth=config.NOTION_API_KEY)
            self.database_id = config.NOTION_DATABASE_ID
            logging.info("Notion 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logging.error(f"Notion 클라이언트 초기화 실패: {e}")
            logging.error("config.py의 NOTION_API_KEY와 NOTION_DATABASE_ID를 확인하세요.")
            self.client = None

    def _create_page_properties(self, article: dict) -> dict:
        """
        Notion API의 pages.create 포맷에 맞는 속성(properties) 딕셔너리를 생성합니다.
        (v1.1: 사용자의 DB 스키마(date, url, category)에 맞게 수정)
        
        Args:
            article (dict): 'title', 'date', 'url', 'category', 'keywords', 'summary' 포함
            
        Returns:
            dict: Notion API가 요구하는 properties 페이로드
        """
        
        # Notion '날짜' 속성은 ISO 8601 형식 (YYYY-MM-DD)을 요구합니다.
        try:
            datetime.fromisoformat(article['date'])
            date_payload = {'start': article['date']}
        except (ValueError, TypeError):
            logging.warning(f"잘못된 날짜 형식 ({article['date']}). 오늘 날짜로 대체합니다.")
            date_payload = {'start': datetime.now().strftime('%Y-%m-%d')}

        properties = {
            # 1. 제목 (Title) - (일치)
            "제목": {
                "title": [{"text": {"content": article.get('title', '제목 없음')}}]
            },
            # 2. 날짜 (Date) - (수정: "날짜" -> "date")
            "date": {
                "date": date_payload
            },
            # 3. 링크 (URL) - (수정: "링크" -> "url")
            "url": {
                "url": article.get('url', None)
            },
            # 4. 카테고리 (Select) - (수정: "카테고리" -> "category")
            "category": {
                "select": {"name": article.get('category', '분류 안됨')}
            },
            # 5. 키워드 (Multi-select) - (일치)
            "키워드": {
                "multi_select": [{"name": kw} for kw in article.get('keywords', [])[:100]] # API 제한 (최대 100개)
            },
            # 6. 요약 (Rich Text) - (일치)
            "요약": {
                "rich_text": [{"text": {"content": article.get('summary', '요약 없음')[:1990]}}]
            }
        }
        return properties

    def upload_article(self, article: dict):
        """
        분석 완료된 기사 1건을 Notion 데이터베이스에 새 페이지로 생성합니다.
        """
        if not self.client:
            logging.error("Notion 클라이언트가 초기화되지 않아 업로드를 중단합니다.")
            return

        try:
            page_properties = self._create_page_properties(article)
            
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=page_properties
            )
            logging.info(f"Notion 업로드 성공: {article.get('title', '제목 없음')}")
        
        except Exception as e:
            logging.error(f"Notion 업로드 실패 (기사: {article.get('title', '제목 없음')}): {e}")
            # logging.error(f"  > 업로드 시도 데이터: {json.dumps(article, ensure_ascii=False, indent=2)}")
            logging.error("  > Notion DB 속성 이름(date, url, category 등)이 코드와 일치하는지 재확인하세요.")

# --- 이 모듈을 직접 실행할 경우를 위한 테스트 코드 ---
if __name__ == "__main__":
    logging.info("NotionUploader (v1.1) 모듈 테스트를 시작합니다.")
    
    # 1. 'article_analyzer.py'의 성공적인 테스트 결과물을 그대로 사용
    dummy_analyzed_article = {
      "title": "[테스트 v1.1] 수소법 개정안 통과 (속성 이름 수정)",
      "content": "지난 29일, '수소경제 육성 및 수소 안전관리에 관한 법률'(수소법) ...",
      "url": "https://www.example.com/h2law-passed-test-v1.1",
      "date": "2024-10-31", # 날짜 변경하여 테스트
      "category": "정책",
      "keywords": [
        "수소법", "개정안", "국회", "본회의", "통과", 
        "청정수소", "인증제", "CHPS", "산업통상자원부"
      ],
      "summary": "수소법 개정안이 국회 본회의를 통과하여 청정수소 인증제 도입과 CHPS 시행을 통해 국내 청정수소 생태계 활성화가 기대된다."
    }
    
    # 2. 업로더 인스턴스 생성
    uploader = NotionUploader()
    
    if uploader.client:
        # 3. 테스트 업로드 실행
        uploader.upload_article(dummy_analyzed_article)
        
        logging.info("테스트 완료. Notion DB를 확인하여 '[테스트 v1.1]' 페이지가 생성되었는지 확인하세요.")
    else:
        logging.error("테스트 실패: Notion 클라이언트가 초기화되지 않았습니다.")