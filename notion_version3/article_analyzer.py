#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 브리핑 분석 모듈"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, Optional

import pdfplumber
import google.generativeai as genai

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BriefingAnalyzer:
    """PDF 브리핑 분석 클래스"""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        logger.info(f"BriefingAnalyzer 초기화 (모델: {config.GEMINI_MODEL})")
    
    def analyze_briefing(self, pdf_path: str) -> Optional[Dict]:
        """PDF 브리핑 파일 분석"""
        logger.info(f"\n📊 분석 시작: {Path(pdf_path).name}")
        
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            logger.warning(f"  ⚠️ 텍스트가 너무 짧습니다 ({len(text)} 자)")
            return None
        
        logger.info(f"  ✅ 텍스트 추출 완료 ({len(text)} 자)")
        
        # 텍스트 길이에 따라 전략 선택
        analysis = self._analyze_with_gemini(text[:10000])
        
        if not analysis:
            # 재시도: 더 짧은 텍스트
            logger.info("  🔄 짧은 텍스트로 재시도...")
            analysis = self._analyze_with_gemini(text[:5000])
        
        if analysis:
            logger.info(f"  ✅ 분석 완료")
            logger.info(f"     감성: {analysis['sentiment']}")
            logger.info(f"     카테고리: {analysis.get('category', 'N/A')}")
            logger.info(f"     키워드: {', '.join(analysis.get('keywords', []))}")
        
        return analysis
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF 텍스트 추출"""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            full_text = "\n\n".join(text_parts)
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = re.sub(r' {2,}', ' ', full_text)
            
            return full_text.strip()
        except Exception as e:
            logger.error(f"  ❌ PDF 텍스트 추출 실패: {e}")
            return ""
    
    def _analyze_with_gemini(self, text: str) -> Optional[Dict]:
        """Gemini API로 텍스트 분석"""
        try:
            prompt = config.ANALYSIS_PROMPT.format(content=text)
            
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800
                ),
                safety_settings=safety_settings
            )
            
            if not response.candidates or response.candidates[0].finish_reason != 1:
                return None
            
            # JSON 파싱
            result_text = response.text.strip()
            json_text = self._extract_json(result_text)
            analysis = json.loads(json_text)
            
            if self._validate_analysis(analysis):
                return analysis
            
            return None
        except Exception as e:
            logger.warning(f"  ⚠️ 분석 실패: {e}")
            return None
    
    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 추출"""
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)
        
        start = text.find('{')
        if start == -1:
            return text.strip()
        
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
        
        return text[start:end].strip() if end > start else text.strip()
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """분석 결과 검증 및 자동 보정"""
        required_keys = ['summary', 'sentiment', 'category', 'keywords']
        
        for key in required_keys:
            if key not in analysis:
                logger.warning(f"  필수 키 누락: {key}")
                return False
        
        # summary 검증
        if not isinstance(analysis['summary'], str) or len(analysis['summary']) < 10:
            return False
        
        # sentiment 자동 보정
        valid_sentiments = ['Positive', 'Negative', 'Neutral']
        if analysis['sentiment'] not in valid_sentiments:
            sentiment_lower = str(analysis['sentiment']).lower()
            if 'positive' in sentiment_lower or '긍정' in sentiment_lower:
                analysis['sentiment'] = 'Positive'
            elif 'negative' in sentiment_lower or '부정' in sentiment_lower:
                analysis['sentiment'] = 'Negative'
            else:
                analysis['sentiment'] = 'Neutral'
        
        # category 자동 보정
        valid_categories = ['기관', '정책', '지자체', '산업계', '연구계', '해외']
        if analysis['category'] not in valid_categories:
            analysis['category'] = '기관'
        
        # keywords 자동 보정
        if not isinstance(analysis['keywords'], list):
            if isinstance(analysis['keywords'], str):
                analysis['keywords'] = [kw.strip() for kw in analysis['keywords'].split(',')]
            else:
                analysis['keywords'] = []
        
        # 최대 5개로 제한
        analysis['keywords'] = [kw for kw in analysis['keywords'] if kw.strip()][:5]
        
        return True


def main():
    """테스트용"""
    sample_pdf = Path("/mnt/project/250925_일간_수소_이슈_브리핑.pdf")
    
    if not sample_pdf.exists():
        print(f"❌ 파일 없음: {sample_pdf}")
        return
    
    analyzer = BriefingAnalyzer()
    result = analyzer.analyze_briefing(str(sample_pdf))
    
    if result:
        print("\n분석 결과:")
        print(f"감성: {result['sentiment']}")
        print(f"카테고리: {result['category']}")
        print(f"키워드: {', '.join(result['keywords'])}")
        print(f"\n요약:\n{result['summary']}")
    else:
        print("\n❌ 분석 실패")


if __name__ == "__main__":
    main()