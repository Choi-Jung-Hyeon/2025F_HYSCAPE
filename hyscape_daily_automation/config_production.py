#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Production Configuration
Unified settings for news briefing, gov support, and Notion archive
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# ===== Google Gemini AI =====
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

# ===== Gmail SMTP Settings =====
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SENDER_NAME = "Hyscape Automation"

RECEIVER_EMAIL = [
    "fourmi103@g.skku.edu",
    "ymkim@hyscape.co.kr",
    "h2lee@hyscape.co.kr",
    "eguitar97@naver.com"
]

EMAIL_SUBJECT_TEMPLATE = "[Hyscape Daily] {date}"

# ===== Article Collection Limits =====
MAX_ARTICLES_PER_SOURCE = 3
MAX_TOTAL_ARTICLES = 5
MAX_NAVER_PER_KEYWORD = 2
MAX_GOOGLE_PER_KEYWORD = 2

SORT_BY = "date"
DATE_FORMAT = "%Y년 %m월 %d일"

# ===== Target Keywords (Technology) =====
TARGET_KEYWORDS_TECH = [
    "PEM 수전해", "AEM 수전해", "PEM 연료전지", "연료전지",
    "촉매", "로딩량", "촉매 사용량", "전해질막",
    "내구성", "durability", "수전해 시스템",
    "재생에너지", "태양광", "풍력", "지열", "수력",
    "그린수소", "청정수소", "수소 생산", "수소 저장",
    "수소 운송", "수소경제", "수소충전소", "암모니아"
]

# ===== Target Keywords (Companies) =====
TARGET_COMPANIES = [
    # 고액 투자 기업
    "Electric Hydrogen", "EnerVenue", "Koloma", "Ohmium", "ZeroAvia",
    "Energy Tree Solutions", "HYSETCO", "Hysata", "LONGi Solar", "LONGi", "Verdagy",

    # 중액 투자 기업
    "Sunshine Hydrogen", "Steelhead Composites", "Power to Hydrogen",
    "Molten Industries", "Hyproof Technologies",

    # 기타 주요 기업
    "Rongcheng New Energy", "ULEMCo", "PuriFire Energy", "Neprie",
    "Brineworks", "Leidong Zhichuang", "Yiting Technology",

    # 한국 주요 기업
    "삼성중공업", "현대건설", "현대로템", "고려아연",
    "두산에너빌리티", "두산에너지빌리티", "아헤스", "블루에프씨",
    "한국수력원자력", "한수원", "GS",

    # 해외 주요 기업
    "ACWA Power", "Larsen & Toubro", "L&T", "EnBW",
    "Tecnicas Reunidas", "Sinopec", "티센크루프", "누세라",

    # 추가 기업
    "Nel Hydrogen", "Plug Power", "ITM Power", "Accelera by Cummins",
    "Siemens Energy", "Sungrow", "PERIC", "Elogen", "Fortescue Future Industries (FFI)",
    "Fusion Fuel", "Quest-One (H-Tec Systems)", "Ohmium",
    "Guofuhee Hydrogen Energy Equipment", "Hygreen Energy", "H2B2 Electrolysis Technologies",
    "Green H2 Systems", "Neuman Esser", "Shandong Saikesai Hydrogen Energy",
    "Shanghai Electric", "China Aerospace Science and Tech Corp", "FABRUM",
    "Schaeffler Technologies", "BriHyNergy", "Changchun Green Dynamic Hydrogen Green Technology",
    "Eastern Electrolyser Ltd.", "Jiangsu Qingneng New Energy Technology Co.Ltd.,",
    "EPC Energy", "Shanghai REFIRE Group Limited", "Beijing Aerospace Advanced Hydrogen Energy",
    "Chunhua Hydrogen Energy Technology", "Weifu Hi-Tech", "Hytron", "Hynovation",
    "Shanghai H-Ray S&T Co.Ltd", "Shuangrui Environment", "GreenH Electrolysis",
    "Hande Automation & Hydrogen", "Enapter", "H2 Core Systems",
    "JA-Gastechnology", "H2Vector", "SPF Hydrogen Energy", "EVE (Huizhou Yiwei) Hydrogen Energy",
    "Future Hydrogen Energy", "Ansaldo Green Tech"
]

TARGET_KEYWORDS = TARGET_KEYWORDS_TECH + TARGET_COMPANIES

# ===== Naver News Keywords =====
NAVER_KEYWORDS = [
    "수소 산업",
    "수소 경제",
    "그린수소",
    "수소 에너지"
]

# ===== Google News Keywords =====
GOOGLE_KEYWORDS = [
    "hydrogen industry",
    "hydrogen energy",
    "green hydrogen",
    "hydrogen economy",
    "fuel cell"
]

# ===== News Sources =====
NEWS_SOURCES = {
    "월간수소경제": {
        "url": "http://www.h2news.kr/rss/S1N1.xml",
        "type": "rss",
        "status": "active",
        "description": "한국 수소 산업 전문 미디어"
    },

    "Hydrogen Central": {
        "url": "https://hydrogen-central.com/feed/",
        "type": "rss",
        "status": "active",
        "description": "글로벌 수소 뉴스 포털"
    },

    "Fuel Cells Works": {
        "url": "https://fuelcellsworks.com/feed/",
        "type": "rss",
        "status": "active",
        "description": "연료전지 및 수소 기술 전문"
    },

    "H2 Energy News": {
        "url": "https://www.h2-view.com/feed/",
        "type": "rss",
        "status": "active",
        "description": "수소 에너지 산업 뉴스"
    },

    "Hydrogen Fuel News": {
        "url": "https://www.hydrogenfuelnews.com/feed/",
        "type": "rss",
        "status": "active",
        "description": "수소 연료 뉴스 및 분석"
    },

    "H2-international": {
        "url": "https://www.h2-international.com/feed/",
        "type": "rss",
        "status": "active",
        "description": "국제 수소 산업 뉴스"
    },

    "H2 View": {
        "type": "web",
        "url": "https://www.h2-view.com/news/all-news/",
        "article_selector": "article.post",
        "title_selector": "h2.entry-title",
        "link_selector": "a",
        "date_selector": "time.entry-date",
        "status": "inactive",
        "description": "H2 View 웹 스크래핑",
        "extra": {
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        }
    },

    "네이버뉴스": {
        "type": "naver",
        "status": "inactive",
        "description": "네이버 뉴스 검색 API (회사 계정 발급 후 사용)",
        "extra": {
            "client_id": "YOUR_CLIENT_ID_HERE",
            "client_secret": "YOUR_CLIENT_SECRET_HERE"
        }
    },

    "구글뉴스": {
        "type": "google",
        "status": "inactive",
        "description": "구글 뉴스 검색",
        "extra": {}
    }
}

# ===== PDF Settings =====
# Platform-independent path configuration
# Linux: /home/fourmi103/2025F_HYSCAPE/pdf/
# Windows: H:\부서\cjh\pdf\
BASE_DIR = Path(__file__).parent.parent  # Points to 2025F_HYSCAPE directory
PDF_DIR = str(BASE_DIR / "pdf")
PDF_TARGET_KEYWORDS = TARGET_KEYWORDS_TECH + TARGET_COMPANIES

# ===== Logging Settings =====
# Platform-independent path configuration
LOG_DIR = str(Path(__file__).parent / "logs")
FAILED_SOURCES_LOG = str(Path(__file__).parent / "logs" / "failed_sources.txt")
LOG_LEVEL = "INFO"

# ===== Summary Prompt Template =====
SUMMARY_PROMPT_TEMPLATE = """
다음 수소 관련 기사를 분석하여 핵심 내용을 요약해주세요.

**중요: 다음 회사들이 언급되면 반드시 강조해주세요**:
{company_keywords}

**기술 키워드**:
{tech_keywords}

---

**기사 제목**: {title}

**기사 내용**:
{content}

---

**요약 지침**:
1. 핵심 내용 3-5줄로 요약 (한국어)
2. 회사 키워드가 포함되면 **굵게** 표시하고 무슨 일을 하는지 명확히 설명
3. 기술 키워드가 포함되면 기술 세부사항 포함
4. 투자/계약/협력 관련 내용은 금액과 시기 포함
5. 구체적인 수치(용량, 금액, 시기) 포함

**요약**:
"""

# ===== System Settings =====
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2
ENABLE_CACHE = True
CACHE_EXPIRY_HOURS = 24

# ===== HTTP Headers =====
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

DEFAULT_HEADERS = {
    'User-Agent': DEFAULT_USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# ===== Directory Creation =====
# Create directories if they don't exist
Path(PDF_DIR).mkdir(parents=True, exist_ok=True)
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
