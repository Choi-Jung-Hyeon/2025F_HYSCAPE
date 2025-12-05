# source_fetcher/naver_fetcher.py
"""
네이버 뉴스 검색 API Fetcher
"""

import requests
from typing import List, Dict
from datetime import datetime
from .api_fetcher import APIFetcher

class NaverFetcher(APIFetcher):
    """네이버 뉴스 검색 API"""

    def __init__(self, **kwargs):
        """네이버 뉴스 Fetcher 초기화"""
        super().__init__(source_name="네이버뉴스", **kwargs)

        extra_config = kwargs.get('extra', {})
        self.client_id = extra_config.get('client_id')
        self.client_secret = extra_config.get('client_secret')
        self.api_url = "https://openapi.naver.com/v1/search/news.json"

        # API 키 검증
        if not self.client_id or not self.client_secret:
            self.logger.warning("네이버 API 키가 설정되지 않았습니다!")
            self.logger.warning("config.py의 NEWS_SOURCES['네이버뉴스']['extra']에 추가하세요:")
    
    def fetch_articles_by_keywords(self, keywords: List[str], max_per_keyword: int = 3) -> List[Dict]:
        """키워드 목록으로 네이버 뉴스 검색"""
        if not self.client_id or not self.client_secret:
            self.logger.error("네이버 API 키가 없어 검색을 중단합니다")
            return []

        all_articles = []

        for keyword in keywords:
            try:
                self.logger.info(f"네이버 검색: '{keyword}'")
                
                headers = {
                    "X-Naver-Client-Id": self.client_id,
                    "X-Naver-Client-Secret": self.client_secret
                }

                params = {
                    "query": keyword,
                    "display": max_per_keyword,
                    "sort": "date"
                }

                response = requests.get(
                    self.api_url,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                # HTTP 에러 체크
                if response.status_code == 401:
                    self.logger.error("인증 실패 (401): API 키를 확인하세요")
                    self.log_error(Exception("API 인증 실패"))
                    continue
                elif response.status_code == 403:
                    self.logger.error("접근 권한 없음 (403)")
                    self.log_error(Exception("API 접근 권한 없음"))
                    continue
                elif response.status_code == 429:
                    self.logger.error("요청 제한 초과 (429)")
                    self.log_error(Exception("API 호출 제한 초과"))
                    continue

                response.raise_for_status()

                data = response.json()
                items = data.get('items', [])

                if not items:
                    self.logger.warning(f"'{keyword}' 검색 결과 없음")
                    continue
                
                for item in items:
                    try:
                        title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                        url = item.get('link', '')
                        pub_date = item.get('pubDate', '')
                        description = item.get('description', '').replace('<b>', '').replace('</b>', '')

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

                self.logger.info(f"  '{keyword}': {len([a for a in all_articles if a.get('keyword') == keyword])}개")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"'{keyword}' 네트워크 에러: {e}")
                self.log_error(e)
                continue
            except Exception as e:
                self.logger.error(f"'{keyword}' 검색 실패: {e}")
                self.log_error(e)
                continue

        self.log_success(len(all_articles))
        return all_articles
    
    def _parse_naver_date(self, naver_date: str) -> str:
        """네이버 날짜 형식 파싱"""
        try:
            dt = datetime.strptime(naver_date, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return naver_date

    def test_api_connection(self) -> bool:
        """API 연결 테스트"""
        if not self.client_id or not self.client_secret:
            self.logger.error("API 키가 설정되지 않았습니다")
            return False

        try:
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            params = {"query": "테스트", "display": 1}

            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                self.logger.info("네이버 API 연결 성공!")
                return True
            else:
                self.logger.error(f"API 연결 실패: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"API 테스트 실패: {e}")
            return False