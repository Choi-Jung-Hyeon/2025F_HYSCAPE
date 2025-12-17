#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Government Support Module

Workflow:
1. Crawl government support websites (K-Startup, IRIS, Bizinfo)
2. Filter by relevance (tech keywords, support keywords, qualification)
3. Score and rank by relevance
4. Log recommendations (Slack disabled)
"""

import sys
import os
import logging
from typing import Dict

# Add dependencies to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dependencies'))

# Import from dependencies
from gov_support.gov_support_manager import GovSupportManager

logger = logging.getLogger(__name__)


def run() -> Dict:
    """
    Execute government support workflow

    Returns:
        dict: {
            "status": "success" | "failed",
            "recommendations": int,
            "error": str (if failed)
        }
    """
    logger.info("[GovSupport] Starting government support module...")

    try:
        # Get config path (relative to this module)
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config_production.yaml')

        # Initialize GovSupportManager
        logger.info(f"[GovSupport] Loading config from: {config_path}")
        gov_manager = GovSupportManager(config_path)

        # Collect and filter notices
        logger.info("[GovSupport] Collecting government support notices...")
        recommended_notices = gov_manager.get_recommended_notices(top_n=5)

        if recommended_notices:
            logger.info(f"[GovSupport] ✅ Found {len(recommended_notices)} relevant notices")

            # Log notices (Slack is disabled in production)
            for i, notice in enumerate(recommended_notices, 1):
                logger.info(f"[GovSupport]   {i}. {notice.get('title', 'N/A')[:60]} (Score: {notice.get('score', 0)})")

            return {
                "status": "success",
                "recommendations": len(recommended_notices)
            }
        else:
            logger.info("[GovSupport] No relevant notices found")
            return {
                "status": "success",
                "recommendations": 0
            }

    except Exception as e:
        logger.error(f"[GovSupport] ❌ Module failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }
