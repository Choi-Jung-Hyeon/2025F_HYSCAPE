# h2korea_fetcher.py
"""
한국수소연합 정기간행물 크롤링 모듈 (선택사항)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict


def fetch_h2korea_publications(limit: int = 5) -> List[Dict[str, str]]:
    """
    한국수소연합 정기간행물 페이지에서 최신 발행물을 가져옵니다.
    
    Args:
        limit: 가져올 최대 개수
    
    Returns:
        List[Dict]: 발행물 정보 리스트
    """
    
    url = "https://h2korea.or.kr/ko/index"
    print(f"[한국수소연합] 정기간행물을 수집합니다: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        publications = []
        
        # 실제 웹사이트 구조에 맞게 선택자를 조정해야 합니다
        # 예시 선택자 (실제 사이트 확인 필요)
        items = soup.select('.publication-item')[:limit]
        
        for item in items:
            title_elem = item.select_one('.title')
            link_elem = item.select_one('a')
            
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                
                # 상대 경로를 절대 경로로 변환
                if href and not href.startswith('http'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                
                publications.append({
                    'title': title,
                    'url': href,
                    'source': '한국수소연합'
                })
        
        print(f"  ✅ {len(publications)}개의 발행물을 찾았습니다.")
        return publications
        
    except Exception as e:
        print(f"  ❌ 한국수소연합 크롤링 중 오류 발생: {e}")
        return []


# 연도별 이슈 브리핑 PDF 다운로드 함수 (추가 기능)
def download_h2korea_pdf(pdf_url: str, save_path: str) -> bool:
    """
    한국수소연합 PDF 파일을 다운로드합니다.
    
    Args:
        pdf_url: PDF 파일 URL
        save_path: 저장할 경로
    
    Returns:
        bool: 다운로드 성공 여부
    """
    try:
        print(f"  📥 PDF 다운로드 중: {pdf_url}")
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✅ PDF 저장 완료: {save_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ PDF 다운로드 실패: {e}")
        return False


# ============================================================
# 단위 테스트
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("h2korea_fetcher.py 단위 테스트")
    print("=" * 60)
    
    # 발행물 목록 가져오기
    publications = fetch_h2korea_publications(limit=3)
    
    if publications:
        print("\n📚 수집된 발행물:")
        for i, pub in enumerate(publications, 1):
            print(f"\n[{i}] {pub['title']}")
            print(f"    링크: {pub['url']}")
    else:
        print("\n⚠️  발행물을 찾을 수 없습니다.")
        print("    웹사이트 구조가 변경되었을 수 있습니다.")
    
    print("\n" + "=" * 60)
    print("단위 테스트 완료")
    print("=" * 60)