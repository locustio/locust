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
