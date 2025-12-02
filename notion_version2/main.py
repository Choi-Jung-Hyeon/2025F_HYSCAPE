#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국수소연합(H2HUB) 브리핑 자동화 시스템 - 메인 실행 파일
"""

import logging
import sys
from pathlib import Path
from typing import List
import argparse

from article_collector import H2HUBBriefingCollector
from article_analyzer import BriefingAnalyzer
from notion_uploader import NotionUploader
import config

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class H2HubAutomation:
    """H2HUB 브리핑 자동화 시스템"""
    
    def __init__(self):
        """컴포넌트 초기화"""
        self.collector = H2HUBBriefingCollector()
        self.analyzer = BriefingAnalyzer()
        self.uploader = NotionUploader()
        
        logger.info("✅ 모든 컴포넌트 초기화 완료")
    
    def run_full_workflow(self, num_pages: int = 1, upload_to_notion: bool = True):
        """
        전체 워크플로우 실행
        1. H2HUB에서 브리핑 수집
        2. 내용 분석
        3. Notion에 업로드
        """
        logger.info("\n" + "="*70)
        logger.info("STEP 1: 브리핑 PDF 수집")
        logger.info("="*70)
        
        # 1. 브리핑 수집
        briefings = self.collector.collect_briefings(num_pages=num_pages)
        
        if not briefings:
            logger.warning("⚠️ 수집된 브리핑이 없습니다.")
            return
        
        logger.info(f"\n✅ {len(briefings)}개의 브리핑 수집 완료")
        
        # 2. 분석 및 업로드
        logger.info("\n" + "="*70)
        logger.info("STEP 2: 브리핑 분석 및 업로드")
        logger.info("="*70)
        
        success_count = 0
        fail_count = 0
        
        for i, briefing in enumerate(briefings, 1):
            logger.info(f"\n[{i}/{len(briefings)}] {briefing['title']}")
            
            try:
                # 분석
                analysis = self.analyzer.analyze_briefing(briefing['pdf_path'])
                
                if not analysis:
                    logger.warning("  ⚠️ 분석 실패, 다음 브리핑으로 이동")
                    fail_count += 1
                    continue
                
                # Notion 업로드
                if upload_to_notion:
                    # briefing과 analysis를 하나의 딕셔너리로 병합 ⭐
                    briefing_data = {**briefing, **analysis}
                    
                    upload_success = self.uploader.upload_briefing(briefing_data)
                    
                    if upload_success:
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    logger.info("  ⏭️  Notion 업로드 건너뛰기 (--no-upload)")
                    
                    # 분석 결과 출력
                    print(f"\n    감성: {analysis['sentiment']}")
                    print(f"    카테고리: {analysis.get('category', 'N/A')}")
                    print(f"    키워드: {', '.join(analysis.get('keywords', []))}")
                    print(f"    요약: {analysis['summary'][:100]}...")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"  ❌ 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                continue
        
        # 최종 결과
        logger.info("\n" + "="*70)
        logger.info("작업 완료")
        logger.info("="*70)
        logger.info(f"✅ 성공: {success_count}개")
        logger.info(f"❌ 실패: {fail_count}개")
        logger.info(f"📊 총 처리: {success_count + fail_count}개")
        logger.info("="*70 + "\n")
    
    def run_with_existing_pdfs(self, pdf_dir: Path, upload_to_notion: bool = True):
        """
        기존 PDF 파일들을 분석하여 업로드
        """
        logger.info("\n" + "="*70)
        logger.info("기존 PDF 파일 분석 모드")
        logger.info("="*70)
        logger.info(f"디렉토리: {pdf_dir}")
        
        # PDF 파일 목록 가져오기
        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️ {pdf_dir}에 PDF 파일이 없습니다.")
            return
        
        logger.info(f"\n✅ {len(pdf_files)}개의 PDF 파일 발견")
        
        success_count = 0
        fail_count = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
            
            try:
                # 분석
                analysis = self.analyzer.analyze_briefing(str(pdf_file))
                
                if not analysis:
                    logger.warning("  ⚠️ 분석 실패")
                    fail_count += 1
                    continue
                
                # 브리핑 데이터 생성 (파일명에서 추출)
                briefing_data = {
                    'title': pdf_file.stem,
                    'date': self._extract_date_from_filename(pdf_file.name),
                    'url': f'file://{pdf_file.absolute()}',
                    'pdf_path': str(pdf_file)
                }
                
                # Notion 업로드
                if upload_to_notion:
                    # briefing_data와 analysis를 병합 ⭐
                    briefing_data.update(analysis)
                    
                    upload_success = self.uploader.upload_briefing(briefing_data)
                    
                    if upload_success:
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    print(f"\n    감성: {analysis['sentiment']}")
                    print(f"    카테고리: {analysis.get('category', 'N/A')}")
                    print(f"    키워드: {', '.join(analysis.get('keywords', []))}")
                    print(f"    요약: {analysis['summary'][:100]}...")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"  ❌ 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                continue
        
        # 최종 결과
        logger.info("\n" + "="*70)
        logger.info("작업 완료")
        logger.info("="*70)
        logger.info(f"✅ 성공: {success_count}개")
        logger.info(f"❌ 실패: {fail_count}개")
        logger.info("="*70 + "\n")
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """
        파일명에서 날짜 추출
        예: "250925_일간 수소 이슈 브리핑.pdf" -> "2025-09-25"
        """
        import re
        
        # YYMMDD 형식 찾기
        match = re.search(r'(\d{2})(\d{2})(\d{2})', filename)
        
        if match:
            yy, mm, dd = match.groups()
            # 25 -> 2025로 변환
            year = f"20{yy}"
            return f"{year}-{mm}-{dd}"
        
        return ""


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="한국수소연합 브리핑 자동화 시스템"
    )
    
    # 모드 선택
    parser.add_argument(
        '--pages',
        type=int,
        default=0,
        help='웹에서 수집할 페이지 수 (기본: 0, 수집 안 함)'
    )
    
    parser.add_argument(
        '--existing-pdfs',
        type=str,
        help='기존 PDF 디렉토리 경로 (예: ../pdf)'
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