#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Notion Archive Module

Workflow:
1. Scan shared PDF directory
2. Extract text from PDFs
3. Analyze with Gemini AI (sentiment, category, keywords)
4. Upload to Notion database
5. Archive processed PDFs
"""

import sys
import os
import logging
from typing import Dict

# Add dependencies to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dependencies'))

# Import from dependencies
from notion_uploader import NotionUploader

# Import from shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.pdf_analyzer import (
    extract_text_from_pdf,
    get_all_pdfs,
    archive_pdf,
    extract_date_from_filename
)
from shared.gemini_client import GeminiClient

# Import configs
import notion_config_production as notion_config
import config_production as config

logger = logging.getLogger(__name__)


def run() -> Dict:
    """
    Execute Notion archive workflow

    Returns:
        dict: {
            "status": "success" | "failed",
            "uploaded": int,
            "error": str (if failed)
        }
    """
    logger.info("[NotionArchive] Starting Notion archive module...")

    try:
        # Initialize Gemini client
        gemini_client = GeminiClient(config.GOOGLE_API_KEY, config.GEMINI_MODEL)

        # Initialize Notion uploader (reads config from dependencies/config.py)
        notion_uploader = NotionUploader()

        # Test Notion connection
        logger.info("[NotionArchive] Testing Notion connection...")
        if not notion_uploader.test_connection():
            raise Exception("Failed to connect to Notion")

        # Get PDFs from shared directory
        pdf_dir = config.PDF_DIR
        logger.info(f"[NotionArchive] Scanning PDF directory: {pdf_dir}")
        pdf_files = get_all_pdfs(pdf_dir)

        if not pdf_files:
            logger.info("[NotionArchive] No PDF files found in shared directory")
            return {
                "status": "success",
                "uploaded": 0
            }

        # Process each PDF
        uploaded_count = 0
        archive_dir = "../pdf_archive/"

        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                logger.info(f"[NotionArchive] [{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

                # Extract text
                text = extract_text_from_pdf(str(pdf_file))

                # Analyze with Gemini
                analysis = gemini_client.analyze_briefing(
                    text,
                    notion_config.ANALYSIS_PROMPT
                )

                # Extract date from filename
                date_str = extract_date_from_filename(pdf_file.name)
                if not date_str:
                    logger.warning(f"[NotionArchive]   Could not extract date from filename: {pdf_file.name}")
                    continue

                # Prepare data for Notion
                briefing_data = {
                    "title": pdf_file.name,
                    "date": date_str,
                    "summary": analysis.get("summary", ""),
                    "url": "",  # No URL for local PDFs
                    "sentiment": analysis.get("sentiment", "Neutral"),
                    "category": analysis.get("category", "기관"),
                    "keywords": analysis.get("keywords", [])
                }

                # Upload to Notion
                success = notion_uploader.upload_briefing(briefing_data)

                if success:
                    logger.info(f"[NotionArchive]   ✅ Uploaded to Notion")

                    # Archive PDF
                    if archive_pdf(str(pdf_file), archive_dir):
                        logger.info(f"[NotionArchive]   ✅ Archived PDF")
                        uploaded_count += 1
                    else:
                        logger.warning(f"[NotionArchive]   ⚠️ Failed to archive PDF")
                else:
                    logger.error(f"[NotionArchive]   ❌ Failed to upload to Notion")

            except Exception as e:
                logger.error(f"[NotionArchive]   ❌ Failed to process {pdf_file.name}: {e}")
                continue

        logger.info(f"[NotionArchive] ✅ Successfully uploaded {uploaded_count}/{len(pdf_files)} PDFs")

        return {
            "status": "success",
            "uploaded": uploaded_count
        }

    except Exception as e:
        logger.error(f"[NotionArchive] ❌ Module failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }
