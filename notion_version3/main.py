#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한국수소연합(H2HUB) 브리핑 자동화 시스템 - 메인"""

import logging
import sys
import argparse
import re
from pathlib import Path

from article_collector import H2HUBBriefingCollector
from article_analyzer import BriefingAnalyzer
from notion_uploader import NotionUploader
import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class H2HubAutomation:
    """H2HUB 브리핑 자동화 시스템"""
    
    def __init__(self):
        self.collector = H2HUBBriefingCollector()
        self.analyzer = BriefingAnalyzer()
        self.uploader = NotionUploader()
        logger.info("✅ 모든 컴포넌트 초기화 완료")
    
    def run_full_workflow(self, num_pages: int = 1, upload_to_notion: bool = True):
        """전체 워크플로우 (수집 → 분석 → 업로드)"""
        logger.info("\n" + "="*70)
        logger.info("STEP 1: 브리핑 PDF 수집")
        logger.info("="*70)
        
        # 수집
        briefings = self.collector.collect_briefings(max_pages=num_pages)
        
        if not briefings:
            logger.warning("⚠️ 수집된 브리핑이 없습니다.")
            return
        
        logger.info(f"\n✅ {len(briefings)}개 수집 완료")
        
        # 분석 및 업로드
        logger.info("\n" + "="*70)
        logger.info("STEP 2: 분석 및 업로드")
        logger.info("="*70)
        
        success, fail = 0, 0
        
        for i, briefing in enumerate(briefings, 1):
            logger.info(f"\n[{i}/{len(briefings)}] {briefing['title']}")
            
            try:
                analysis = self.analyzer.analyze_briefing(briefing['pdf_path'])
                
                if not analysis:
                    logger.warning("  ⚠️ 분석 실패")
                    fail += 1
                    continue
                
                if upload_to_notion:
                    briefing_data = {**briefing, **analysis}
                    if self.uploader.upload_briefing(briefing_data):
                        success += 1
                    else:
                        fail += 1
                else:
                    self._print_analysis(analysis)
                    success += 1
            except Exception as e:
                logger.error(f"  ❌ 처리 오류: {e}")
                fail += 1
        
        self._print_summary(success, fail)
    
    def run_with_existing_pdfs(self, pdf_dir: Path, upload_to_notion: bool = True):
        """기존 PDF 파일 분석"""
        logger.info("\n" + "="*70)
        logger.info("기존 PDF 파일 분석 모드")
        logger.info("="*70)
        logger.info(f"디렉토리: {pdf_dir}")
        
        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️ PDF 파일이 없습니다: {pdf_dir}")
            return
        
        logger.info(f"\n✅ {len(pdf_files)}개 PDF 파일 발견")
        
        success, fail = 0, 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
            
            try:
                analysis = self.analyzer.analyze_briefing(str(pdf_file))
                
                if not analysis:
                    logger.warning("  ⚠️ 분석 실패")
                    fail += 1
                    continue
                
                briefing_data = {
                    'title': pdf_file.stem,
                    'date': self._extract_date(pdf_file.name),
                    'url': f'file://{pdf_file.absolute()}',
                    'pdf_path': str(pdf_file),
                    **analysis
                }
                
                if upload_to_notion:
                    if self.uploader.upload_briefing(briefing_data):
                        success += 1
                    else:
                        fail += 1
                else:
                    self._print_analysis(analysis)
                    success += 1
            except Exception as e:
                logger.error(f"  ❌ 처리 오류: {e}")
                fail += 1
        
        self._print_summary(success, fail)
    
    def _extract_date(self, filename: str) -> str:
        """파일명에서 날짜 추출 (YYMMDD → YYYY-MM-DD)"""
        match = re.search(r'(\d{2})(\d{2})(\d{2})', filename)
        if match:
            yy, mm, dd = match.groups()
            return f"20{yy}-{mm}-{dd}"
        return ""
    
    def _print_analysis(self, analysis: dict):
        """분석 결과 출력"""
        print(f"\n    감성: {analysis['sentiment']}")
        print(f"    카테고리: {analysis.get('category', 'N/A')}")
        print(f"    키워드: {', '.join(analysis.get('keywords', []))}")
        print(f"    요약: {analysis['summary'][:100]}...")
    
    def _print_summary(self, success: int, fail: int):
        """최종 결과 출력"""
        logger.info("\n" + "="*70)
        logger.info("작업 완료")
        logger.info("="*70)
        logger.info(f"✅ 성공: {success}개")
        logger.info(f"❌ 실패: {fail}개")
        logger.info(f"📊 총 처리: {success + fail}개")
        logger.info("="*70 + "\n")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="한국수소연합 브리핑 자동화 시스템"
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=0,
        help='웹에서 수집할 페이지 수 (기본: 0)'
    )
    
    parser.add_argument(
        '--existing-pdfs',
        type=str,
        help='기존 PDF 디렉토리 경로 (예: /mnt/project)'
    )
    
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Notion 업로드 건너뛰기 (분석만)'
    )
    
    parser.add_argument(
        '--test-notion',
        action='store_true',
        help='Notion 연결 테스트만 수행'
    )
    
    args = parser.parse_args()
    
    # Notion 연결 테스트
    if args.test_notion:
        print("\n" + "="*70)
        print("Notion 연결 테스트")
        print("="*70)
        uploader = NotionUploader()
        uploader.test_connection()
        return
    
    # 시스템 시작
    logger.info("\n" + "="*70)
    logger.info("한국수소연합 브리핑 자동화 시스템 시작")
    logger.info("="*70)
    
    automation = H2HubAutomation()
    upload_to_notion = not args.no_upload
    
    # 기존 PDF 모드
    if args.existing_pdfs:
        pdf_dir = Path(args.existing_pdfs)
        if not pdf_dir.exists():
            logger.error(f"❌ 디렉토리를 찾을 수 없습니다: {pdf_dir}")
            sys.exit(1)
        automation.run_with_existing_pdfs(pdf_dir, upload_to_notion)
    
    # 웹 수집 모드
    elif args.pages > 0:
        automation.run_full_workflow(args.pages, upload_to_notion)
    
    else:
        parser.print_help()
        print("\n❌ --pages 또는 --existing-pdfs 옵션이 필요합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()