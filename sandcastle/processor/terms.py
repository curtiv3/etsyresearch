from __future__ import annotations

from collections import Counter

from sandcastle.processor.text import bigrams, tokenize_text


def aggregate_terms(items: list[dict], limit: int = 20) -> dict:
    term_counter = Counter()
    bigram_counter = Counter()

    for item in items:
        text = f"{item['title']} {item['snippet']}"
        tokens = tokenize_text(text)
        term_counter.update(tokens)
        bigram_counter.update(bigrams(tokens))

    def _top(counter: Counter) -> list[list]:
        items_sorted = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        return [[term, count] for term, count in items_sorted[:limit]]

    return {
        "global_top_terms": _top(term_counter),
        "global_top_bigrams": _top(bigram_counter),
    }
