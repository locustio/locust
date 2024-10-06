from urllib.parse import urlparse


def is_url(url: str) -> bool:
    """
    Check if path is an url
    """
    try:
        result = urlparse(url)
        if result.scheme == "https" or result.scheme == "http":
            return True
        else:
            return False
    except ValueError:
        return False


def normalize_base_url(url: str) -> str:
    """Normalize the base URL to ensure consistent format."""
    if not url:
        return "/"
    url = url.strip("/")
    return f"/{url}" if url else "/"
