# summarizer.py

import google.generativeai as genai
from config import GOOGLE_API_KEY

def get_summary_and_keywords(title, content):
    if not GOOGLE_API_KEY:
        print("[오류] Gemini API 키가 config.py에 설정되지 않았습니다.")
        return "Gemini API 키가 설정되지 않았습니다.", ""

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        당신은 수소 에너지 전문 애널리스트입니다. 다음 뉴스 기사의 핵심 내용을 분석하여 아래 형식에 맞춰 응답해주세요.

        - 요약: 기사의 핵심 내용을 3문장으로 요약합니다.
        - 키워드: 기사의 핵심 키워드를 5개 쉼표(,)로 구분하여 나열합니다.

        ---
        [기사 제목]: {title}
        
        [기사 내용]:
        {content[:8000]} 
        ---
        """
        
        print("  Gemini AI에게 기사 요약을 요청합니다...")
        response = model.generate_content(prompt)
        
        summary_part = response.text.split("키워드:")[0].replace("요약:", "").strip()
        keywords_part = response.text.split("키워드:")[-1].strip()

        return summary_part, keywords_part

    except Exception as e:
        print(f"  [오류] Gemini AI 요약 처리 중 오류 발생: {e}")
        return "요약 처리 중 오류가 발생했습니다.", ""

# 단위 테스트 코드
if __name__ == '__main__':
    print("--- summarizer.py 단위 테스트 시작 ---")

    # 테스트용 기사 제목과 본문
    test_title = "정부, 수전해 수소 생산단가 2030년 2달러대까지 낮춘다"
    test_content = """
    정부가 오는 2030년까지 수전해 수소 생산단가를 kg당 2달러대까지 낮춘다는 목표를 제시했다. 
    산업통상자원부는 10월 26일 서울 더플라자호텔에서 수소 R&D 산학연 전문가 및 기업인 등 100여명이 참석한 가운데 
    ‘제1회 수소 R&D 성과 포럼’을 개최했다. 이번 포럼은 그간의 수소 R&D 성과를 공유하고 향후 기술개발 방향을 논의하기 위해 마련됐다. 
    이 자리에서 산업부는 수전해 수소 생산, 수소 저장·운송, 수소 모빌리티, 연료전지 등 4대 기술개발 분야를 중심으로 한 
    ‘수소 기술개발 로드맵’을 발표했다. 로드맵에 따르면 정부는 수전해 기술 분야에서 현재 kg당 5~6달러 수준인 그린수소 생산단가를 
    2030년까지 2달러대로 낮추는 것을 목표로 설정했다. 이를 위해 알칼라인, PEM, AEM, SOEC 등 다양한 방식의 수전해 기술을 개발하고 상용화할 계획이다.
    """
    
    summary, keywords = get_summary_and_keywords(test_title, test_content)
    
    print("\n[AI 요약 결과]")
    print(f"요약: {summary}")
    print(f"키워드: {keywords}")
        
    print("\n--- 단위 테스트 종료 ---")