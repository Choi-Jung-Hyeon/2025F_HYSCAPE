#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# notion_uploader_DEBUG.py (Notion Archive - Phase 3 - v1.2 DEBUG)
# (오직 '제목' 속성에만 쓰기를 시도하여 연결 자체를 테스트)

import config  # API 키 및 DB ID 로드
from notion_client import Client
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NotionUploaderDebug:
    
    def __init__(self):
        try:
            self.client = Client(auth=config.NOTION_API_KEY)
            self.database_id = config.NOTION_DATABASE_ID
            logging.info("Notion 클라이언트 (DEBUG)가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logging.error(f"Notion 클라이언트 (DEBUG) 초기화 실패: {e}")
            self.client = None

    def upload_minimal_article(self, title_str: str):
        """
        오직 '제목' 속성에만 쓰기를 시도합니다.
        (스크린샷에서 '제목' 속성은 확인되었습니다.)
        """
        if not self.client:
            logging.error("Notion 클라이언트가 초기화되지 않아 업로드를 중단합니다.")
            return False

        properties = {
            # 1. 제목 (Title) - (이 속성은 기본값이므로 반드시 존재해야 함)
            "제목": { 
                "title": [{"text": {"content": title_str}}]
            }
        }
        
        try:
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            logging.info(f"Notion (DEBUG) 업로드 성공: {title_str}")
            return True
        
        except Exception as e:
            logging.error(f"Notion (DEBUG) 업로드 실패: {e}")
            logging.error("  > '제목' 속성조차 찾을 수 없거나, DB ID/API 키가 잘못되었거나, '편집' 권한이 없습니다.")
            return False

# --- 이 모듈을 직접 실행할 경우를 위한 테스트 코드 ---
if __name__ == "__main__":
    logging.info("NotionUploader (v1.2 DEBUG) 모듈 테스트를 시작합니다.")
    
    # 식별하기 쉽도록 현재 시간으로 제목 설정
    debug_title = f"[DEBUG 테스트 {datetime.now()}] '제목' 속성만 테스트"
    
    uploader = NotionUploaderDebug()
    
    if uploader.client:
        success = uploader.upload_minimal_article(debug_title)
        if success:
            logging.info("✅ 테스트 성공! Notion DB에서 '[DEBUG 테스트...]' 페이지를 확인하세요.")
        else:
            logging.error("❌ 테스트 실패. API 키, DB ID, 또는 '편집' 권한을 확인하세요.")
    else:
        logging.error("❌ 테스트 실패: Notion 클라이언트가 초기화되지 않았습니다.")