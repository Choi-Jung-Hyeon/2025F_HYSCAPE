#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 브리핑 분석 모듈 (category와 keywords 포함)
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
    """PDF 브리핑 분석 클래스 (category와 keywords 자동 추출)"""
    
    def __init__(self):
        """Google Gemini 클라이언트 초기화"""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        logger.info(f"BriefingAnalyzer 초기화 완료 (모델: {config.GEMINI_MODEL})")
    
    def analyze_briefing(self, pdf_path: str) -> Optional[Dict]:
        """PDF 브리핑 파일 분석"""
        logger.info(f"\n📊 분석 시작: {Path(pdf_path).name}")
        
        # 1. PDF 텍스트 추출
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            logger.warning(f"  ⚠️ 추출된 텍스트가 너무 짧습니다 ({len(text)} 자)")
            return None
        
        logger.info(f"  ✅ 텍스트 추출 완료 ({len(text)} 자)")
        
        # 2. Gemini API로 분석 (여러 전략 시도)
        analysis = None
        
        # 전략 1: 짧은 텍스트로 시도
        if not analysis and len(text) > 3000:
            logger.info("  📝 전략 1: 짧은 텍스트로 시도...")
            short_text = text[:3000]
            analysis = self._analyze_with_gemini(short_text, strategy="short")
        
        # 전략 2: 전체 텍스트
        if not analysis:
            logger.info("  📝 전략 2: 전체 텍스트로 시도...")
            limited_text = text[:10000]
            analysis = self._analyze_with_gemini(limited_text, strategy="full")
        
        # 전략 3: 매우 간단한 프롬프트
        if not analysis:
            logger.info("  📝 전략 3: 간단한 프롬프트로 시도...")
            analysis = self._analyze_simple(text[:5000])
        
        if analysis:
            logger.info(f"  ✅ 분석 완료")
            logger.info(f"     감성: {analysis['sentiment']}")
            logger.info(f"     카테고리: {analysis.get('category', 'N/A')}")
            logger.info(f"     키워드: {', '.join(analysis.get('keywords', []))}")
            logger.info(f"     요약: {analysis['summary'][:50]}...")
        
        return analysis
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
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
    
    def _analyze_with_gemini(self, text: str, strategy: str = "full") -> Optional[Dict]:
        """Gemini API로 텍스트 분석"""
        try:
            # 프롬프트 생성
            if strategy == "short":
                prompt = self._create_safe_prompt(text)
            else:
                prompt = config.ANALYSIS_PROMPT.format(content=text)
            
            # Safety settings
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
                    max_output_tokens=800  # keywords 때문에 조금 늘림
                ),
                safety_settings=safety_settings
            )
            
            # 응답 확인
            if not response.candidates:
                logger.warning(f"  ⚠️ 응답 없음 (전략: {strategy})")
                return None
            
            # finish_reason 확인
            finish_reason = response.candidates[0].finish_reason
            if finish_reason != 1:
                logger.warning(f"  ⚠️ 비정상 종료: finish_reason={finish_reason} (전략: {strategy})")
                return None
            
            # JSON 파싱
            result_text = response.text.strip()
            json_text = self._extract_json(result_text)
            analysis = json.loads(json_text)
            
            if self._validate_analysis(analysis):
                return analysis
            
            return None
            
        except Exception as e:
            logger.warning(f"  ⚠️ 분석 실패 (전략: {strategy}): {e}")
            return None
    
    def _analyze_simple(self, text: str) -> Optional[Dict]:
        """매우 간단한 프롬프트로 분석"""
        try:
            simple_prompt = f"""
다음 수소 브리핑을 분석하여 JSON으로 답변하세요:

1. summary: 핵심 내용 3줄 요약
2. sentiment: Positive/Negative/Neutral
3. category: 기관/정책/지자체/산업계/연구계/해외 중 1개
4. keywords: 핵심 키워드 3-5개 (배열)

JSON 형식:
{{
  "summary": "...",
  "sentiment": "Positive",
  "category": "기관",
  "keywords": ["수소", "수전해"]
}}

텍스트:
{text[:3000]}
"""
            
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
            
            response = self.model.generate_content(
                simple_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=500
                ),
                safety_settings=safety_settings
            )
            
            if response.candidates and response.candidates[0].finish_reason == 1:
                result_text = response.text.strip()
                json_text = self._extract_json(result_text)
                analysis = json.loads(json_text)
                
                if self._validate_analysis(analysis):
                    return analysis
            
            return None
            
        except Exception as e:
            logger.warning(f"  ⚠️ 간단한 분석 실패: {e}")
            return None
    
    def _create_safe_prompt(self, text: str) -> str:
        """안전한 프롬프트 생성"""
        return f"""
아래 수소 산업 뉴스 브리핑을 분석해주세요.

요구사항:
- summary: 주요 내용 3줄 요약
- sentiment: Positive/Negative/Neutral
- category: 기관/정책/지자체/산업계/연구계/해외 중 1개
- keywords: 핵심 키워드 3-5개 (배열)

JSON 형식으로만 답변:
{{
  "summary": "요약 내용",
  "sentiment": "Positive",
  "category": "기관",
  "keywords": ["수소", "수전해", "청정수소"]
}}

브리핑 내용:
{text}
"""
    
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
        
        if end > start:
            return text[start:end].strip()
        
        return text.strip()
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """분석 결과 검증 (category와 keywords 포함)"""
        # 필수 키 확인
        required_keys = ['summary', 'sentiment', 'category', 'keywords']
        
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
            sentiment_lower = str(analysis['sentiment']).lower()
            if 'positive' in sentiment_lower or '긍정' in sentiment_lower:
                analysis['sentiment'] = 'Positive'
            elif 'negative' in sentiment_lower or '부정' in sentiment_lower:
                analysis['sentiment'] = 'Negative'
            else:
                analysis['sentiment'] = 'Neutral'
            logger.info(f"  sentiment 자동 보정: {analysis['sentiment']}")
        
        # category 검증 및 자동 보정
        valid_categories = ['기관', '정책', '지자체', '산업계', '연구계', '해외']
        if analysis['category'] not in valid_categories:
            logger.warning(f"  잘못된 category 값: {analysis['category']}")
            analysis['category'] = '기관'  # 기본값
            logger.info(f"  category 기본값 설정: {analysis['category']}")
        
        # keywords 검증 및 자동 보정
        if not isinstance(analysis['keywords'], list):
            logger.warning("  keywords가 배열이 아닙니다")
            if isinstance(analysis['keywords'], str):
                # 쉼표로 분리
                analysis['keywords'] = [kw.strip() for kw in analysis['keywords'].split(',')]
            else:
                analysis['keywords'] = []
        
        # 키워드 개수 제한 (최대 5개)
        if len(analysis['keywords']) > 5:
            analysis['keywords'] = analysis['keywords'][:5]
            logger.info(f"  keywords 개수 제한: 5개")
        
        # 빈 키워드 제거
        analysis['keywords'] = [kw for kw in analysis['keywords'] if kw.strip()]
        
        return True


def main():
    """테스트용 메인 함수"""
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
        print(f"카테고리: {result['category']}")
        print(f"키워드: {', '.join(result['keywords'])}")
        print(f"\n요약:\n{result['summary']}")
    else:
        print("\n❌ 분석 실패")


if __name__ == "__main__":
    main()