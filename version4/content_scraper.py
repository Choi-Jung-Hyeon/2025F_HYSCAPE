# 파일명: content_scraper.py

import requests
from bs4 import BeautifulSoup
import re
import time

def get_and_clean_article_content(url):
    """
    기사 URL에 접속하여 본문 텍스트를 추출하고 AI에 맞게 가공합니다.
    (n8n의 HTTP Request + HTML Extract + Content Processor 역할)
    """
    # 네트워크 오류 등을 대비해 최대 3번 재시도합니다.
    for attempt in range(3):
        try:
            # 실제 브라우저처럼 보이기 위한 User-Agent 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            # HTTP 요청이 실패하면 예외를 발생시킵니다.
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 본문 추출: <p> 태그 내용을 모두 가져옵니다.
            paragraphs = soup.find_all('p')
            
            # 2. 텍스트 가공: 의미 있는 문장들만 필터링하고 결합합니다.
            content_list = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                # 너무 짧은 텍스트(광고, 캡션 등)는 제외합니다. (예: 10단어 이상)
                if len(text.split()) > 10:
                    content_list.append(text)
            
            # 필터링된 문단들을 하나의 문자열로 합칩니다.
            clean_content = ' '.join(content_list)
            
            # AI가 더 잘 이해하도록 불필요한 특수문자를 제거합니다.
            clean_content = re.sub(r'[^\w\s가-힣]', '', clean_content)
            
            # 성공적으로 본문을 추출했으면 결과를 반환하고 함수를 종료합니다.
            return clean_content

        except Exception as e:
            print(f"  [오류] 본문 추출 실패 (시도 {attempt + 1}/3): {url}")
            print(f"  오류 내용: {e}")
            time.sleep(2) # 2초 대기 후 재시도
            
    # 3번 모두 실패하면 None을 반환합니다.
    return None

# --- 단위 테스트 코드 ---
if __name__ == '__main__':
    print("--- content_scraper.py 단위 테스트 시작 ---")
    
    # 실제 뉴스 기사 URL로 테스트합니다.
    test_url = "https://www.h2news.kr/news/articleView.html?idxno=11140"
    
    content = get_and_clean_article_content(test_url)
    
    if content:
        print("\n[추출된 본문 내용 (일부)]")
        print(content[:400] + "...") # 너무 길지 않게 400자만 출력
    else:
        print("\n본문 내용을 추출하는 데 실패했습니다.")
        
    print("\n--- 단위 테스트 종료 ---")