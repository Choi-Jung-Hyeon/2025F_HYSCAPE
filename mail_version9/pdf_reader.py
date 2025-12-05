# pdf_reader.py
"""
PDF 브리핑 파일 처리 모듈
"""

import os
import glob
import PyPDF2
import google.generativeai as genai
from config import (
    GOOGLE_API_KEY,
    PDF_DIR,
    PDF_TARGET_KEYWORDS,
    TARGET_KEYWORDS_TECH,
    TARGET_COMPANIES,
    GEMINI_MODEL
)

genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf(pdf_path):
    """PDF에서 전체 텍스트 추출"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        print(f"  PDF 읽기 실패 ({pdf_path}): {e}")
        return ""

def extract_keyword_paragraphs(text, keywords):
    """Target 키워드가 포함된 문단만 추출"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    keyword_paragraphs = []
    matched_keywords = set()

    for paragraph in paragraphs:
        if len(paragraph) < 50:
            continue

        for keyword in keywords:
            if keyword.lower() in paragraph.lower():
                keyword_paragraphs.append(paragraph)
                matched_keywords.add(keyword)
                break

    print(f"  매칭된 키워드: {len(matched_keywords)}개")
    print(f"  관련 문단: {len(keyword_paragraphs)}개")

    return keyword_paragraphs, list(matched_keywords)

def summarize_pdf_with_keywords(keyword_paragraphs, matched_keywords):
    """키워드가 포함된 문단들을 Gemini로 요약"""
    if not keyword_paragraphs:
        return "관련 내용 없음"

    content = "\n\n".join(keyword_paragraphs)

    prompt = f"""
다음은 수소 산업 관련 PDF 브리핑 문서에서 추출한 내용입니다.

**매칭된 키워드**: {', '.join(matched_keywords)}

**추출된 내용**:
{content[:4000]}

---

**요약 지침**:
1. 매칭된 키워드를 중심으로 핵심 내용만 정리
2. 회사명이 언급되면 **굵게** 표시하고 무슨 일을 하는지 명확히 설명
3. 기술 용어(PEM 수전해, AEM 수전해 등)가 나오면 기술 세부사항 포함
4. 투자/계약/프로젝트 관련 내용은 금액, 용량, 시기 포함
5. 5-7개 bullet point로 정리 (각 2-3줄)

**요약**:
"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  Gemini 요약 실패: {e}")
        return "요약 실패"

def process_pdf_briefing():
    """pdf/ 디렉토리의 PDF 파일들을 처리"""
    print("\n" + "=" * 70)
    print("PDF 브리핑 파일 처리")
    print("=" * 70)

    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))

    if not pdf_files:
        print(f"  {PDF_DIR} 디렉토리에 PDF 파일이 없습니다.")
        return {
            'status': 'no_files',
            'keywords': [],
            'summary': ''
        }

    print(f"\n{len(pdf_files)}개 PDF 파일 발견:")
    for pdf_file in pdf_files:
        print(f"  - {os.path.basename(pdf_file)}")

    all_keyword_paragraphs = []
    all_matched_keywords = set()

    for pdf_path in pdf_files:
        print(f"\n처리 중: {os.path.basename(pdf_path)}")

        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue

        print(f"  전체 텍스트 길이: {len(text)} 글자")

        keyword_paragraphs, matched_keywords = extract_keyword_paragraphs(
            text,
            PDF_TARGET_KEYWORDS
        )

        all_keyword_paragraphs.extend(keyword_paragraphs)
        all_matched_keywords.update(matched_keywords)

    if all_keyword_paragraphs:
        print(f"\nGemini로 요약 중... (총 {len(all_keyword_paragraphs)}개 문단)")
        summary = summarize_pdf_with_keywords(
            all_keyword_paragraphs,
            list(all_matched_keywords)
        )

        print("PDF 요약 완료")

        return {
            'status': 'success',
            'keywords': list(all_matched_keywords),
            'summary': summary,
            'paragraph_count': len(all_keyword_paragraphs)
        }
    else:
        print("  Target 키워드와 관련된 내용을 찾지 못했습니다.")
        return {
            'status': 'no_match',
            'keywords': [],
            'summary': ''
        }

def generate_pdf_html(pdf_result):
    """PDF 요약 결과를 이메일용 HTML로 변환"""
    if pdf_result['status'] == 'no_files':
        return ""

    if pdf_result['status'] == 'no_match':
        return """
        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <h3 style="color: #856404; margin-top: 0;">PDF 브리핑 파일</h3>
            <p>Target 키워드와 관련된 내용을 찾지 못했습니다.</p>
        </div>
        """

    keywords_html = ", ".join([f"<strong>{k}</strong>" for k in pdf_result['keywords']])

    html = f"""
    <div style="background-color: #e3f2fd; padding: 20px; border-left: 4px solid #2196f3; margin: 20px 0;">
        <h3 style="color: #1976d2; margin-top: 0;">월간수소경제 PDF 브리핑 요약</h3>

        <p style="margin: 10px 0;">
            <strong>매칭 키워드 ({len(pdf_result['keywords'])}개):</strong><br>
            {keywords_html}
        </p>

        <p style="margin: 10px 0;">
            <strong>관련 문단:</strong> {pdf_result.get('paragraph_count', 0)}개
        </p>

        <div style="background-color: white; padding: 15px; margin-top: 15px; border-radius: 5px;">
            <strong>핵심 내용:</strong><br><br>
            {pdf_result['summary'].replace(chr(10), '<br>')}
        </div>
    </div>
    """

    return html