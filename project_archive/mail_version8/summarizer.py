# summarizer.py (v3.0)
"""
Gemini API를 이용한 기사 요약 모듈
- Target 키워드 (기술 + 회사) 중심 요약
- 회사 키워드 발견 시 강조 ⭐
"""

import google.generativeai as genai
from config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    SUMMARY_PROMPT_TEMPLATE,
    TARGET_KEYWORDS_TECH,
    TARGET_COMPANIES
)

# Gemini API 설정
genai.configure(api_key=GOOGLE_API_KEY)

# ========================================
# 1. 기사 요약 함수
# ========================================
def get_summary_and_keywords(content, article_title):
    """
    Gemini API로 기사 요약
    - 회사 키워드 강조 ⭐
    - 기술 키워드 포함
    """
    
    # 프롬프트 생성
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        title=article_title,
        content=content[:4000],  # 토큰 제한 고려
        company_keywords=", ".join(TARGET_COMPANIES[:15]),  # 주요 회사만
        tech_keywords=", ".join(TARGET_KEYWORDS_TECH[:10])  # 주요 기술만
    )
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        summary = response.text.strip()
        
        # 매칭된 키워드 추출
        matched_keywords = extract_matched_keywords(content, article_title)
        
        return {
            'summary': summary,
            'matched_keywords': matched_keywords,
            'has_company': any(k in matched_keywords for k in TARGET_COMPANIES),
            'has_tech': any(k in matched_keywords for k in TARGET_KEYWORDS_TECH)
        }
        
    except Exception as e:
        print(f"    ⚠️  요약 실패: {e}")
        return {
            'summary': "요약 실패",
            'matched_keywords': [],
            'has_company': False,
            'has_tech': False
        }

# ========================================
# 2. 키워드 매칭 함수
# ========================================
def extract_matched_keywords(content, title):
    """
    기사 제목 + 본문에서 Target 키워드 추출
    """
    full_text = (title + " " + content).lower()
    matched = []
    
    # 기술 키워드 매칭
    for keyword in TARGET_KEYWORDS_TECH:
        if keyword.lower() in full_text:
            matched.append(keyword)
    
    # 회사 키워드 매칭 ⭐
    for keyword in TARGET_COMPANIES:
        if keyword.lower() in full_text:
            matched.append(keyword)
    
    return list(set(matched))  # 중복 제거

# ========================================
# 3. 키워드 중요도 판단
# ========================================
def calculate_relevance_score(matched_keywords):
    """
    매칭된 키워드 개수로 관련도 점수 계산
    - 회사 키워드: 2점
    - 기술 키워드: 1점
    """
    score = 0
    
    for keyword in matched_keywords:
        if keyword in TARGET_COMPANIES:
            score += 2  # 회사 키워드는 더 높은 점수
        elif keyword in TARGET_KEYWORDS_TECH:
            score += 1
    
    return score

# ========================================
# 4. 이메일용 HTML 생성
# ========================================
def generate_article_html(article_data, summary_result):
    """
    기사 요약 결과를 이메일용 HTML로 변환
    - 회사 키워드가 있으면 강조 ⭐
    """
    
    # 관련도 점수
    relevance_score = calculate_relevance_score(summary_result['matched_keywords'])
    
    # 회사 키워드 포함 여부
    has_company = summary_result['has_company']
    
    # 스타일 설정
    if has_company:
        border_color = "#e74c3c"  # 빨강 (회사 키워드!)
        bg_color = "#fff5f5"
        badge = "⭐ 관심 기업"
    elif relevance_score >= 3:
        border_color = "#f39c12"  # 주황 (높은 관련도)
        bg_color = "#fffbf0"
        badge = "🔥 높은 관련도"
    else:
        border_color = "#3498db"  # 파랑 (일반)
        bg_color = "#f0f8ff"
        badge = ""
    
    # HTML 생성
    html = f"""
    <div style="border-left: 4px solid {border_color}; background-color: {bg_color}; 
                padding: 20px; margin: 20px 0; border-radius: 5px;">
        
        <!-- 제목 -->
        <h3 style="color: #2c3e50; margin-top: 0;">
            {badge + " " if badge else ""}{article_data['title']}
        </h3>
        
        <!-- 출처 -->
        <p style="color: #7f8c8d; font-size: 14px; margin: 5px 0;">
            <strong>출처:</strong> {article_data['source']} | 
            <a href="{article_data['url']}" style="color: #3498db;">원문 링크</a>
        </p>
        
        <!-- 매칭 키워드 -->
        {_generate_keywords_html(summary_result['matched_keywords'], has_company)}
        
        <!-- 요약 내용 -->
        <div style="background-color: white; padding: 15px; margin-top: 15px; 
                    border-radius: 5px; line-height: 1.8;">
            {summary_result['summary'].replace(chr(10), '<br>')}
        </div>
        
        <!-- 관련도 점수 -->
        <p style="color: #95a5a6; font-size: 12px; margin-top: 10px;">
            관련도 점수: {relevance_score}점
        </p>
    </div>
    """
    
    return html

def _generate_keywords_html(matched_keywords, has_company):
    """매칭 키워드를 HTML로 변환"""
    if not matched_keywords:
        return ""
    
    # 회사 키워드와 기술 키워드 분리
    company_kw = [k for k in matched_keywords if k in TARGET_COMPANIES]
    tech_kw = [k for k in matched_keywords if k in TARGET_KEYWORDS_TECH]
    
    html = '<div style="margin: 10px 0;">'
    
    if company_kw:
        html += '<p style="margin: 5px 0;"><strong>⭐ 관심 기업:</strong> '
        html += ", ".join([f'<span style="color: #e74c3c; font-weight: bold;">{k}</span>' for k in company_kw])
        html += '</p>'
    
    if tech_kw:
        html += '<p style="margin: 5px 0;"><strong>🔧 기술 키워드:</strong> '
        html += ", ".join([f'<span style="color: #3498db;">{k}</span>' for k in tech_kw])
        html += '</p>'
    
    html += '</div>'
    
    return html

# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Summarizer v3.0 테스트")
    print("=" * 70)
    
    # 테스트 기사
    test_article = """
    Electric Hydrogen가 새로운 PEM 수전해 시스템을 개발했습니다.
    이 시스템은 기존 대비 촉매 사용량을 50% 줄였으며, 
    내구성(durability)도 크게 향상되었습니다.
    """
    
    result = get_summary_and_keywords(test_article, "Electric Hydrogen의 혁신")
    
    print(f"\n매칭 키워드: {result['matched_keywords']}")
    print(f"회사 포함: {result['has_company']}")
    print(f"기술 포함: {result['has_tech']}")
    print(f"\n요약:\n{result['summary']}")