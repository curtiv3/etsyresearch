from sandcastle.processor.clustering import assign_clusters, build_clusters


def test_assign_clusters_multi_label():
    keywords = ["shadow work", "gratitude", "prompt journal"]
    text = "Shadow work prompt journal for gratitude"
    clusters = assign_clusters(text, keywords)
    assert "shadow_work" in clusters
    assert "gratitude" in clusters
    assert "prompt_journal" in clusters


def test_build_clusters_counts():
    items = [
        {"id": "a", "title": "Anxiety journal pdf", "snippet": "printable", "cluster_ids": []},
        {"id": "b", "title": "Mindfulness journal", "snippet": "pdf", "cluster_ids": []},
    ]
    keywords = ["anxiety", "mindfulness", "pdf"]
    clusters = build_clusters(items, keywords)
    ids = {cluster.cluster_id for cluster in clusters}
    assert ids == {"anxiety", "mindfulness", "pdf"}


def test_intent_counts():
    items = [
        {"id": "a", "title": "Printable worksheet", "snippet": "pdf", "cluster_ids": []},
    ]
    keywords = ["worksheet"]
    clusters = build_clusters(items, keywords)
    assert clusters[0].intent_counts["worksheet"] == 1
    assert clusters[0].intent_counts["pdf"] == 1
