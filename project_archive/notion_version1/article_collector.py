#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# article_collector.py (Notion Archive - Phase 1 - v2.2)
# (v2.1: CSS 선택자 수정)
# (v2.2: 디버깅 기능 추가 - debug_page.html 파일 생성)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import config  # config.py 파일 로드
import logging
import time
from datetime import datetime
import os # v2.2: 파일 저장을 위해 추가
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class H2NewsArchiveCollector:
    """
    기획서(PDF) 기반 '월간수소경제' 아카이브 수집기
    지정된 연도의 기사 목록(articleList)을 가져온 후,
    각 기사의 본문 내용을 직접 스크래핑합니다.
    """
    
    def __init__(self):
        self.base_url = config.H2NEWS_ARCHIVE_URL
        self.headers = config.DEFAULT_HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # URL 루트 (e.g., https://www.h2news.kr)
        parsed_uri = urlparse(self.base_url)
        self.root_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"

    def _parse_article_date(self, soup) -> str:
        """
        기사 본문 페이지에서 작성일(승인일)을 추출합니다.
        (H2News는 '승인' 날짜를 사용)
        """
        try:
            date_items = soup.select("ul.infomation li")
            for item in date_items:
                text = item.get_text()
                if "승인" in text:
                    date_str = text.replace("승인", "").strip()
                    dt = datetime.strptime(date_str, '%Y.%m.%d %H:%M')
                    return dt.strftime('%Y-%m-%d')
        except Exception as e:
            logging.warning(f"날짜 파싱 오류: {e}")
        return datetime.now().strftime('%Y-%m-%d')

    def fetch_article_content(self, article_url):
        """
        개별 기사 페이지에 접속하여 제목, 본문, 날짜를 스크래핑합니다.
        (v2.3: 본문 페이지 선택자 수정)
        """
        full_url = urljoin(self.base_url, article_url)

        try:
            response = self.session.get(full_url, timeout=10)

            # --- [v2.3 디버깅 코드 추가] ---
            # (이 코드는 v2.2에서 추가한 것이므로 그대로 두거나, 
            #  이제 문제가 해결되었는지 확인 후 삭제하셔도 됩니다.)
            if "debug_article_page_created" not in globals():
                globals()["debug_article_page_created"] = True 
                debug_file = "debug_article_page.html"
                try:
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logging.info(f"기사 본문 디버깅 파일 '{debug_file}'이 생성되었습니다.")
                except Exception as e:
                    logging.error(f"기사 본문 디버깅 파일 저장 실패: {e}")
            # --- [디버깅 코드 끝] ---

            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # --- [v2.3 선택자 수정] ---
            # 1. 제목 (Title)
            title_elem = soup.select_one("h1.titles#user-tit")
            title = title_elem.get_text().strip() if title_elem else "제목 없음"

            # 2. 날짜 (Date) - 로직 변경
            date_elem = soup.select_one("i.icon-clock-o")
            date_text = ""
            if date_elem:
                date_text = date_elem.parent.get_text() # <li><i class="icon-clock-o"></i> 2025.11.12 08:55</li>

            date_match = re.search(r'(\d{4}[-\.]\d{2}[-\.]\d{2})', date_text)
            date = date_match.group(1).replace('.', '-') if date_match else datetime.now().strftime('%Y-%m-%d')

            # 3. 본문 (Body)
            body_elem = soup.select_one("div#article-view-content-div")
            body = body_elem.get_text().strip() if body_elem else "본문 없음"
            # --- [수정 끝] ---

            if body == "본문 없음":
                logging.warning(f"본문 수집 실패: {full_url}")

            return {
                'title': title,
                'content': body,
                'date': date,
                'url': full_url
            }

        except requests.RequestException as e:
            logging.error(f"기사 본문({full_url}) 요청 실패: {e}")
        except Exception as e:
            logging.error(f"기사 본문({full_url}) 처리 중 오류: {e}")

        return {
            'title': '제목 없음',
            'content': '본문 없음',
            'date': datetime.now().strftime('%Y-%m-%d')
        }

    def fetch_archive_by_year(self, year: int, max_pages: int = 1, debug: bool = False) -> list:
        """
        특정 연도의 기사 URL 목록을 수집합니다.
        
        Args:
            year (int): 수집할 연도 (예: 2024)
            max_pages (int): 수집할 최대 페이지 수 (테스트용)
            debug (bool): v2.2 - True일 경우, debug_page.html을 저장합니다.
        
        Returns:
            list: 기사 정보(title, content, url, date) 딕셔너리의 리스트
        """
        articles = []
        
        for page in range(1, max_pages + 1):
            params = {
                'page': page,
                'page_size': 20, # v2.2: 100 -> 20으로 변경 (더 표준적인 값)
                'year': year
            }
            
            try:
                logging.info(f"{year}년 기사 목록 수집 중... (Page {page}/{max_pages})")
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                # v2.2: 디버깅 기능
                if debug and page == 1:
                    debug_file = os.path.join(os.path.dirname(__file__), 'debug_page.html')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logging.info(f"디버그 HTML 파일 저장 완료: {debug_file}")

                soup = BeautifulSoup(response.text, 'lxml')
                
                # v2.1 선택자 유지 (이전 테스트에서 실패했으나, 페이지 크기 변경 후 재시도)
                article_links = soup.select("section#section-list ul.type-list H2.titles a")
                
                if not article_links:
                    logging.warning(f"페이지 {page}에서 기사 링크를 찾을 수 없습니다.")
                    # v2.2: 대안 선택자 시도 (더 넓은 범위)
                    logging.info("대안 선택자 (section.article-list-content h4.titles a)로 재시도...")
                    article_links = soup.select("section.article-list-content h4.titles a")

                if not article_links:
                    logging.error(f"페이지 {page}에서 더 이상 기사를 찾을 수 없습니다. 수집을 중단합니다.")
                    logging.error(f"-> (v2.2) 'debug_page.html' 파일을 열어 HTML 구조를 직접 확인해주세요.")
                    break
                
                for link in article_links:
                    article_url = link.get('href')
                    if article_url and not article_url.startswith('http'):
                        
                        article_data = self.fetch_article_content(article_url)
                        if article_data:
                            articles.append(article_data)
                        
                        time.sleep(0.5) # 서버 부하 방지
            
            except requests.exceptions.RequestException as e:
                logging.error(f"기사 목록 수집 실패 (Page {page}): {e}")
                break
            except Exception as e:
                logging.error(f"알 수 없는 오류 (Page {page}): {e}")
                break
                
        logging.info(f"총 {len(articles)}개의 기사 수집 완료 (Year: {year}, Max Pages: {max_pages})")
        return articles

# --- 이 모듈을 직접 실행할 경우를 위한 테스트 코드 ---
if __name__ == "__main__":
    logging.info("ArticleCollector (v2.2) 모듈 테스트를 시작합니다.")
    
    collector = H2NewsArchiveCollector()
    
    # 2024년 1페이지만, 디버그 모드(debug=True)로 테스트
    articles_2024 = collector.fetch_archive_by_year(year=2024, max_pages=1, debug=True)
    
    if articles_2024:
        logging.info(f"--- 수집된 기사 샘플 (총 {len(articles_2024)}개) ---")
        
        for i, article in enumerate(articles_2024[:3]):
            print("\n" + "="*30 + f" 샘플 {i+1} " + "="*30)
            print(f"  [날짜] {article['date']}")
            print(f"  [제목] {article['title']}")
            print(f"  [URL] {article['url']}")
            print(f"  [본문] {article['content'][:150]}...")
        
        logging.info("\n✅ 테스트 성공: 기사 목록 및 본문 수집이 정상적으로 완료되었습니다.")
    else:
        logging.error("❌ 테스트 실패: 기사를 수집하지 못했습니다.")
        logging.info("➡️  'notion_version1/debug_page.html' 파일을 열어서 기사 목록이 보이는지 확인해주세요.")