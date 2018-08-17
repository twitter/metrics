#!/usr/bin/env bash
# Use Python 3.6+
python scripts/fetch_all_metrics.py || true
python scripts/fetch_augur_metrics.py || true
python scripts/gen_reports.py || true
python scripts/gen_graphs.py || true
python scripts/gen_index_pages.py || true
