"""hequ.ai ↔ makau.ai bridge client.

Talks to makau.ai's /api/hequ/* endpoints to:
  1. Discover and read live sensor data
  2. Submit equation predictions for verification against
     measured values
  3. Execute Jupyter notebooks against live data and retrieve
     cell outputs
  4. Sync verification records back to hequ.ai's ledger

Auth: X-Makau-Tenant + X-Makau-User headers (dev mode) or
Firebase tokens (production). Configured via environment
variables MAKAU_API_BASE, MAKAU_TENANT, MAKAU_USER.

Usage:
    from framework.makau_bridge import MakauBridge

    bridge = MakauBridge()
    sensors = bridge.list_sensors()
    latest = bridge.sensor_latest("temp-01")
    result = bridge.verify(
        equation_id="fourier-heat",
        bindings=[{"sensor_id": "temp-01", "variable_name": "T_hot"}],
        predicted_values={"T_hot": 95.0},
    )
    nb_result = bridge.execute_notebook(notebook_json)
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorReading:
    sensor_id: str
    value: float
    unit: str
    timestamp: str
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class VerificationResult:
    equation_id: str
    measured_values: Dict[str, float]
    predicted_values: Dict[str, float]
    residuals: Dict[str, float]
    pass_fail: Dict[str, bool]
    timestamp: str = ""
    all_passed: bool = False


@dataclass
class NotebookResult:
    success: bool
    cell_outputs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class MakauBridgeError(Exception):
    """Raised when the makau.ai bridge returns an error."""


class MakauBridge:
    """Client for the makau.ai hequ bridge API."""

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        user: Optional[str] = None,
    ):
        self.api_base = (
            api_base
            or os.environ.get("MAKAU_API_BASE", "https://makau.ai")
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("MAKAU_API_KEY", "")
        self.user = user or os.environ.get("MAKAU_USER", "hequ-bridge")
        if not self.api_key:
            raise MakauBridgeError(
                "MAKAU_API_KEY environment variable not set. "
                "Set it to the X-Makau-Api-Key value before running."
            )

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Makau-Api-Key": self.api_key,
            "X-Makau-User": self.user,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.api_base}{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{qs}"
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise MakauBridgeError(
                f"GET {path} failed: {exc.code} {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MakauBridgeError(
                f"GET {path} connection failed: {exc}"
            ) from exc

    def _post(self, path: str, body: Any) -> Any:
        url = f"{self.api_base}{path}"
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers=self._headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise MakauBridgeError(
                f"POST {path} failed: {exc.code} {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MakauBridgeError(
                f"POST {path} connection failed: {exc}"
            ) from exc

    # ----- Sensor discovery and reading -----

    def list_sensors(self) -> List[Dict[str, Any]]:
        """GET /api/hequ/sensors — discover all sensors."""
        return self._get("/api/hequ/sensors")

    def sensor_latest(self, sensor_id: str) -> SensorReading:
        """GET /api/hequ/sensors/{id}/latest — current value."""
        data = self._get(f"/api/hequ/sensors/{sensor_id}/latest")
        return SensorReading(
            sensor_id=sensor_id,
            value=float(data.get("value", 0)),
            unit=data.get("unit", ""),
            timestamp=data.get("timestamp", ""),
            lat=data.get("lat"),
            lon=data.get("lon"),
        )

    def sensor_history(
        self, sensor_id: str, since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """GET /api/hequ/sensors/{id}/history — time series."""
        params = {}
        if since:
            params["since"] = since
        return self._get(
            f"/api/hequ/sensors/{sensor_id}/history", params=params
        )

    def sensor_batch(
        self, bindings: List[Dict[str, str]]
    ) -> Dict[str, float]:
        """POST /api/hequ/sensors/batch — hydrate all equation
        variables in one round-trip.

        bindings: [{"sensor_id": "temp-01", "variable_name": "T_hot"}, ...]
        Returns: {"T_hot": 97.2, ...}
        """
        data = self._post("/api/hequ/sensors/batch", bindings)
        return {
            item["variable_name"]: float(item["value"])
            for item in data
        }

    # ----- Equation verification -----

    def verify(
        self,
        equation_id: str,
        bindings: List[Dict[str, str]],
        predicted_values: Dict[str, float],
        tolerance: float = 0.05,
    ) -> VerificationResult:
        """POST /api/hequ/verify — the core verification endpoint.

        Sends equation bindings + predicted values to makau.ai,
        which reads the live sensor values, computes residuals,
        and returns pass/fail per variable.
        """
        body = {
            "equation_id": equation_id,
            "bindings": bindings,
            "predicted_values": predicted_values,
            "tolerance": tolerance,
        }
        data = self._post("/api/hequ/verify", body)
        return VerificationResult(
            equation_id=equation_id,
            measured_values=data.get("measured_values", {}),
            predicted_values=predicted_values,
            residuals=data.get("residuals", {}),
            pass_fail=data.get("pass_fail", {}),
            timestamp=data.get("timestamp", ""),
            all_passed=all(data.get("pass_fail", {}).values()),
        )

    # ----- Notebook execution -----

    def execute_notebook(
        self, notebook_json: Dict[str, Any]
    ) -> NotebookResult:
        """POST /api/hequ/execute-notebook — send a full Jupyter
        notebook and get back cell outputs.

        This is the power path: hequ.ai generates an entire
        notebook (imports, sensor reads, equation evaluation,
        residual computation, plots) and makau.ai executes it
        against live data.
        """
        data = self._post(
            "/api/hequ/execute-notebook", {"notebook": notebook_json}
        )
        return NotebookResult(
            success=data.get("success", False),
            cell_outputs=data.get("cell_outputs", []),
            error=data.get("error"),
        )

    # ----- Verification ledger sync -----

    def list_verifications(
        self, since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """GET /api/hequ/verifications — list past verification
        records from the makau.ai side."""
        params = {}
        if since:
            params["since"] = since
        return self._get("/api/hequ/verifications", params=params)
