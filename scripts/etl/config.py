"""Paths shared by ETL stages; resolved relative to the project checkout."""
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_JSON_SITE = os.path.join(SITE_DIR, 'data.json')
OUTPUT_JSON_ROOT = os.path.join(PROJECT_ROOT, 'data.json')
