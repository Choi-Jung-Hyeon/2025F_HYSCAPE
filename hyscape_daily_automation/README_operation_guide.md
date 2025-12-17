# Hyscape Daily Automation - Operation Guide

## Quick Start

### First Time Setup
1. Run `setup_production.bat`
2. Enter Python executable path when prompted
3. Enter project directory path when prompted

### Daily Execution
Double-click `RUN_autobriefing.bat` at 9 AM

## What It Does

The system performs 3 automated tasks:

### 1. News Briefing
- Crawls hydrogen industry news from RSS feeds and websites
- Summarizes articles using Gemini AI
- Processes PDF briefings from shared directory
- Sends comprehensive email to recipients

### 2. Gov Support
- Finds relevant government support programs
- Filters by technology keywords and company qualifications
- Logs recommendations (currently Slack notifications are disabled)

### 3. Notion Archive
- Uploads PDF briefings to Notion database
- Analyzes content with Gemini AI (sentiment, category, keywords)
- Archives processed PDFs automatically

## System Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.8 or higher
- **Internet Connection:** Required for API access
- **Dependencies:** Automatically installed via requirements.txt

## Logs

### Log Locations
- **Main Log:** `logs/unified_automation.log`
  - Contains all module execution details
  - Shows success/failure status for each task

- **Error Log:** `logs/error.log`
  - Contains error-specific information
  - Created when batch file execution fails

### Reading Logs
Logs follow this format:
```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message
```

## Troubleshooting

### Issue: Python not found
**Error Message:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Run `setup_production.bat` again
2. Find your Python path with: `where python` in Command Prompt
3. Enter the full path (example: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe`)

### Issue: Email not sent
**Symptoms:** Email section shows "Failed" in summary

**Solution:**
1. Check `config_production.py` file
2. Verify `SENDER_PASSWORD` is correct (should be: `cnpeherzeuzhdmbyc`)
3. Ensure Gmail app password has no spaces
4. Check internet connection

### Issue: Notion upload failed
**Symptoms:** Notion Archive shows 0 uploads

**Solution:**
1. Check `notion_config_production.py` file
2. Verify `NOTION_API_TOKEN` is correct
3. Verify `NOTION_DATABASE_ID` is correct
4. Test Notion connection in browser

### Issue: No PDFs found
**Symptoms:** Both PDF Briefing and Notion Archive show no files

**Solution:**
1. Check PDF directory: `../pdf/`
2. Ensure PDFs follow naming format: `YYMMDD_title.pdf`
3. Place PDF files in the shared pdf directory

### Issue: Import errors
**Symptoms:** Module import errors in logs

**Solution:**
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (must be 3.8+)
3. Reinstall dependencies in virtual environment if needed

## Configuration Changes

### Add/Remove Email Recipients

Edit `config_production.py`:
```python
RECEIVER_EMAIL = [
    "new.email@hyscape.co.kr",  # Add new recipient
    # "old.email@example.com",  # Comment out to remove
]
```

### Modify Keywords

Edit `config_production.py`:
```python
TARGET_KEYWORDS_TECH = [
    "new keyword",  # Add new keyword
    # ... existing keywords
]
```

### Change Gov Support Filters

Edit `config_production.yaml`:
```yaml
keywords:
  tech:
    - "new tech keyword"
    - "another keyword"
```

### Update Notion Database

Edit `notion_config_production.py`:
```python
NOTION_DATABASE_ID = "your_new_database_id"
```

## File Structure

```
hyscape_daily_automation/
├── main_unified.py              # Main entry point
├── config_production.py         # Python configuration
├── config_production.yaml       # Gov support configuration
├── notion_config_production.py  # Notion configuration
├── requirements.txt             # Python dependencies
│
├── modules/                     # Module adapters
│   ├── news_briefing.py         # News + Email module
│   ├── gov_support.py           # Gov support module
│   └── notion_archive.py        # Notion upload module
│
├── shared/                      # Shared utilities
│   ├── pdf_analyzer.py          # PDF processing
│   └── gemini_client.py         # Gemini API client
│
├── dependencies/                # Copied from existing systems
│   ├── source_fetcher/          # News crawling
│   ├── gov_support/             # Gov support crawling
│   ├── content_scraper.py       # Article extraction
│   ├── notifier.py              # Email sender
│   └── notion_uploader.py       # Notion uploader
│
├── logs/                        # Log files
├── RUN_autobriefing.bat         # One-click execution
├── setup_production.bat         # Path configuration
└── README_operation_guide.md    # This file
```

## Advanced Configuration

### Running Specific Modules Only

You can modify `main_unified.py` to comment out modules you don't want to run:

```python
# Comment out unwanted modules
# results['news_briefing'] = news_briefing.run()
results['gov_support'] = gov_support.run()
results['notion_archive'] = notion_archive.run()
```

### Changing Gemini Model

Edit `config_production.py`:
```python
GEMINI_MODEL = "gemini-2.0-flash"  # Current model
# GEMINI_MODEL = "gemini-1.5-pro"  # Alternative
```

### Adjusting Article Limits

Edit `config_production.py`:
```python
MAX_ARTICLES_PER_SOURCE = 3  # Articles per news source
MAX_TOTAL_ARTICLES = 5       # Total articles in email
```

## Scheduled Execution (Optional)

To run automatically at 9 AM daily:

### Option 1: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `C:\Path\To\hyscape_daily_automation\RUN_autobriefing.bat`

### Option 2: Manual Execution
Simply double-click `RUN_autobriefing.bat` when needed

## Contact

### Development Team
- **Developer:** 중현 (fourmi103@g.skku.edu)
- **Company:** Hyscape
- **Email:** ymkim@hyscape.co.kr

### Reporting Issues
Please include:
1. Error message from logs
2. Steps to reproduce
3. Screenshot of error (if applicable)
4. Log file: `logs/unified_automation.log`

## Version History

- **v1.0** (2025-12-17): Initial unified system release
  - Merged mail_version9, government_version2, notion_version3
  - Production credentials configured
  - One-click batch execution
  - Comprehensive error isolation
