"""HTTP client for the Paperclip AI orchestration server."""
import json
from pathlib import Path
from typing import Any

import requests

CONFIG_PATH = Path.home() / ".config" / "paperclip-cli" / "config.json"
DEFAULT_URL = "http://localhost:3100"


class PaperclipError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class PaperclipClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        config = self._load_config()
        self.base_url = (base_url or config.get("base_url", DEFAULT_URL)).rstrip("/")
        self.token = token or config.get("token", "")

    def _load_config(self) -> dict:
        if CONFIG_PATH.exists():
            try:
                return json.loads(CONFIG_PATH.read_text())
            except Exception:
                return {}
        return {}

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _raise_for_status(self, resp: requests.Response) -> None:
        if not resp.ok:
            try:
                msg = resp.json().get("error", resp.text)
            except Exception:
                msg = resp.text
            raise PaperclipError(resp.status_code, msg)

    def get(self, path: str, **kwargs) -> Any:
        resp = requests.get(f"{self.base_url}/api{path}", headers=self._headers(), **kwargs)
        self._raise_for_status(resp)
        return resp.json()

    def post(self, path: str, data: dict | None = None, **kwargs) -> Any:
        resp = requests.post(f"{self.base_url}/api{path}", json=data, headers=self._headers(), **kwargs)
        self._raise_for_status(resp)
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def patch(self, path: str, data: dict | None = None, **kwargs) -> Any:
        resp = requests.patch(f"{self.base_url}/api{path}", json=data, headers=self._headers(), **kwargs)
        self._raise_for_status(resp)
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def delete(self, path: str, **kwargs) -> Any:
        resp = requests.delete(f"{self.base_url}/api{path}", headers=self._headers(), **kwargs)
        self._raise_for_status(resp)
        return {}

    def health(self) -> dict:
        resp = requests.get(f"{self.base_url}/api/health", headers=self._headers(), timeout=5)
        self._raise_for_status(resp)
        return resp.json()
