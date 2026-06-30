from urllib.parse import urlparse


def is_url(url: str) -> bool:
    """
    Check if path is an url
    """
    try:
        result = urlparse(url)
        return result.scheme in ("https", "http") and bool(result.netloc)
    except ValueError:
        return False
