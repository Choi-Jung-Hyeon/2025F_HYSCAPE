#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 브리핑 분석 모듈
pdfplumber로 PDF 텍스트를 추출하고, Google Gemini API로 요약 및 감성 분석을 수행합니다.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import json
import re

import pdfplumber
import google.generativeai as genai

import config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BriefingAnalyzer:
    """
    PDF 브리핑 분석 클래스
    
    주요 기능:
    1. PDF 텍스트 추출 (pdfplumber)
    2. Google Gemini를 사용한 요약 및 감성 분석
    """
    
    def __init__(self):
        """Google Gemini 클라이언트 초기화"""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        logger.info(f"BriefingAnalyzer 초기화 완료 (모델: {config.GEMINI_MODEL})")
    
    def analyze_briefing(self, pdf_path: str) -> Optional[Dict]:
        """
        PDF 브리핑 파일을 분석하는 메인 메서드
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict: 분석 결과
                {
                    'summary': '3줄 요약',
                    'sentiment': 'Positive/Negative/Neutral'
                }
                실패 시 None 반환
        """
        logger.info(f"\n📊 분석 시작: {Path(pdf_path).name}")
        
        # 1. PDF 텍스트 추출
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            logger.warning(f"  ⚠️ 추출된 텍스트가 너무 짧습니다 ({len(text)} 자)")
            return None
        
        logger.info(f"  ✅ 텍스트 추출 완료 ({len(text)} 자)")
        
        # 2. Gemini API로 분석
        analysis = self._analyze_with_gemini(text)
        
        if analysis:
            logger.info(f"  ✅ 분석 완료")
            logger.info(f"     감성: {analysis['sentiment']}")
            logger.info(f"     요약: {analysis['summary'][:50]}...")
        
        return analysis
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        pdfplumber를 사용하여 PDF에서 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        try:
            text_parts = []
            
            with pdfplumber.open(pdf_path) as pdf:
                logger.debug(f"  페이지 수: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"    페이지 {page_num}: {len(page_text)} 자 추출")
            
            full_text = "\n\n".join(text_parts)
            
            # 불필요한 공백 정리
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = re.sub(r' {2,}', ' ', full_text)
            
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"  ❌ PDF 텍스트 추출 실패: {e}")
            return ""
    
    def _analyze_with_gemini(self, text: str) -> Optional[Dict]:
        """
        Google Gemini API를 사용하여 텍스트 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict: 분석 결과 {'summary': ..., 'sentiment': ...}
        """
        try:
            # 텍스트가 너무 길면 잘라내기
            max_chars = 30000
            if len(text) > max_chars:
                logger.info(f"  텍스트가 너무 깁니다. {max_chars}자로 제한합니다.")
                text = text[:max_chars] + "..."
            
            # 프롬프트 생성
            prompt = config.ANALYSIS_PROMPT.format(content=text)
            
            # Gemini API 호출 (⭐ Safety Settings 완화)
            logger.debug("  Gemini API 호출 중...")
            
            # Safety settings 완화 (PDF 브리핑 분석용)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500
                ),
                safety_settings=safety_settings
            )
            
            # 응답 확인
            if not response.candidates:
                logger.error("  ❌ Gemini 응답 없음")
                return None
            
            # finish_reason 확인
            finish_reason = response.candidates[0].finish_reason
            if finish_reason != 1:  # 1 = STOP (정상)
                logger.warning(f"  ⚠️ 비정상 종료: finish_reason={finish_reason}")
                # 2=SAFETY, 3=RECITATION, 4=OTHER
                if finish_reason == 2:
                    logger.error("  안전 필터에 걸렸습니다. 내용을 확인해주세요.")
                return None
            
            # 응답 파싱
            result_text = response.text.strip()
            
            # 디버깅: 원본 응답 출력
            logger.debug(f"  Gemini 원본 응답:\n{result_text}")
            
            # JSON 추출
            json_text = self._extract_json(result_text)
            logger.debug(f"  추출된 JSON: {json_text}")
            
            # JSON 파싱
            analysis = json.loads(json_text)
            
            # 검증
            if not self._validate_analysis(analysis):
                logger.warning("  ⚠️ 분석 결과 검증 실패")
                return None
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON 파싱 실패: {e}")
            logger.error(f"  원본 응답:\n{result_text}")
            logger.error(f"  추출된 JSON:\n{json_text}")
            return None
            
        except Exception as e:
            logger.error(f"  ❌ Gemini 분석 실패: {e}")
            import traceback
            logger.error(f"  상세 오류:\n{traceback.format_exc()}")
            return None
    
    def _extract_json(self, text: str) -> str:
        """
        텍스트에서 JSON 부분만 추출 (개선된 버전)
        
        Args:
            text: 원본 텍스트
            
        Returns:
            str: JSON 문자열
        """
        # 1. 마크다운 코드 블록 제거
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)
        
        # 2. 중괄호로 시작하고 끝나는 JSON 객체 찾기
        start = text.find('{')
        if start == -1:
            return text.strip()
        
        # 중괄호 매칭으로 JSON 끝 찾기
        count = 0
        end = start
        for i in range(start, len(text)):
            if text[i] == '{':
                count += 1
            elif text[i] == '}':
                count -= 1
                if count == 0:
                    end = i + 1
                    break
        
        if end > start:
            json_text = text[start:end]
            return json_text.strip()
        
        # 3. 정규식으로 시도
        json_match = re.search(r'\{[^{}]*"summary"[^{}]*"sentiment"[^{}]*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # 4. 실패 시 전체 텍스트 반환
        return text.strip()
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """
        분석 결과 검증
        
        Args:
            analysis: 분석 결과 딕셔너리
            
        Returns:
            bool: 유효성 여부
        """
        # 필수 키 확인
        required_keys = ['summary', 'sentiment']
        
        for key in required_keys:
            if key not in analysis:
                logger.warning(f"  필수 키 누락: {key}")
                return False
        
        # summary 검증
        if not isinstance(analysis['summary'], str) or len(analysis['summary']) < 10:
            logger.warning("  요약이 너무 짧습니다")
            return False
        
        # sentiment 검증 및 자동 보정
        valid_sentiments = ['Positive', 'Negative', 'Neutral']
        if analysis['sentiment'] not in valid_sentiments:
            logger.warning(f"  잘못된 sentiment 값: {analysis['sentiment']}")
            # 자동 보정 시도
            sentiment_lower = str(analysis['sentiment']).lower()
            if 'positive' in sentiment_lower or '긍정' in sentiment_lower:
                analysis['sentiment'] = 'Positive'
            elif 'negative' in sentiment_lower or '부정' in sentiment_lower:
                analysis['sentiment'] = 'Negative'
            else:
                analysis['sentiment'] = 'Neutral'
            logger.info(f"  sentiment 자동 보정: {analysis['sentiment']}")
        
        return True


def main():
    """테스트용 메인 함수"""
    # 샘플 PDF 파일로 테스트
    sample_pdf = Path("../pdf/250925_일간 수소 이슈 브리핑.pdf")
    
    if not sample_pdf.exists():
        print(f"❌ 테스트 파일을 찾을 수 없습니다: {sample_pdf}")
        return
    
    analyzer = BriefingAnalyzer()
    result = analyzer.analyze_briefing(str(sample_pdf))
    
    if result:
        print("\n" + "=" * 70)
        print("분석 결과:")
        print("=" * 70)
        print(f"\n감성 분석: {result['sentiment']}")
        print(f"\n요약:\n{result['summary']}")
    else:
        print("\n❌ 분석 실패")


if __name__ == "__main__":
    main()