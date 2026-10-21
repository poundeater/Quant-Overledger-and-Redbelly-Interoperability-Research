#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 scripts/make_diagrams.py && python3 scripts/build_site.py && python3 scripts/build_evidence.py && python3 scripts/build_reader.py && python3 scripts/add_zoom.py && python3 scripts/make_pdf.py && python3 scripts/make_docx.py && python3 scripts/check.py
