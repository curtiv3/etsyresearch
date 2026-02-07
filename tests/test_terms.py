from sandcastle.processor.terms import aggregate_terms


def test_term_extraction():
    items = [
        {"title": "Anxiety journal", "snippet": "Printable anxiety prompts"},
        {"title": "Gratitude journal", "snippet": "Printable pdf"},
    ]
    terms = aggregate_terms(items, limit=5)
    top_terms = dict(terms["global_top_terms"])
    assert top_terms["anxiety"] == 2
    assert "gratitude" in top_terms


def test_bigram_extraction():
    items = [
        {"title": "Anxiety journal", "snippet": "Printable anxiety prompts"},
    ]
    terms = aggregate_terms(items, limit=5)
    bigrams = dict(terms["global_top_bigrams"])
    assert "anxiety journal" in bigrams


def test_stopwords_filtered():
    items = [
        {"title": "The journal", "snippet": "A guide to the journal"},
    ]
    terms = aggregate_terms(items, limit=5)
    top_terms = {term for term, _ in terms["global_top_terms"]}
    assert "the" not in top_terms
    assert "a" not in top_terms
