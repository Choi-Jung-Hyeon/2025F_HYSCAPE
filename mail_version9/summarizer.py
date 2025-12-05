# summarizer.py
"""
Gemini API를 이용한 기사 요약 모듈
"""

import google.generativeai as genai
from config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    SUMMARY_PROMPT_TEMPLATE,
    TARGET_KEYWORDS_TECH,
    TARGET_COMPANIES
)

genai.configure(api_key=GOOGLE_API_KEY)

def get_summary_and_keywords(content, article_title):
    """Gemini API로 기사 요약"""
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        title=article_title,
        content=content[:4000],
        company_keywords=", ".join(TARGET_COMPANIES[:15]),
        tech_keywords=", ".join(TARGET_KEYWORDS_TECH[:10])
    )
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        summary = response.text.strip()
        matched_keywords = extract_matched_keywords(content, article_title)

        return {
            'summary': summary,
            'matched_keywords': matched_keywords,
            'has_company': any(k in matched_keywords for k in TARGET_COMPANIES),
            'has_tech': any(k in matched_keywords for k in TARGET_KEYWORDS_TECH)
        }

    except Exception as e:
        print(f"    요약 실패: {e}")
        return {
            'summary': "요약 실패",
            'matched_keywords': [],
            'has_company': False,
            'has_tech': False
        }

def extract_matched_keywords(content, title):
    """기사 제목 + 본문에서 Target 키워드 추출"""
    full_text = (title + " " + content).lower()
    matched = []

    for keyword in TARGET_KEYWORDS_TECH:
        if keyword.lower() in full_text:
            matched.append(keyword)

    for keyword in TARGET_COMPANIES:
        if keyword.lower() in full_text:
            matched.append(keyword)

    return list(set(matched))

def calculate_relevance_score(matched_keywords):
    """관련도 점수 계산 (회사: 2점, 기술: 1점)"""
    score = 0

    for keyword in matched_keywords:
        if keyword in TARGET_COMPANIES:
            score += 2
        elif keyword in TARGET_KEYWORDS_TECH:
            score += 1

    return score

def generate_article_html(article_data, summary_result):
    """기사 요약 결과를 이메일용 HTML로 변환"""
    relevance_score = calculate_relevance_score(summary_result['matched_keywords'])
    has_company = summary_result['has_company']

    # 스타일 설정
    if has_company:
        border_color = "#e74c3c"
        bg_color = "#fff5f5"
        badge = "관심 기업"
    elif relevance_score >= 3:
        border_color = "#f39c12"
        bg_color = "#fffbf0"
        badge = "높은 관련도"
    else:
        border_color = "#3498db"
        bg_color = "#f0f8ff"
        badge = ""
    
    html = f"""
    <div style="border-left: 4px solid {border_color}; background-color: {bg_color};
                padding: 20px; margin: 20px 0; border-radius: 5px;">

        <h3 style="color: #2c3e50; margin-top: 0;">
            {badge + " " if badge else ""}{article_data['title']}
        </h3>

        <p style="color: #7f8c8d; font-size: 14px; margin: 5px 0;">
            <strong>출처:</strong> {article_data['source']} |
            <a href="{article_data['url']}" style="color: #3498db;">원문 링크</a>
        </p>

        {_generate_keywords_html(summary_result['matched_keywords'], has_company)}

        <div style="background-color: white; padding: 15px; margin-top: 15px;
                    border-radius: 5px; line-height: 1.8;">
            {summary_result['summary'].replace(chr(10), '<br>')}
        </div>

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

    company_kw = [k for k in matched_keywords if k in TARGET_COMPANIES]
    tech_kw = [k for k in matched_keywords if k in TARGET_KEYWORDS_TECH]

    html = '<div style="margin: 10px 0;">'

    if company_kw:
        html += '<p style="margin: 5px 0;"><strong>관심 기업:</strong> '
        html += ", ".join([f'<span style="color: #e74c3c; font-weight: bold;">{k}</span>' for k in company_kw])
        html += '</p>'

    if tech_kw:
        html += '<p style="margin: 5px 0;"><strong>기술 키워드:</strong> '
        html += ", ".join([f'<span style="color: #3498db;">{k}</span>' for k in tech_kw])
        html += '</p>'

    html += '</div>'

    return html