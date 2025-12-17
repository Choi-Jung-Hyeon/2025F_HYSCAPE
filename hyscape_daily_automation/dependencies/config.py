#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compatibility shim - redirects to config_production
This allows copied dependency files to work without modification
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import everything from config_production
from config_production import *

# Import Notion-specific configs (for NotionUploader compatibility)
from notion_config_production import (
    NOTION_API_TOKEN as NOTION_API_KEY,  # Alias for compatibility
    NOTION_DATABASE_ID,
    NOTION_PROPERTIES,
    SENTIMENT_TAGS,
    CATEGORY_TAGS,
    ANALYSIS_PROMPT
)
