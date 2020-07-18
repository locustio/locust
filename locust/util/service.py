from urllib.parse import urlparse


def get_service_name(host):
    service_name = ""
    if host:
        service_name = '{uri.netloc}'.format(uri=urlparse(host))
    return service_name
