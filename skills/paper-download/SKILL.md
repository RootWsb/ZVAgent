---
name: paper-download
description: Download legal open-access academic paper PDFs and source documents from DOI, arXiv ID/URL, PMCID, or direct PDF URL. Use when the user asks to download, save, fetch, archive, or collect paper full texts/PDFs, especially after paper-lookup finds metadata or open-access links. Never use for paywall circumvention or Sci-Hub-style requests.
allowed-tools: Read Write Edit Bash web_fetch
metadata:
  skill-author: ZVAgent
---

# Paper Download

Download legally accessible scholarly full text into the workspace. This skill complements `paper-lookup`: first find the paper and open-access locations, then download the PDF or source document.

## When To Use

Use this skill when the user asks to:

- Download or save a paper PDF.
- Fetch full text for a DOI, arXiv ID, arXiv URL, PMCID, PMC URL, or direct PDF URL.
- Build a local folder of papers for reading, literature review, citation management, or knowledge-base archiving.
- Continue from `paper-lookup` results that include `url_for_pdf`, `best_oa_location`, arXiv IDs, PMC IDs, CORE links, or publisher/repository PDF links.

Do not use this skill for:

- Circumventing paywalls, bypassing authentication, or using Sci-Hub mirrors.
- Downloading copyrighted papers when no legal open-access copy is available.
- Bulk downloading at high rates from publisher sites.

## Core Workflow

1. **Classify the input**
   - Direct PDF URL: download it.
   - arXiv ID or URL: convert to `https://arxiv.org/pdf/{id}.pdf`.
   - PMCID or PMC URL: use PMC PDF endpoints.
   - DOI or doi.org URL: query Unpaywall for legal open-access locations. If `UNPAYWALL_EMAIL` is not set, ask the user for an email or use `--email`.
   - Title-only request: use `paper-lookup` first to find DOI/arXiv/PMCID/OA links.

2. **Check legality and provenance**
   - Prefer open repositories, arXiv, PMC, publisher-hosted OA PDFs, and Unpaywall `best_oa_location`.
   - Report when no open copy is found instead of looking for unauthorized mirrors.

3. **Download to workspace**
   - Default folder: `papers/`.
   - Use safe filenames based on title/identifier.
   - Preserve metadata in a JSON sidecar when possible.

4. **Return a concise result**
   - Local file path.
   - Source URL used.
   - OA status/license/version when available.
   - Any failures and the next legal fallback.

## Script

Use the bundled script for repeatable downloads:

```bash
python skills/paper-download/scripts/download_paper.py "10.48550/arXiv.1706.03762" --output-dir papers --email you@example.com
```

Examples:

```bash
# arXiv ID
python skills/paper-download/scripts/download_paper.py 1706.03762 --output-dir papers

# arXiv URL
python skills/paper-download/scripts/download_paper.py https://arxiv.org/abs/1706.03762 --output-dir papers

# DOI via Unpaywall
python skills/paper-download/scripts/download_paper.py 10.1038/s41586-021-03819-2 --email you@example.com --output-dir papers

# PMCID
python skills/paper-download/scripts/download_paper.py PMC7029759 --output-dir papers

# Direct PDF URL
python skills/paper-download/scripts/download_paper.py https://example.org/paper.pdf --output-dir papers

# Preview candidate URLs without downloading
python skills/paper-download/scripts/download_paper.py 1706.03762 --dry-run
```

The script prints JSON with:

- `ok`
- `identifier`
- `source_type`
- `download_url`
- `output_path`
- `metadata_path`
- `oa_status`
- `license`
- `version`
- `error`

## Environment

For DOI downloads through Unpaywall:

```bash
set UNPAYWALL_EMAIL=you@example.com
```

Unpaywall requires a real email address. If none is configured, do not invent one; ask the user or pass `--email`.

## Fallbacks

If the script cannot download:

1. Use `paper-lookup` to query Crossref/Semantic Scholar/OpenAlex for identifiers.
2. Use Unpaywall on the DOI.
3. Use PMC when a PMCID exists.
4. Use arXiv when an arXiv ID exists.
5. Return the legal landing page when no direct PDF is available.

## Safety

- Never suggest unauthorized mirrors.
- Respect robots, rate limits, and publisher terms.
- For bulk jobs, keep requests slow and small, and prefer open repositories.
- If a paper is closed access, say so plainly and offer legal alternatives: abstract, citation, preprint search, library access, author manuscript request, or interlibrary loan.
