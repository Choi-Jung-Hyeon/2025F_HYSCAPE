# summarizer.py (v2.0)
"""
Gemini AI를 이용한 기사 요약 및 키워드 추출 모듈
"""

import google.generativeai as genai
from config import GOOGLE_API_KEY, TARGET_KEYWORDS


def get_summary_and_keywords(title, content):
    """
    Gemini AI를 사용하여 기사를 요약하고 키워드를 추출합니다.
    
    Args:
        title: 기사 제목
        content: 기사 본문
    
    Returns:
        tuple: (요약문, 키워드 문자열)
    """
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "여기에_본인의_GEMINI_API_키를_입력하세요":
        print("[오류] Gemini API 키가 config.py에 설정되지 않았습니다.")
        return "Gemini API 키가 설정되지 않았습니다.", ""

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Gemini 2.5 Flash 모델 사용 (무료 할당량 더 많음)
        # RPM: 10, RPD: 250, TPM: 250,000
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Target 키워드 리스트를 문자열로 변환
        target_keywords_str = ", ".join(TARGET_KEYWORDS[:15])  # 처음 15개만

        prompt = f"""
당신은 수소 에너지 및 수전해 기술 전문 애널리스트입니다. 
다음 뉴스 기사의 핵심 내용을 분석하여 정확하고 간결하게 요약해주세요.

**[분석 중점 사항]**
다음 기술 키워드들에 특히 주목하여 분석하세요:
{target_keywords_str}

**[출력 형식]**
1. **요약**: 기사의 핵심 내용을 3~4문장으로 명확하게 요약
   - 누가(Who), 무엇을(What), 왜(Why), 어떻게(How)를 포함
   - 구체적인 수치나 날짜가 있다면 반드시 포함
   
2. **키워드**: 기사의 핵심 키워드 5~7개를 쉼표(,)로 구분하여 나열
   - 기술 용어 우선
   - 회사명/기관명 포함
   - 국가/지역명 포함 (해당시)

---
**[기사 제목]**: {title}

**[기사 내용]**:
{content[:10000]}
---

**응답 형식 예시:**
요약: 한국수력원자력이 2025년까지 100MW급 수전해 시스템을 개발한다. PEM 방식을 채택하며 총 500억원이 투입된다. 이를 통해 연간 2만톤의 그린수소 생산이 가능할 것으로 기대된다.

키워드: PEM 수전해, 한국수력원자력, 그린수소, 100MW, 수소 생산, 재생에너지, 2025년
        """
        
        print("  📡 Gemini 2.5 Flash에게 기사 요약을 요청합니다...")
        response = model.generate_content(prompt)
        
        # 응답 파싱
        response_text = response.text.strip()
        
        # "요약:"과 "키워드:" 구분
        if "키워드:" in response_text:
            parts = response_text.split("키워드:")
            summary_part = parts[0].replace("요약:", "").strip()
            keywords_part = parts[1].strip()
        else:
            # 구분자가 없으면 전체를 요약으로 처리
            summary_part = response_text.replace("요약:", "").strip()
            keywords_part = "키워드 추출 실패"

        return summary_part, keywords_part

    except Exception as e:
        print(f"  ❌ [오류] Gemini AI 요약 처리 중 오류 발생: {e}")
        return "요약 처리 중 오류가 발생했습니다.", "오류"


# ============================================================
# 단위 테스트 코드
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("summarizer.py (v2.0) 단위 테스트")
    print("=" * 70)

    # 테스트용 기사 제목과 본문
    test_title = "한국수소산업협회, 2030년 수소경제 로드맵 발표"
    test_content = """
    한국수소산업협회는 10일 서울 여의도에서 '2030 수소경제 실현 로드맵'을 발표했다.
    이번 로드맵에 따르면, 2030년까지 수전해 수소 생산단가를 현재 kg당 5~6달러에서 
    2달러대로 낮추는 것을 목표로 설정했다.
    
    특히 PEM(고분자전해질막) 수전해 기술 개발에 집중하며, 알칼라인, AEM, SOEC 등 
    다양한 방식의 수전해 기술도 동시에 개발할 계획이다. 
    
    정부는 이를 위해 향후 5년간 총 3조원의 R&D 예산을 투입하고, 
    대규모 실증 사업을 추진할 예정이다. 또한 재생에너지와 수전해 시스템을 
    연계한 통합 솔루션 개발에도 박차를 가한다.
    
    협회 관계자는 "내구성 향상과 촉매 로딩량 감소가 핵심 과제"라며 
    "글로벌 수소 시장을 선도하기 위해 산학연이 협력할 것"이라고 밝혔다.
    """
    
    print("\n[테스트 입력]")
    print(f"제목: {test_title}")
    print(f"본문 길이: {len(test_content)}자")
    
    print("\n[AI 처리 시작]")
    summary, keywords = get_summary_and_keywords(test_title, test_content)
    
    print("\n" + "=" * 70)
    print("[AI 요약 결과]")
    print("=" * 70)
    print(f"\n📝 요약:\n{summary}")
    print(f"\n🔑 키워드:\n{keywords}")
    print("\n" + "=" * 70)
    print("단위 테스트 완료")
    print("=" * 70)