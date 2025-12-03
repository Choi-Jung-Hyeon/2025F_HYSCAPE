#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# article_analyzer.py (Notion Archive - Phase 2)

import google.generativeai as genai
import config  # config.py 파일에서 API 키와 모델 이름 가져오기
import logging
import time
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArticleAnalyzer:
    """
    기획서(PDF) 기반 기사 분석 및 분류 클래스
    [cite: 85-86]
    Gemini API를 사용하여 기사를 분류하고, 요약하며, 핵심 키워드를 추출합니다.
    """

    def __init__(self):
        """
        Gemini 모델을 초기화합니다.
        """
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(
                config.GEMINI_MODEL,
                # PDF 기획안의 분류/요약 작업은 안정적인 출력이 중요
                generation_config={"temperature": 0.2} 
            )
            logging.info(f"Gemini 모델 '{config.GEMINI_MODEL}'이 성공적으로 초기화되었습니다.")
        except Exception as e:
            logging.error(f"Gemini 모델 초기화 중 오류 발생: {e}")
            self.model = None

    def _parse_classification_response(self, raw_text: str) -> dict:
        """
        Gemini API의 텍스트 응답을 파싱하여 딕셔너리로 변환합니다.
        [cite: 98-101]
        
        Args:
            raw_text (str): "카테고리: ...", "핵심 키워드: ...", "한 줄 요약: ..." 형식의 텍스트

        Returns:
            dict: 파싱된 데이터를 담은 딕셔너리
        """
        parsed_data = {
            "category": "분류 안됨",
            "keywords": [],
            "summary": "요약 없음"
        }
        
        try:
            # 카테고리 추출
            category_match = re.search(r"카테고리\s*:\s*(.+)", raw_text)
            if category_match:
                parsed_data["category"] = category_match.group(1).strip()

            # 핵심 키워드 추출
            keywords_match = re.search(r"핵심\s*키워드\s*:\s*(.+)", raw_text)
            if keywords_match:
                keywords_str = keywords_match.group(1).strip()
                # 쉼표(,) 또는 공백으로 구분된 키워드를 리스트로 변환
                parsed_data["keywords"] = [k.strip() for k in re.split(r'[,\s]+', keywords_str) if k.strip()]

            # 한 줄 요약 추출
            summary_match = re.search(r"한\s*줄\s*요약\s*:\s*(.+)", raw_text)
            if summary_match:
                parsed_data["summary"] = summary_match.group(1).strip()

        except Exception as e:
            logging.warning(f"Gemini 응답 파싱 중 오류 발생: {e}. 원본 텍스트: {raw_text[:200]}")
            
        return parsed_data

    def classify_article(self, article_data: dict) -> dict:
        """
        단일 기사 데이터를 Gemini API로 분석하고 분류합니다.
        [cite: 87-88]
        
        Args:
            article_data (dict): 'title', 'content', 'url', 'date' 키를 포함한 딕셔너리

        Returns:
            dict: 원본 article_data에 'category', 'keywords', 'summary'가 추가된 딕셔너리
        """
        if not self.model:
            logging.error("모델이 초기화되지 않아 기사 분류를 중단합니다.")
            return article_data

        title = article_data.get('title', '')
        # 본문은 Gemini API의 토큰 제한을 고려하여 1500자 정도로 제한
        content = article_data.get('content', '')[:1500] 
        
        # 기획서 PDF의 프롬프트 양식 적용 [cite: 89-101]
        prompt = f"""
        다음 수소 관련 기사를 분석하고 카테고리를 선택하세요:

        [카테고리 목록]
        1. 기술 (Technology): PEM 수전해, AEM 수전해, 연료전지, 수소터빈, 암모니아, CCUS 등 특정 기술 개발, R&D, 성능 향상, 신기술 동향
        2. 정책 (Policy): 정부 부처(산업부, 과기부 등)의 정책 발표, 법안(수소법 등), 보조금, 규제, 표준, 로드맵, 국가간 협력(MOU)
        3. 기업 (Company): 특정 기업의 경영 활동, 투자 유치, 계약, 파트너십, 공장 증설, 제품 출시, 재무 성과, 인사
        4. 프로젝트 (Project): 특정 지역에서 진행되는 실증 사업, 플랜트 건설, 수소 도시, 충전소 구축, 수소 모빌리티(선박, 트럭 등) 도입 프로젝트

        [기사 정보]
        기사 제목: {title}
        기사 내용: {content}

        [출력 형식]
        반드시 다음 형식에 맞춰 한글로 출력하세요:
        카테고리: [위 4가지 목록 중 하나만 선택]
        핵심 키워드: [기사 내 핵심 키워드 3-5개, 쉼표(,)로 구분]
        한 줄 요약: [기사 전체 내용을 한 줄로 요약]
        """

        try:
            logging.info(f"기사 분석 요청 (Gemini API): {title}")
            response = self.model.generate_content(prompt)
            
            # API 응답 텍스트 파싱
            parsed_result = self._parse_classification_response(response.text)
            
            # 원본 데이터에 분석 결과 추가
            article_data.update(parsed_result)
            
            # API 과호출 방지를 위한 간단한 딜레이 (1초)
            time.sleep(1) 

        except Exception as e:
            logging.error(f"Gemini API 호출 중 오류 발생 (기사: {title}): {e}")
            # 실패 시에도 Notion 업로드를 위해 빈 값으로 업데이트
            article_data.update(self._parse_classification_response("")) 
        
        return article_data

# --- 이 모듈을 직접 실행할 경우를 위한 테스트 코드 ---
if __name__ == "__main__":
    logging.info("ArticleAnalyzer 모듈 테스트를 시작합니다.")
    
    # 1. 테스트용 더미 기사 데이터 생성
    dummy_article = {
        'title': "월간수소경제, '수소법 개정안' 국회 본회의 통과 소식 전해",
        'content': """
        지난 29일, '수소경제 육성 및 수소 안전관리에 관한 법률'(수소법) 
        개정안이 국회 본회의를 통과했다. 
        이번 개정안은 청정수소 인증제 도입과 CHPS(청정수소발전의무화제도) 
        시행을 골자로 한다. 산업통상자원부는 이를 통해 
        국내 청정수소 생태계가 빠르게 활성화될 것으로 기대하고 있다.
        """,
        'url': 'https://www.example.com/h2law-passed',
        'date': '2024-10-30'
    }
    
    # 2. 분석기 인스턴스 생성
    analyzer = ArticleAnalyzer()
    
    if analyzer.model:
        # 3. 기사 분류 테스트 실행
        analyzed_data = analyzer.classify_article(dummy_article)
        
        # 4. 결과 출력
        logging.info("--- 기사 분석 결과 ---")
        import json
        print(json.dumps(analyzed_data, indent=2, ensure_ascii=False))
        logging.info("----------------------")
        
        if analyzed_data.get("category") != "분류 안됨":
            logging.info("테스트 성공: 기사 분류가 정상적으로 완료되었습니다.")
        else:
            logging.warning("테스트 실패: 기사가 분류되지 않았습니다.")
    else:
        logging.error("테스트 실패: Gemini 모델이 초기화되지 않았습니다. config.py의 API 키를 확인하세요.")