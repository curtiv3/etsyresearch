from sandcastle.processor.dedupe import dedupe_records, normalize_records


def sample_records():
    return [
        {
            "query": "test",
            "engine": "searxng",
            "rank": 2,
            "url": "https://example.com/page?utm_source=x",
            "title": "Anxiety Journal PDF",
            "snippet": "Printable anxiety prompts",
            "timestamp": "2026-02-06T10:30:00Z",
        },
        {
            "query": "test",
            "engine": "brave",
            "rank": 1,
            "url": "https://example.com/page",
            "title": "Anxiety Journal PDF",
            "snippet": "Printable anxiety prompts",
            "timestamp": "2026-02-06T10:31:00Z",
        },
        {
            "query": "test",
            "engine": "searxng",
            "rank": 3,
            "url": "https://example.com/other",
            "title": "Guided anxiety journal",
            "snippet": "Printable anxiety prompts",
            "timestamp": "2026-02-06T10:32:00Z",
        },
    ]


def test_exact_canonical_dedupe():
    normalized = normalize_records(sample_records())
    deduped = dedupe_records(normalized, threshold=0.85)
    assert len(deduped) == 2
    assert deduped[0].best_rank == 1
    assert "brave" in deduped[0].engines


def test_near_duplicate_dedupe():
    records = sample_records()
    records[2]["url"] = "https://different.com/page"
    normalized = normalize_records(records)
    deduped = dedupe_records(normalized, threshold=0.5)
    assert len(deduped) == 1


def test_near_duplicate_threshold_respected():
    normalized = normalize_records(sample_records())
    deduped = dedupe_records(normalized, threshold=0.95)
    assert len(deduped) == 2
