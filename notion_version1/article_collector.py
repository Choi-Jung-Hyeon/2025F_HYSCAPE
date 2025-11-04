#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# article_collector.py (Notion Archive - Phase 1 - v2)
# (newspaper3k 라이브러리 제거, requests + BeautifulSoup4로 직접 파싱)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import config  # config.py 파일 로드
import logging
import time
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class H2NewsArchiveCollector:
    """
    기획서(PDF) 기반 '월간수소경제' 아카이브 수집기
    [cite: 55-69]
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
            # H2News는 여러 날짜 li 항목 중 '승인'을 사용
            date_items = soup.select("ul.infomation li")
            for item in date_items:
                text = item.get_text()
                if "승인" in text:
                    date_str = text.replace("승인", "").strip()
                    # 'YYYY.MM.DD HH:MM' 형식을 'YYYY-MM-DD'로 변환
                    dt = datetime.strptime(date_str, '%Y.%m.%d %H:%M')
                    return dt.strftime('%Y-%m-%d')
        except Exception as e:
            logging.warning(f"날짜 파싱 오류: {e}")
        # 실패 시 현재 날짜 반환 (Notion 필수 필드용)
        return datetime.now().strftime('%Y-%m-%d')

    def fetch_article_content(self, article_url: str) -> dict:
        """
        개별 기사 URL을 받아 제목, 본문, 날짜를 스크래핑합니다.
        (Newspaper 라이브러리 대체)
        """
        full_url = urljoin(self.root_url, article_url)
        
        try:
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 제목 추출 (H2News 기준)
            title_tag = soup.select_one("header.article-view-header h3.heading")
            title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
            
            # 본문 추출 (H2News 기준)
            content_div = soup.select_one("div#article-view-content-div")
            if content_div:
                # 불필요한 태그 제거 (광고, SCRIPT 등)
                for unwanted in content_div.select("script, style, table, figure.figure-img-multi"):
                    unwanted.decompose()
                content = content_div.get_text(separator="\n", strip=True)
            else:
                content = "본문 없음"
            
            # 날짜 추출
            date_str = self._parse_article_date(soup)
            
            return {
                "title": title,
                "content": content,
                "url": full_url,
                "date": date_str
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"기사 내용 수집 실패 ({full_url}): {e}")
            return None
        except Exception as e:
            logging.error(f"기사 파싱 중 알 수 없는 오류 ({full_url}): {e}")
            return None

    def fetch_archive_by_year(self, year: int, max_pages: int = 1) -> list:
        """
        특정 연도의 기사 URL 목록을 수집합니다.
        [cite: 63-66]
        
        Args:
            year (int): 수집할 연도 (예: 2024)
            max_pages (int): 수집할 최대 페이지 수 (테스트용)
        
        Returns:
            list: 기사 정보(title, content, url, date) 딕셔너리의 리스트
        """
        articles = []
        
        for page in range(1, max_pages + 1):
            params = {
                'page': page,
                'page_size': 100, # PDF 기획안 기준 [cite: 66]
                'year': year
            }
            
            try:
                logging.info(f"{year}년 기사 목록 수집 중... (Page {page}/{max_pages})")
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # H2News 목록 기준 (div.list-block)
                article_links = soup.select("section.article-list-content div.list-block a")
                
                if not article_links:
                    logging.info(f"페이지 {page}에서 더 이상 기사를 찾을 수 없습니다. 수집을 중단합니다.")
                    break
                
                for link in article_links:
                    article_url = link.get('href')
                    if article_url and not article_url.startswith('http'):
                        
                        # 기사 본문 즉시 수집
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
    logging.info("ArticleCollector (v2) 모듈 테스트를 시작합니다.")
    
    collector = H2NewsArchiveCollector()
    
    # PDF 기획안의 2024년 기준, 1페이지만 테스트
    # [cite: 72]
    articles_2024 = collector.fetch_archive_by_year(year=2024, max_pages=1)
    
    if articles_2024:
        logging.info(f"--- 수집된 기사 샘플 (총 {len(articles_2024)}개) ---")
        
        # 상위 3개 기사 샘플 출력
        for i, article in enumerate(articles_2024[:3]):
            print("\n" + "="*30 + f" 샘플 {i+1} " + "="*30)
            print(f"  [날짜] {article['date']}")
            print(f"  [제목] {article['title']}")
            print(f"  [URL] {article['url']}")
            print(f"  [본문] {article['content'][:150]}...")
        
        logging.info("\n테스트 성공: 기사 목록 및 본문 수집이 정상적으로 완료되었습니다.")
    else:
        logging.error("테스트 실패: 기사를 수집하지 못했습니다.")