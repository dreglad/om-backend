import json
from urllib.parse import urljoin

import requests


def request_conversion(stream):
    """Request conversion through Wowza Streaming Engine API"""
    r = requests.get(urljoin(stream.api_url, '/dvrstores'))
    if r.status_code == requests.codes.ok:
        stores = json.loads(r.text)
        return stores
