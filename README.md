# Sandcastle

Sandcastle is a deterministic, three-phase search pipeline designed for cheap, repeatable research workflows. Phase 1 collects raw search results. Phase 2 canonicalizes, deduplicates, and clusters results. Phase 3 provides a schema-only reasoning stub with placeholder outputs.

## Why no LLM in Phase 1/2
Phase 1 and 2 avoid LLMs to keep results deterministic, inexpensive, and reproducible. The pipeline relies on canonicalization rules, token-based similarity, and keyword clustering to ensure repeatable outputs given the same inputs and upstream responses.

## Quickstart

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

### Collect

```bash
sandcastle collect --queries queries.txt --engines searxng,brave --out data/collector.jsonl
```

With query expansion:

```bash
sandcastle collect --queries queries.txt --engines searxng --out data/collector.jsonl --expand
```

### Process

```bash
sandcastle process --in data/collector.jsonl --outdir data/ --keywords config/keywords.txt
```

### Reason (stub)

```bash
sandcastle reason --indir data/ --outdir data/
```

## Configuration

- `config/default.yaml` controls search endpoints, timeouts, user agent, dedupe threshold, and query expansion settings.
- `config/domains.yaml` defines include/exclude domain filters and toggles (Amazon, Pinterest, Reddit, YouTube, Quora are excluded by default).
- `config/keywords.txt` supplies the keyword phrases used to form clusters.
- `config/anchor_terms.txt` supplies anchor terms for query expansion.

## CLI examples

```bash
sandcastle collect --queries queries.txt --engines searxng --out data/collector.jsonl
sandcastle process --in data/collector.jsonl --outdir data/
sandcastle reason --indir data/ --outdir data/
```

## Design notes

- **Canonicalization**: URLs are normalized to HTTPS, lowercase hostnames, sorted query parameters, stripped tracking params, and stripped fragments. Trailing slashes and repeated slashes are normalized for consistency.
- **Deduplication**: First dedupes by exact canonical URL. Then performs near-duplicate detection using Jaccard similarity of title + snippet tokens (threshold configurable).
- **Clustering**: Keyword-based, multi-label assignment from `keywords.txt`. A result can belong to multiple clusters.

## Brave Search API costs
Brave Search offers a free tier (2,000 queries/month) and then costs $0.50 per 1,000 queries. Set `BRAVE_API_KEY` to enable it.

## Dependencies
- `requests`: HTTP client for search endpoints.
- `pydantic`: schema validation for outputs.
- `rapidfuzz`: fast Jaccard similarity for near-duplicate detection.
- `pyyaml`: configuration parsing.
- `click`: CLI argument parsing.
- `duckduckgo-search` (optional): DuckDuckGo adapter when enabled.
