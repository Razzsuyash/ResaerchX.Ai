from urllib.parse import urlparse


HIGH_TRUST_DOMAINS = {
    "who.int",
    "worldbank.org",
    "imf.org",
    "oecd.org",
    "nature.com",
    "sciencedirect.com",
    "ieee.org",
}

MAJOR_NEWS_DOMAINS = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "nytimes.com",
    "theguardian.com",
}


def assess_source(url: str) -> tuple[str, float]:
    """
    Heuristic source-quality signal, not a factual truth score.
    It is used to help rank/display sources and should never be
    treated as a guarantee that a source is correct.
    """
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        host = ""

    host = host.removeprefix("www.")

    if host.endswith(".gov") or host.endswith(".gov.in"):
        return "Government", 0.95

    if host.endswith(".edu") or host.endswith(".ac.in"):
        return "Academic", 0.95

    if host in HIGH_TRUST_DOMAINS or any(
        host.endswith("." + domain) for domain in HIGH_TRUST_DOMAINS
    ):
        return "Research / Institution", 0.90

    if host in MAJOR_NEWS_DOMAINS or any(
        host.endswith("." + domain) for domain in MAJOR_NEWS_DOMAINS
    ):
        return "Major News", 0.85

    if host:
        return "Web Source", 0.55

    return "Unknown", 0.30
