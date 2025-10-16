# pdf_reader.py
"""
PDF 파일에서 텍스트를 추출하고 AI를 통해 키워드를 분석하는 모듈
월간수소경제 브리핑 PDF 등을 처리합니다.
"""

import PyPDF2
import google.generativeai as genai
from config import GOOGLE_API_KEY, PDF_FILE_PATH
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDF 파일에서 전체 텍스트를 추출
    
    Args:
        pdf_path: PDF 파일 경로
    
    Returns:
        추출된 텍스트 (문자열)
    """
    print(f"[PDF 리더] PDF 파일을 읽습니다: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"  ❌ 파일을 찾을 수 없습니다: {pdf_path}")
        return None
    
    try:
        text_content = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"  📄 총 {num_pages}페이지를 읽습니다...")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_content.append(text)
        
        full_text = '\n'.join(text_content)
        print(f"  ✅ 텍스트 추출 완료 ({len(full_text)}자)")
        
        return full_text
        
    except Exception as e:
        print(f"  ❌ PDF 읽기 오류: {e}")
        return None


def extract_keywords_from_pdf_text(pdf_text: str) -> list:
    """
    PDF에서 추출한 텍스트를 AI로 분석하여 주요 키워드를 추출
    
    Args:
        pdf_text: PDF에서 추출한 텍스트
    
    Returns:
        키워드 리스트
    """
    print("[AI 분석] PDF 내용에서 키워드를 추출합니다...")
    
    if not pdf_text or len(pdf_text) < 100:
        print("  ❌ 텍스트가 너무 짧거나 비어있습니다.")
        return []
    
    try:
        # Gemini AI 설정
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 프롬프트 작성 (텍스트가 너무 길 경우 앞부분만 사용)
        if len(pdf_text) > 50000:
            pdf_text = pdf_text[:50000] + "...(이하 생략)"
        
        prompt = f"""
아래는 수소 관련 일간 뉴스 브리핑 PDF의 내용입니다.
이 문서에서 언급된 주요 키워드를 15개 이내로 추출해주세요.

키워드 추출 기준:
1. 기술 관련: PEM 수전해, AEM 수전해, 연료전지, 촉매 등
2. 기업 및 기관명
3. 국가 및 지역명
4. 프로젝트명
5. 주요 수치 (예: GW, MW, 톤 등)

출력 형식:
키워드를 쉼표(,)로 구분하여 한 줄로 작성해주세요.

PDF 내용:
{pdf_text}

키워드:
"""
        
        response = model.generate_content(prompt)
        keywords_text = response.text.strip()
        
        # 쉼표로 구분된 키워드를 리스트로 변환
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        
        print(f"  ✅ {len(keywords)}개의 키워드를 추출했습니다.")
        return keywords
        
    except Exception as e:
        print(f"  ❌ AI 키워드 추출 오류: {e}")
        return []


def process_pdf_briefing() -> dict:
    """
    PDF 브리핑 파일을 처리하는 메인 함수
    
    Returns:
        {'text': 추출된 텍스트, 'keywords': 키워드 리스트}
    """
    print("\n" + "="*60)
    print("PDF 브리핑 파일 처리 시작")
    print("="*60 + "\n")
    
    # 1. PDF에서 텍스트 추출
    pdf_text = extract_text_from_pdf(PDF_FILE_PATH)
    
    if not pdf_text:
        print("\n⚠️ PDF 처리 실패")
        return {'text': None, 'keywords': []}
    
    # 2. AI로 키워드 추출
    keywords = extract_keywords_from_pdf_text(pdf_text)
    
    print("\n" + "="*60)
    print(f"PDF 처리 완료 - {len(keywords)}개 키워드")
    print("="*60 + "\n")
    
    return {
        'text': pdf_text,
        'keywords': keywords
    }


# ============================================================
# 모듈 단위 테스트
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("pdf_reader.py 단위 테스트")
    print("=" * 60)
    
    result = process_pdf_briefing()
    
    if result['text']:
        print("\n📄 추출된 텍스트 (처음 500자):")
        print("-" * 60)
        print(result['text'][:500] + "...")
    
    if result['keywords']:
        print("\n🔑 추출된 키워드:")
        print("-" * 60)
        for i, keyword in enumerate(result['keywords'], 1):
            print(f"{i}. {keyword}")
    
    print("\n" + "=" * 60)
    print("단위 테스트 완료")
    print("=" * 60)