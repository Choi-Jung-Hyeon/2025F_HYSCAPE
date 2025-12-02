#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국수소연합(H2HUB) 브리핑 자동화 시스템 - 메인 실행 스크립트
"""

import logging
import argparse
from pathlib import Path
from typing import List, Dict

import config
from article_collector import H2HUBBriefingCollector
from article_analyzer import BriefingAnalyzer
from notion_uploader import NotionUploader

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class H2HUBAutomation:
    """
    한국수소연합 브리핑 자동화 시스템 메인 클래스
    
    워크플로우:
    1. 브리핑 PDF 수집
    2. PDF 분석 (요약 + 감성 분석)
    3. Notion에 업로드
    """
    
    def __init__(self):
        """컴포넌트 초기화"""
        logger.info("\n" + "="*70)
        logger.info("한국수소연합 브리핑 자동화 시스템 시작")
        logger.info("="*70)
        
        self.collector = H2HUBBriefingCollector()
        self.analyzer = BriefingAnalyzer()
        self.uploader = NotionUploader()
        
        logger.info("✅ 모든 컴포넌트 초기화 완료\n")
    
    def run(self, max_pages: int = 3, upload_to_notion: bool = True):
        """
        전체 자동화 프로세스 실행
        
        Args:
            max_pages: 수집할 최대 페이지 수
            upload_to_notion: Notion 업로드 여부
        """
        # Step 1: 브리핑 수집
        logger.info("\n" + "="*70)
        logger.info("STEP 1: 브리핑 PDF 수집")
        logger.info("="*70)
        
        briefings = self.collector.collect_briefings(max_pages=max_pages)
        
        if not briefings:
            logger.warning("⚠️ 수집된 브리핑이 없습니다.")
            return
        
        logger.info(f"\n✅ {len(briefings)}개의 브리핑 수집 완료")
        
        # Step 2 & 3: 분석 및 업로드
        logger.info("\n" + "="*70)
        logger.info("STEP 2: PDF 분석 및 STEP 3: Notion 업로드")
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
                    upload_success = self.uploader.upload_briefing(briefing, analysis)
                    
                    if upload_success:
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    logger.info("  ⏭️  Notion 업로드 건너뛰기 (--no-upload)")
                    
                    # 분석 결과 출력
                    print(f"\n    감성: {analysis['sentiment']}")
                    print(f"    요약: {analysis['summary'][:100]}...")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"  ❌ 처리 중 오류 발생: {e}")
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
        (웹 크롤링 없이 로컬 PDF만 처리)
        
        Args:
            pdf_dir: PDF 파일이 있는 디렉토리
            upload_to_notion: Notion 업로드 여부
        """
        logger.info("\n" + "="*70)
        logger.info("기존 PDF 파일 분석 모드")
        logger.info("="*70)
        logger.info(f"디렉토리: {pdf_dir}")
        
        # PDF 파일 찾기
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️ PDF 파일을 찾을 수 없습니다: {pdf_dir}")
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
                    upload_success = self.uploader.upload_briefing(briefing_data, analysis)
                    
                    if upload_success:
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    print(f"\n    감성: {analysis['sentiment']}")
                    print(f"    요약: {analysis['summary'][:100]}...")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"  ❌ 처리 중 오류 발생: {e}")
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
        
        Args:
            filename: 파일명
            
        Returns:
            str: YYYY-MM-DD 형식의 날짜
        """
        import re
        from datetime import datetime
        
        # YYMMDD 또는 YYYYMMDD 패턴 찾기
        date_patterns = [
            r'(\d{8})',  # YYYYMMDD
            r'(\d{6})',  # YYMMDD
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{4})\.(\d{2})\.(\d{2})'  # YYYY.MM.DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if len(match.group(0)) == 8:  # YYYYMMDD
                        date_str = match.group(0)
                        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    elif len(match.group(0)) == 6:  # YYMMDD
                        date_str = match.group(0)
                        year = f"20{date_str[:2]}"
                        return f"{year}-{date_str[2:4]}-{date_str[4:6]}"
                    else:
                        # 구분자가 있는 경우
                        return match.group(0).replace('.', '-')
                except:
                    pass
        
        # 날짜를 찾지 못한 경우 오늘 날짜 반환
        return datetime.now().strftime('%Y-%m-%d')


def main():
    """메인 함수 - CLI 인자 처리"""
    parser = argparse.ArgumentParser(
        description='한국수소연합(H2HUB) 브리핑 자동화 시스템'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=3,
        help='수집할 최대 페이지 수 (기본값: 3)'
    )
    
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Notion 업로드 건너뛰기 (분석 결과만 출력)'
    )
    
    parser.add_argument(
        '--existing-pdfs',
        type=str,
        help='기존 PDF 디렉토리 경로 (웹 크롤링 없이 로컬 PDF만 처리)'
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
    
    # 자동화 시스템 실행
    automation = H2HUBAutomation()
    
    # 기존 PDF 처리 모드
    if args.existing_pdfs:
        pdf_dir = Path(args.existing_pdfs)
        automation.run_with_existing_pdfs(
            pdf_dir=pdf_dir,
            upload_to_notion=not args.no_upload
        )
    # 일반 모드 (웹 크롤링 + 분석 + 업로드)
    else:
        automation.run(
            max_pages=args.pages,
            upload_to_notion=not args.no_upload
        )


if __name__ == "__main__":
    main()
