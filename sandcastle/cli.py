from __future__ import annotations

import json
import os
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import click

from sandcastle.collectors import brave, ddg, searxng
from sandcastle.config import load_config, load_domains
from sandcastle.models import ClusterSummary, ResearchQuestion, StrategyItem, TermsSummary
from sandcastle.processor.clustering import build_clusters, load_keywords
from sandcastle.processor.dedupe import dedupe_records, normalize_records
from sandcastle.processor.filters import apply_domain_filters
from sandcastle.processor.text import tokenize_text
from sandcastle.processor.terms import aggregate_terms


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_queries(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def append_jsonl(path: Path, payloads: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_anchor_terms(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip().lower() for line in handle if line.strip()]


def extract_phrases(texts: list[str], anchor_terms: list[str], max_followups: int) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        tokens = tokenize_text(text)
        for size in range(2, 5):
            for idx in range(len(tokens) - size + 1):
                phrase = " ".join(tokens[idx : idx + size])
                if any(anchor in phrase for anchor in anchor_terms):
                    counter[phrase] += 1
    phrases = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [phrase for phrase, _ in phrases[:max_followups]]


@click.group()
def main() -> None:
    """Sandcastle pipeline CLI."""


@main.command()
@click.option("--queries", "queries_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--engines", default="searxng", help="Comma-separated engines")
@click.option("--out", "out_path", type=click.Path(dir_okay=False), required=True)
@click.option("--expand", is_flag=True, default=False)
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--anchor-terms", "anchor_terms_path", type=click.Path(exists=True, dir_okay=False), default="config/anchor_terms.txt")
def collect(queries_path: str, engines: str, out_path: str, expand: bool, config_path: str | None, anchor_terms_path: str) -> None:
    """Collect raw search results into append-only JSONL."""
    config = load_config(Path(config_path) if config_path else None)
    query_list = read_queries(Path(queries_path))
    engine_list = [engine.strip().lower() for engine in engines.split(",") if engine.strip()]

    queue = deque(query_list)
    seen_queries = set(query_list)
    queries_all_path = Path("data/queries_all.txt")
    if expand:
        queries_all_path.parent.mkdir(parents=True, exist_ok=True)
        queries_all_path.write_text("", encoding="utf-8")
        anchor_terms = load_anchor_terms(Path(anchor_terms_path))
    else:
        anchor_terms = []

    while queue:
        query = queue.popleft()
        if expand:
            with queries_all_path.open("a", encoding="utf-8") as handle:
                handle.write(query + "\n")

        batch_texts: list[str] = []
        for engine in engine_list:
            try:
                if engine == "searxng":
                    results = searxng.fetch(
                        query,
                        base_url=os.getenv("SEARX_URL", config.search.searx_url),
                        timeout_s=config.search.timeout_s,
                        user_agent=config.search.user_agent,
                    )
                elif engine == "brave":
                    results = brave.fetch(
                        query,
                        timeout_s=config.search.timeout_s,
                        user_agent=config.search.user_agent,
                    )
                elif engine == "ddg":
                    results = ddg.fetch(query)
                else:
                    click.echo(f"Unknown engine: {engine}")
                    continue
            except (brave.BraveDisabledError, ddg.DdgUnavailableError) as exc:
                click.echo(f"Engine {engine} unavailable: {exc}")
                continue
            except Exception as exc:
                click.echo(f"Engine {engine} error: {exc}")
                continue

            timestamp = utc_now()
            payloads = []
            for result in results:
                batch_texts.append(f"{result.get('title', '')} {result.get('snippet', '')}")
                payloads.append(
                    {
                        "query": query,
                        "engine": engine,
                        "rank": result["rank"],
                        "url": result["url"],
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "timestamp": timestamp,
                        "raw_metadata": result.get("raw_metadata", {}),
                    }
                )
            append_jsonl(Path(out_path), payloads)

        if expand and batch_texts:
            followups = extract_phrases(batch_texts, anchor_terms, config.expansion.max_followups)
            for phrase in followups:
                if phrase in seen_queries:
                    continue
                if len(queue) >= config.expansion.max_queue_size:
                    break
                queue.append(phrase)
                seen_queries.add(phrase)
                with queries_all_path.open("a", encoding="utf-8") as handle:
                    handle.write(phrase + "\n")


@main.command()
@click.option("--in", "input_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--outdir", "out_dir", type=click.Path(file_okay=False), required=True)
@click.option("--keywords", "keywords_path", type=click.Path(exists=True, dir_okay=False), default="config/keywords.txt")
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--domains", "domains_path", type=click.Path(exists=True, dir_okay=False), default=None)
def process(input_path: str, out_dir: str, keywords_path: str, config_path: str | None, domains_path: str | None) -> None:
    """Process raw JSONL into deduped outputs and clusters."""
    config = load_config(Path(config_path) if config_path else None)
    domains = load_domains(Path(domains_path) if domains_path else None)

    records: list[dict] = []
    with Path(input_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            records.append(json.loads(line))

    normalized = normalize_records(records)
    deduped = dedupe_records(normalized, threshold=config.dedupe.similarity_threshold)

    deduped_payloads: list[dict] = []
    for item in deduped:
        deduped_payloads.append(
            {
                "id": item.id,
                "canonical_url": item.canonical_url,
                "title": item.title,
                "snippet": item.snippet,
                "engines": item.engines,
                "best_rank": item.best_rank,
                "cluster_ids": [],
                "timestamp": item.timestamp,
            }
        )

    filtered = apply_domain_filters(deduped_payloads, domains)
    keywords = load_keywords(Path(keywords_path))
    clusters = build_clusters(filtered, keywords)
    terms = aggregate_terms(filtered)

    out_path = Path(out_dir)
    write_json(out_path / "deduped.json", filtered)
    write_json(out_path / "clusters.json", [ClusterSummary(**cluster.__dict__).model_dump() for cluster in clusters])
    write_json(out_path / "terms.json", TermsSummary(**terms).model_dump())


@main.command()
@click.option("--indir", "in_dir", type=click.Path(exists=True, file_okay=False), required=True)
@click.option("--outdir", "out_dir", type=click.Path(file_okay=False), required=True)
def reason(in_dir: str, out_dir: str) -> None:
    """Reasoning stub that writes placeholder outputs."""
    in_path = Path(in_dir)
    out_path = Path(out_dir)
    clusters = json.loads((in_path / "clusters.json").read_text(encoding="utf-8"))
    strategy = [
        StrategyItem(cluster_id=cluster["cluster_id"], recommendation="TODO: analyze with LLM", priority=0).model_dump()
        for cluster in clusters
    ]
    questions = [
        ResearchQuestion(
            question="TODO: generate with LLM",
            related_clusters=[cluster["cluster_id"]],
            status="pending",
        ).model_dump()
        for cluster in clusters
    ]

    out_path.mkdir(parents=True, exist_ok=True)
    write_json(out_path / "strategy.json", strategy)
    write_json(out_path / "research_questions.json", questions)


if __name__ == "__main__":
    main()
