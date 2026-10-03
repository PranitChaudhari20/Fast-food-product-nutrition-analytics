#!/usr/bin/env bash
# Reproduce the whole project from the raw file (about 1 minute).
set -e
python python/01_clean_data.py            # 1,147 raw rows -> 713 clean menu items
python python/02_analysis.py              # summary tables + charts in screenshots/
python python/03_build_excel.py           # Excel workbook (open+save it once so values are cached)
# optional, needs a MySQL/MariaDB server:
# python python/run_sql_queries.py --user root --password "..."
