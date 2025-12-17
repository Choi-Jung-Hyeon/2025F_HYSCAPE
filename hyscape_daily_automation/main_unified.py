#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Unified Daily Automation System

Main orchestrator that executes 3 independent modules:
1. News Briefing (PDF + News + Email)
2. Government Support (Crawler + Filter)
3. Notion Archive (PDF + Gemini + Notion)

Each module runs independently with error isolation.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules
from modules import news_briefing, gov_support, notion_archive


def setup_logging():
    """Configure logging for the unified system"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'unified_automation.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def main() -> int:
    """
    Main orchestrator function

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    logger = setup_logging()

    # Print banner
    print("\n" + "=" * 80)
    print("⚡ Hyscape Unified Daily Automation")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    # Track results for each module
    results = {
        'news_briefing': None,
        'gov_support': None,
        'notion_archive': None
    }

    # Task 1: News Briefing Email
    try:
        logger.info("\n[1/3] News Briefing Email...")
        result = news_briefing.run()
        results['news_briefing'] = result

        if result.get('status') == 'success':
            articles = result.get('articles_sent', 0)
            logger.info(f"✅ News briefing completed ({articles} articles)")
        else:
            logger.error(f"❌ News briefing failed: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ News briefing failed: {e}", exc_info=True)
        results['news_briefing'] = {"status": "failed", "error": str(e)}

    # Task 2: Government Support Programs
    try:
        logger.info("\n[2/3] Government Support Programs...")
        result = gov_support.run()
        results['gov_support'] = result

        if result.get('status') == 'success':
            recommendations = result.get('recommendations', 0)
            logger.info(f"✅ Gov support completed ({recommendations} recommendations)")
        else:
            logger.error(f"❌ Gov support failed: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Gov support failed: {e}", exc_info=True)
        results['gov_support'] = {"status": "failed", "error": str(e)}

    # Task 3: Notion Archive Upload
    try:
        logger.info("\n[3/3] Notion Archive Upload...")
        result = notion_archive.run()
        results['notion_archive'] = result

        if result.get('status') == 'success':
            uploaded = result.get('uploaded', 0)
            logger.info(f"✅ Notion archive completed ({uploaded} PDFs uploaded)")
        else:
            logger.error(f"❌ Notion archive failed: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Notion archive failed: {e}", exc_info=True)
        results['notion_archive'] = {"status": "failed", "error": str(e)}

    # Print summary
    print("\n" + "=" * 80)
    print("📊 Automation Summary")
    print("=" * 80)

    news_success = results['news_briefing'] and results['news_briefing'].get('status') == 'success'
    gov_success = results['gov_support'] and results['gov_support'].get('status') == 'success'
    notion_success = results['notion_archive'] and results['notion_archive'].get('status') == 'success'

    print(f"News Briefing:    {'✅ Success' if news_success else '❌ Failed'}")
    print(f"Gov Support:      {'✅ Success' if gov_success else '❌ Failed'}")
    print(f"Notion Archive:   {'✅ Success' if notion_success else '❌ Failed'}")
    print("=" * 80 + "\n")

    # Return exit code
    # Success if at least one module succeeded
    if news_success or gov_success or notion_success:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
