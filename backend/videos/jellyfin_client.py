import hashlib
import hmac
import os
import time
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class JellyfinClient:
    def __init__(self, base_url: str, api_key: str, user_id: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update({
            'X-MediaBrowser-Token': self.api_key,
        })

    def refresh_library(self) -> None:
        # Trigger a library scan; optional, Jellyfin usually auto-scans
        try:
            self.session.post(f"{self.base_url}/Library/Refresh")
        except Exception:
            pass

    def list_items(self, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {
            'IncludeItemTypes': 'Movie,Video',
            'Fields': 'PrimaryImageAspectRatio,Path,Overview,Genres,RunTimeTicks',
            'SortBy': 'DateCreated,SortName',
            'SortOrder': 'Descending',
        }
        if parent_id:
            params['ParentId'] = parent_id
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get('Items', [])

    def get_item(self, item_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/Users/{self.user_id}/Items/{item_id}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_stream_url(self, item_id: str) -> str:
        # We will return the HLS stream path; clients will access via Django proxy
        # Example Jellyfin HLS endpoint: /Videos/{item_id}/master.m3u8?api_key=...
        return f"{self.base_url}/Videos/{item_id}/master.m3u8"


def build_signed_url(path: str, expires_in: int) -> str:
    expires = int(time.time()) + expires_in
    payload = f"{path}.{expires}"
    signature = hmac.new(
        key=settings.SIGNED_URL_SECRET.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"{path}?expires={expires}&sig={signature}"


def verify_signature(path: str, expires: int, sig: str) -> bool:
    if int(expires) < int(time.time()):
        return False
    payload = f"{path}.{expires}"
    expected = hmac.new(
        key=settings.SIGNED_URL_SECRET.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, sig)



