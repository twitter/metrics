#!/usr/bin/env bash
echo "Use Python 3"
python scripts/fetch_all_metrics.py
python scripts/fetch_augur_metrics.py
python scripts/gen_reports.py
python scripts/gen_graphs.py
python scripts/gen_index_pages.py
python scripts/fetch_year_in_review.py
