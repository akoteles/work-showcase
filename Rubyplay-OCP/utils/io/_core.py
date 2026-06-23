import os
from urllib.parse import urlparse


def parse_url(url: str) -> str:
    parse_result = urlparse(url)

    proto = parse_result.scheme
    netloc = parse_result.netloc
    path = parse_result.path

    if proto == '':
        proto = 'file'
    elif proto == 'file':
        path = os.path.join(netloc, path)

    return proto, netloc, path
