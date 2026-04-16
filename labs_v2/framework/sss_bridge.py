"""hequ.ai ↔ SavvySuperSaver data API bridge.

Reads structured datasets (CVE severity, economic indicators,
grocery prices, legislative text, etc.) for equation verification
against non-sensor data. SSS provides raw data; hequ.ai decides
which equations apply.

Auth: X-Hequ-Key header or ?api_key= query param.
Base: https://sss-api-281207837690.us-central1.run.app/api/hequ

Environment variables:
  SSS_API_BASE — defaults to the URL above
  SSS_API_KEY  — the X-Hequ-Key value
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class SSSBridgeError(Exception):
    pass


@dataclass
class Dataset:
    id: str
    name: str
    description: str
    rows: int
    schema: Dict[str, str]


class SSSBridge:
    """Client for the SavvySuperSaver hequ data API."""

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.api_base = (
            api_base or os.environ.get(
                "SSS_API_BASE",
                "https://sss-api-281207837690.us-central1.run.app/api/hequ"
            )
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("SSS_API_KEY", "")
        if not self.api_key:
            raise SSSBridgeError(
                "SSS_API_KEY environment variable not set."
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Hequ-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.api_base}{path}"
        p = params or {}
        p["api_key"] = self.api_key
        qs = "&".join(f"{k}={v}" for k, v in p.items())
        url = f"{url}?{qs}" if qs else url
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise SSSBridgeError(
                f"GET {path} failed: {exc.code} {exc.reason}"
            ) from exc

    def _post(self, path: str, body: Any) -> Any:
        url = f"{self.api_base}{path}?api_key={self.api_key}"
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers=self._headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise SSSBridgeError(
                f"POST {path} failed: {exc.code} {exc.reason}"
            ) from exc

    def list_datasets(self) -> List[Dataset]:
        data = self._get("/datasets")
        return [
            Dataset(
                id=d["id"],
                name=d.get("name", ""),
                description=d.get("description", ""),
                rows=d.get("rows", 0),
                schema=d.get("schema", {}),
            )
            for d in data.get("datasets", [])
        ]

    def query(
        self,
        dataset_id: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        params = {"limit": str(limit), "offset": str(offset)}
        if filters:
            for k, v in filters.items():
                params[k] = str(v)
        data = self._get(f"/datasets/{dataset_id}", params=params)
        return data.get("rows", data.get("data", []))

    def aggregate(
        self,
        dataset_id: str,
        group_by: Optional[str] = None,
        agg: str = "count",
    ) -> List[Dict[str, Any]]:
        params = {"agg": agg}
        if group_by:
            params["group_by"] = group_by
        data = self._get(f"/datasets/{dataset_id}/aggregate", params=params)
        return data.get("rows", data.get("data", []))
