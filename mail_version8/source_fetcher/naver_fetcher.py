# source_fetcher/naver_fetcher.py (v7.1 - API 버전)
"""
네이버 뉴스 검색 API Fetcher
- 공식 네이버 검색 API 사용
- HTML 파싱이 아닌 API 방식
- config.py에서 API 키 읽기
"""

import requests
from typing import List, Dict
from datetime import datetime
from .api_fetcher import APIFetcher

class NaverFetcher(APIFetcher):
    """
    네이버 뉴스 검색 API
    
    사용 예:
        from config import NAVER_KEYWORDS, MAX_NAVER_PER_KEYWORD
        
        # config.py의 NEWS_SOURCES['네이버뉴스']['extra']에서 API 키 자동 로드
        fetcher = NaverFetcher(
            client_id="your_client_id",
            client_secret="your_client_secret"
        )
        articles = fetcher.fetch_articles_by_keywords(NAVER_KEYWORDS, MAX_NAVER_PER_KEYWORD)
    
    API 키 발급:
        https://developers.naver.com/apps/#/list
        → 애플리케이션 등록 → 검색 API 선택
    """
    
    def __init__(self, **kwargs):
        """
        네이버 뉴스 Fetcher 초기화 (API 방식)
        
        Args:
            **kwargs: 
                - 'extra' (dict): {'client_id': '...', 'client_secret': '...'}
                - (기타 APIFetcher 인수들)
        """
        super().__init__(source_name="네이버뉴스", **kwargs)
        
        # v7.1: config.py의 'extra' 딕셔너리에서 API 키를 로드
        extra_config = kwargs.get('extra', {})
        self.client_id = extra_config.get('client_id')
        self.client_secret = extra_config.get('client_secret')
        
        self.api_url = "https://openapi.naver.com/v1/search/news.json"
        
        # API 키 검증
        if not self.client_id or not self.client_secret:
            self.logger.warning("⚠️ 네이버 API 키가 설정되지 않았습니다!")
            self.logger.warning("   config.py의 NEWS_SOURCES['네이버뉴스']['extra']에 추가하세요:")
            self.logger.warning("   'client_id': 'your_client_id'")
            self.logger.warning("   'client_secret': 'your_client_secret'")
    
    def fetch_articles_by_keywords(self, keywords: List[str], max_per_keyword: int = 3) -> List[Dict]:
        """
        키워드 목록으로 네이버 뉴스 검색 (API 방식)
        
        Args:
            keywords: 검색 키워드 목록
            max_per_keyword: 키워드당 최대 기사 수
            
        Returns:
            List[Dict]: 기사 목록
        """
        # API 키 체크
        if not self.client_id or not self.client_secret:
            self.logger.error("❌ 네이버 API 키가 없어 검색을 중단합니다")
            return []
        
        all_articles = []
        
        for keyword in keywords:
            try:
                self.logger.info(f"🔍 네이버 검색: '{keyword}'")
                
                # API 요청 헤더
                headers = {
                    "X-Naver-Client-Id": self.client_id,
                    "X-Naver-Client-Secret": self.client_secret
                }
                
                # API 요청 파라미터
                params = {
                    "query": keyword,
                    "display": max_per_keyword,  # 검색 결과 개수
                    "sort": "date"  # 최신순 정렬
                }
                
                # API 호출
                response = requests.get(
                    self.api_url, 
                    headers=headers, 
                    params=params, 
                    timeout=10
                )
                
                # HTTP 에러 체크
                if response.status_code == 401:
                    self.logger.error("❌ 인증 실패 (401): API 키를 확인하세요")
                    self.log_error(Exception("API 인증 실패"))
                    continue
                elif response.status_code == 403:
                    self.logger.error("❌ 접근 권한 없음 (403): API 사용 권한을 확인하세요")
                    self.log_error(Exception("API 접근 권한 없음"))
                    continue
                elif response.status_code == 429:
                    self.logger.error("❌ 요청 제한 초과 (429): 일일 API 호출 제한")
                    self.log_error(Exception("API 호출 제한 초과"))
                    continue
                
                response.raise_for_status()
                
                # JSON 응답 파싱
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    self.logger.warning(f"⚠️ '{keyword}' 검색 결과 없음")
                    continue
                
                # 기사 정보 추출
                for item in items:
                    try:
                        # HTML 태그 제거 (<b>, </b>)
                        title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                        url = item.get('link', '')
                        pub_date = item.get('pubDate', '')
                        description = item.get('description', '').replace('<b>', '').replace('</b>', '')
                        
                        # 발행일시 파싱 (RFC 822 → ISO 8601)
                        try:
                            published = self._parse_naver_date(pub_date)
                        except:
                            published = pub_date
                        
                        article = {
                            'title': title,
                            'url': url,
                            'published': published,
                            'source': f"{self.source_name}({keyword})",
                            'keyword': keyword,
                            'description': description
                        }
                        
                        if self.validate_article(article):
                            all_articles.append(article)
                            
                    except Exception as e:
                        self.logger.debug(f"기사 파싱 실패: {e}")
                        continue
                
                self.logger.info(f"  ✅ '{keyword}': {len([a for a in all_articles if a.get('keyword') == keyword])}개")
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ '{keyword}' 네트워크 에러: {e}")
                self.log_error(e)
                continue
            except Exception as e:
                self.logger.error(f"❌ '{keyword}' 검색 실패: {e}")
                self.log_error(e)
                continue
        
        self.log_success(len(all_articles))
        return all_articles
    
    def _parse_naver_date(self, naver_date: str) -> str:
        """
        네이버 날짜 형식을 파싱
        
        Args:
            naver_date: 네이버 API 날짜 (RFC 822 형식)
                       예: "Tue, 22 Oct 2025 16:30:00 +0900"
        
        Returns:
            str: 파싱된 날짜 (ISO 형식) 또는 원본
        """
        try:
            # RFC 822 → datetime
            dt = datetime.strptime(naver_date, "%a, %d %b %Y %H:%M:%S %z")
            # datetime → ISO 8601
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return naver_date
    
    def test_api_connection(self) -> bool:
        """
        API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        if not self.client_id or not self.client_secret:
            self.logger.error("❌ API 키가 설정되지 않았습니다")
            return False
        
        try:
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            params = {"query": "테스트", "display": 1}
            
            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("✅ 네이버 API 연결 성공!")
                return True
            else:
                self.logger.error(f"❌ API 연결 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ API 테스트 실패: {e}")
            return False


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("🧪 NaverFetcher v7.1 (API 버전) 테스트")
    print("=" * 70)
    
    # API 키는 환경변수나 config.py에서 가져오기
    import os
    
    client_id = os.environ.get('NAVER_CLIENT_ID', 'YOUR_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
    
    if client_id == 'YOUR_CLIENT_ID':
        print("\n⚠️ 환경변수에 네이버 API 키를 설정하세요:")
        print("   export NAVER_CLIENT_ID='your_client_id'")
        print("   export NAVER_CLIENT_SECRET='your_client_secret'")
        print("\n또는 코드에 직접 입력:")
        print("   client_id = 'your_client_id'")
        print("   client_secret = 'your_client_secret'")
    else:
        # 테스트 실행
        extra_test_config = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        fetcher = NaverFetcher(extra=extra_test_config)
        
        # API 연결 테스트
        print("\n[테스트 1] API 연결 테스트")
        if fetcher.test_api_connection():
            print("✅ 연결 성공!\n")
            
            # 키워드 검색 테스트
            print("[테스트 2] 키워드 검색")
            test_keywords = ["수소", "그린수소"]
            articles = fetcher.fetch_articles_by_keywords(test_keywords, max_per_keyword=2)
            
            if articles:
                print(f"\n✅ 총 {len(articles)}개 기사 수집\n")
                for i, article in enumerate(articles, 1):
                    print(f"{i}. [{article['keyword']}] {article['title'][:60]}...")
                    print(f"   URL: {article['url']}")
                    print(f"   발행: {article['published']}")
                    print()
            else:
                print("⚠️ 검색 결과 없음")