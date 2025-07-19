# src/scrapers/__init__.py
"""Scrapers do sistema"""

# Import direto sem relative imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scrapers.base_scraper import BaseScraper
from scrapers.zapimoveis_scraper import ZapImoveisScraper

__all__ = ['BaseScraper', 'ZapImoveisScraper']
