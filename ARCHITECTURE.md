# Sandcastle Architecture

```
queries.txt
   |
   v
Phase 1: Collector
   - searxng/brave/ddg adapters
   - append-only JSONL
   - optional query expansion
   |
   v
Phase 2: Processor
   - canonicalize URLs
   - dedupe (exact + near-duplicate)
   - domain filters
   - keyword clustering + term extraction
   |
   v
Phase 3: Reasoner (stub)
   - schema validation
   - placeholder strategy + questions
```

## Phase responsibilities

- **Phase 1 Collector**: Fetches raw results from search engines and writes append-only JSONL output to `data/collector.jsonl`. Optionally performs deterministic query expansion.
- **Phase 2 Processor**: Canonicalizes URLs, deduplicates results, applies domain filters, clusters results by keywords, and extracts term statistics.
- **Phase 3 Reasoner (stub)**: Reads processed outputs, validates schemas, and writes placeholder strategy and research question files.

## File format specs

- `data/collector.jsonl`: One JSON object per result with query, engine, rank, URL, title, snippet, timestamp, and raw metadata.
- `data/deduped.json`: List of canonicalized and deduplicated results with cluster IDs.
- `data/clusters.json`: Cluster summaries with members, top terms, and intent counts.
- `data/terms.json`: Global term and bigram frequencies.
- `data/strategy.json`: Placeholder strategy outputs (LLM stub).
- `data/research_questions.json`: Placeholder research questions (LLM stub).
