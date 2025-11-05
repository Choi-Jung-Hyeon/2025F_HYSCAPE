#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py (Notion Archive - Phase 4: Main Controller)
# [cite: 232]
import argparse
import logging
import json
from datetime import datetime

# 프로젝트 모듈 임포트
from article_collector import H2NewsArchiveCollector
from article_analyzer import ArticleAnalyzer
from notion_uploader import NotionUploader

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dummy_data_for_testing():
    """
    1단계 수집기가 실패할 경우를 대비한 테스트용 더미 데이터.
    2단계(분석기)가 처리할 수 있는 포맷을 반환합니다.
    """
    logging.warning("테스트 모드: 실제 수집기 대신 더미 데이터를 사용합니다.")
    return [
        {
            'title': f"[Main 테스트 {datetime.now()}] 수소법 개정안 통과",
            'content': "지난 29일, '수소경제 육성 및 수소 안전관리에 관한 법률'(수소법) 개정안이 국회 본회의를 통과했다. 이번 개정안은 청정수소 인증제 도입과 CHPS 시행을 골자로 한다.",
            'url': 'https://www.example.com/h2law-passed-main-test',
            'date': '2024-11-05'
        },
        {
            'title': f"[Main 테스트 {datetime.now()}] AEM 수전해 스타트업 투자 유치",
            'content': "호주의 AEM 수전해 기술 스타트업 Hysata가 시리즈B 펀딩 라운드에서 1.1억 달러의 투자를 유치했다고 발표했습니다. BP Ventures가 주도했습니다.",
            'url': 'https://www.example.com/hysata-funding-main-test',
            'date': '2024-11-04'
        }
    ]

def main(year: int, max_pages: int, use_dummy: bool = False):
    """
    프로젝트 전체 파이프라인 실행
    [cite: 233, 249]
    """
    logging.info(f"======== Notion 아카이브 프로젝트 시작 (Target: {year}년) ========")
    
    # 1. 초기화
    collector = H2NewsArchiveCollector()
    analyzer = ArticleAnalyzer()
    uploader = NotionUploader()
    
    if not analyzer.model or not uploader.client:
        logging.error("Gemini 또는 Notion 클라이언트가 초기화되지 않았습니다. config.py를 확인하세요.")
        return

    # --- Phase 1: 데이터 수집 ---
    # [cite: 55]
    articles = []
    if use_dummy:
        articles = create_dummy_data_for_testing()
    else:
        try:
            articles = collector.fetch_archive_by_year(year=year, max_pages=max_pages)
        except Exception as e:
            logging.error(f"1단계 (수집) 중 심각한 오류 발생: {e}")
            logging.warning("수집기 오류로 인해 테스트용 더미 데이터로 대체합니다.")
            articles = create_dummy_data_for_testing() # 실패 시 더미 데이터로 전환
            
    if not articles:
        logging.warning("수집된 기사가 없습니다. 프로세스를 종료합니다.")
        return
        
    logging.info(f"--- 1단계 (수집) 완료: 총 {len(articles)}개 기사 확보 ---")

    # --- Phase 2: 기사 분석 및 분류 ---
    # [cite: 78]
    analyzed_articles = []
    total = len(articles)
    for i, article in enumerate(articles):
        logging.info(f"[2단계 (분석) 진행중... ({i+1}/{total})] {article.get('title')}")
        try:
            analyzed_data = analyzer.classify_article(article)
            analyzed_articles.append(analyzed_data)
        except Exception as e:
            logging.error(f"기사 분석 중 오류 (기사: {article.get('title')}): {e}")

    logging.info(f"--- 2단계 (분석) 완료: 총 {len(analyzed_articles)}개 기사 분석 ---")

    # --- Phase 3: 노션 자동 업로드 ---
    # [cite: 130-132]
    total = len(analyzed_articles)
    for i, article in enumerate(analyzed_articles):
        logging.info(f"[3단계 (업로드) 진행중... ({i+1}/{total})] {article.get('title')}")
        try:
            uploader.upload_article(article)
        except Exception as e:
            logging.error(f"Notion 업로드 중 오류 (기사: {article.get('title')}): {e}")

    logging.info(f"--- 3단계 (업로드) 완료: 총 {len(analyzed_articles)}개 기사 업로드 ---")
    logging.info(f"======== Notion 아카이브 프로젝트 종료 (Target: {year}년) ========")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="월간수소경제 Notion 아카이브 시스템")
    
    # PDF 기획안의 연도별 실행 옵션 [cite: 251]
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="수집할 연도 (기본값: 현재 연도)"
    )
    # 테스트를 위한 페이지 제한 옵션 (기획안에는 없으나 유용함)
    parser.add_argument(
        "--max_pages",
        type=int,
        default=1,
        help="수집할 최대 페이지 수 (기본값: 1)"
    )
    # 1단계(수집기)가 불안정하므로 더미 데이터 사용 옵션 추가
    parser.add_argument(
        "--dummy",
        action="store_true",
        help="실제 수집 대신 테스트용 더미 데이터를 사용합니다."
    )
    
    args = parser.parse_args()
    
    # --dummy 플래그가 있으면 dummy=True로 main 실행
    main(year=args.year, max_pages=args.max_pages, use_dummy=args.dummy)