from urllib.parse import urlparse


def robots_checker(url: str) -> bool:
    """
    Check whether scraping is allowed for a URL.
    For now, this is a permissive stub.
    """
    parsed = urlparse(url)

    # Future: fetch and parse robots.txt here
    # Currently allow all
    return True
