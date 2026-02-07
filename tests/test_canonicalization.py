from sandcastle.processor.canonicalize import canonicalize_url


def test_https_normalization():
    assert canonicalize_url("http://Example.com/path") == "https://example.com/path"


def test_tracking_params_removed_and_sorted():
    url = "https://example.com/page?utm_source=aa&b=2&a=1&fbclid=123"
    assert canonicalize_url(url) == "https://example.com/page?a=1&b=2"


def test_fragment_removed():
    url = "https://example.com/page#section"
    assert canonicalize_url(url) == "https://example.com/page"


def test_trailing_slash_and_multi_slash():
    url = "https://example.com//path//to/"
    assert canonicalize_url(url) == "https://example.com/path/to"


def test_www_stripped():
    url = "https://www.example.com/path"
    assert canonicalize_url(url) == "https://example.com/path"
