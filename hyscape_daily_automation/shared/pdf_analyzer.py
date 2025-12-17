#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyscape Daily Automation - Shared PDF Analyzer

Unified PDF processing with dual-mode analysis:
- Mode 1: Keyword-based extraction (for news briefing emails)
- Mode 2: Comprehensive extraction (for Notion archiving)

Uses pdfplumber (primary) + PyPDF2 (fallback) for maximum robustness
"""

import os
import re
import glob
import shutil
import logging
from pathlib import Path
from typing import List, Optional

# PDF processing libraries (dual-library approach)
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available, will use PyPDF2 only")

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available, will use pdfplumber only")

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, use_fallback: bool = True) -> str:
    """
    Extract text from PDF using pdfplumber (primary) or PyPDF2 (fallback)

    Args:
        pdf_path: Path to PDF file
        use_fallback: If True, try PyPDF2 if pdfplumber fails

    Returns:
        Extracted text as string

    Raises:
        Exception: If both libraries fail
    """
    # Try pdfplumber first (more robust)
    if PDFPLUMBER_AVAILABLE:
        try:
            return _extract_with_pdfplumber(pdf_path)
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path}: {e}")
            if not use_fallback or not PYPDF2_AVAILABLE:
                raise

    # Fallback to PyPDF2
    if use_fallback and PYPDF2_AVAILABLE:
        try:
            return _extract_with_pypdf2(pdf_path)
        except Exception as e:
            logger.error(f"PyPDF2 also failed for {pdf_path}: {e}")
            raise

    raise Exception(f"No PDF library available or all failed for {pdf_path}")


def _extract_with_pdfplumber(pdf_path: str) -> str:
    """
    Extract text using pdfplumber (more robust, from notion_version3)

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted and cleaned text
    """
    logger.debug(f"Extracting with pdfplumber: {pdf_path}")
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num} from {pdf_path}: {e}")
                continue

    if not text_parts:
        raise Exception(f"No text extracted from {pdf_path}")

    # Join and clean
    full_text = "\n".join(text_parts)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)  # Remove excessive newlines
    full_text = re.sub(r' {2,}', ' ', full_text)  # Remove excessive spaces

    return full_text.strip()


def _extract_with_pypdf2(pdf_path: str) -> str:
    """
    Extract text using PyPDF2 (fallback, from mail_gov_integrated)

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text
    """
    logger.debug(f"Extracting with PyPDF2: {pdf_path}")
    text_parts = []

    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num} from {pdf_path}: {e}")
                continue

    if not text_parts:
        raise Exception(f"No text extracted from {pdf_path}")

    return "\n".join(text_parts).strip()


def extract_keyword_paragraphs(text: str, keywords: List[str]) -> List[str]:
    """
    Extract paragraphs containing any of the specified keywords
    (from mail_gov_integrated/pdf_reader.py)

    Args:
        text: Full PDF text
        keywords: List of keywords to match (case-insensitive)

    Returns:
        List of paragraphs containing keywords
    """
    if not text or not keywords:
        return []

    # Split into paragraphs (double newline or single newline with sufficient length)
    paragraphs = re.split(r'\n\n+', text)

    matched_paragraphs = []
    keywords_lower = [kw.lower() for kw in keywords]

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if len(paragraph) < 20:  # Skip very short paragraphs
            continue

        paragraph_lower = paragraph.lower()

        # Check if any keyword is in this paragraph
        for keyword in keywords_lower:
            if keyword in paragraph_lower:
                matched_paragraphs.append(paragraph)
                break  # Don't add the same paragraph twice

    return matched_paragraphs


def get_all_pdfs(pdf_dir: str) -> List[Path]:
    """
    Scan directory for PDF files

    Args:
        pdf_dir: Directory path to scan

    Returns:
        List of Path objects sorted by modification time (newest first)
    """
    pdf_dir_path = Path(pdf_dir)

    if not pdf_dir_path.exists():
        logger.warning(f"PDF directory does not exist: {pdf_dir}")
        return []

    # Find all PDF files
    pdf_files = list(pdf_dir_path.glob("*.pdf"))

    # Sort by modification time (newest first)
    pdf_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    logger.info(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
    return pdf_files


def archive_pdf(pdf_path: str, archive_dir: str) -> bool:
    """
    Move processed PDF to archive directory

    Args:
        pdf_path: Path to PDF file
        archive_dir: Archive directory path

    Returns:
        True if successful, False otherwise
    """
    try:
        pdf_path_obj = Path(pdf_path)
        archive_dir_obj = Path(archive_dir)

        # Create archive directory if not exists
        archive_dir_obj.mkdir(parents=True, exist_ok=True)

        # Destination path
        dest_path = archive_dir_obj / pdf_path_obj.name

        # Move file
        shutil.move(str(pdf_path_obj), str(dest_path))
        logger.info(f"Archived: {pdf_path_obj.name} → {archive_dir}")

        return True

    except Exception as e:
        logger.error(f"Failed to archive {pdf_path}: {e}")
        return False


def extract_date_from_filename(filename: str) -> Optional[str]:
    """
    Extract date from filename in YYMMDD format

    Args:
        filename: PDF filename (e.g., "251204_일간 수소 이슈 브리핑.pdf")

    Returns:
        Date in ISO format (YYYY-MM-DD) or None if not found
    """
    # Match YYMMDD pattern at start of filename
    match = re.match(r'(\d{2})(\d{2})(\d{2})', filename)

    if match:
        yy, mm, dd = match.groups()
        # Assume 20YY for years
        year = f"20{yy}"
        return f"{year}-{mm}-{dd}"

    return None
