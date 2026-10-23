# Could Redbelly connect to Quant's Overledger? (TASK-29)

Feasibility research on whether Redbelly could connect to Quant's Overledger, what that would take, and what it could offer institutions. Public sources only. Redbelly and Quant have no announced partnership or talks, and nothing here suggests otherwise.

Live site: https://quant-overledger-research.vercel.app

## Deliverables

| Deliverable | Where |
| --- | --- |
| Report | the site, `REPORT.md`, and `public/downloads/Quant-Overledger-Redbelly-Report.pdf` and `.docx` (both linked in the site header; the PDF also from the home page) |
| Community summary (paragraphs and X thread) | `COMMUNITY-SUMMARY.md` |
| Source list, link for every claim | `SOURCES.md` and the Sources page |
| Plain words glossary | `GLOSSARY.md` and the Glossary page |
| Community summary as a page with copy buttons | the Community page |
| Evidence | `evidence/` and the Evidence page |

## Labels

Every finding paragraph carries one label. **Confirmed**: a linked source says it. **Tested**: we ran the call ourselves, output in `evidence/tests/`. **Analysis**: our reasoning from confirmed facts. **Unknown**: no source reviewed answers it. Claims cite sources as `[S#]` and own tests as `[T#]`.

## Evidence

`evidence/snapshots/` holds a saved copy of each source page. Pages that block automated tools (S2, S3, S4, S5, S15) were copied as text from a normal browser on 20 October 2026. `evidence/manifest.txt` lists capture times and SHA-256 hashes. API keys are never stored.

## Rebuild and check

```
pip install markdown reportlab python-docx beautifulsoup4
sudo apt-get install pandoc poppler-utils
sh build.sh                  # every step in order, ends with check.py: RESULT: PASS
python3 -m http.server -d public 8000   # local preview
```

Run `build.sh`, not single scripts: `build_site.py` clears the evidence pages, and `build_evidence.py`, `build_reader.py` and `add_zoom.py` must run after it. A rebuild also writes a new PDF and Word file even when `REPORT.md` did not change (new timestamps); restore them with `git checkout public/downloads` if the report text is unchanged.

Optional: put private words to block (names, handles), one per line, in a git-ignored `.denylist` file. `check.py` then also scans the text and the built site for them.

## Deploy

Static site on Vercel. `vercel.json` serves `public/` with clean URLs, no build step and basic security headers. It is edited by hand; the build does not rewrite it.

## Licences

Fonts: Be Vietnam Pro and JetBrains Mono, SIL Open Font License 1.1, self-hosted. Logo and icon from the Task Board brand kit.
