"""Cloud Function: hequ.ai live equation verification.

Deployed on GCP (hequ-ai project) to call makau.ai's /api/hequ/*
endpoints from within GCP networking. Reads live sensor data,
computes equation predictions, returns verification results.

Triggered via HTTP. Can be called manually, on a schedule (Cloud
Scheduler), or from the hequ.ai website.

Environment variables (set at deploy time):
  MAKAU_API_KEY — the X-Makau-Api-Key value
  MAKAU_USER    — defaults to "hequ-bridge"
"""

import json
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone

import functions_framework

MAKAU_BASE = "https://makau.ai"
EXPERIMENTS = [
    {
        "id": "EXP-IDEAL-GAS-LIVE-001",
        "equation": "Ideal Gas Law: V_m = RT/P",
        "sensors": {
            "T": {"sensor_id": "nws-kiah", "transform": "temperature_c", "convert_K": True},
            "P": {"sensor_id": "nws-kiah", "transform": "pressure_pa"},
        },
        "constants": {"R": 8.314472},
        "formula": lambda v: v["R"] * v["T"] / v["P"],
        "predicted_var": "V_m",
        "unit": "m³/mol",
    },
    {
        "id": "EXP-CLAUSIUS-CLAPEYRON-LIVE-001",
        "equation": "Magnus formula: e_s = 6.112·exp(17.67·T/(T+243.5))",
        "sensors": {
            "T_c": {"sensor_id": "nws-kord", "transform": "temperature_c"},
        },
        "constants": {},
        "formula": lambda v: 6.112 * math.exp(17.67 * v["T_c"] / (v["T_c"] + 243.5)),
        "predicted_var": "e_s",
        "unit": "hPa",
    },
    {
        "id": "EXP-FOURIER-GRADIENT-LIVE-001",
        "equation": "Fourier heat flux: q = k·(T_hot−T_cold)/L (pipeline test)",
        "sensors": {
            "T_hot": {"sensor_id": "nws-kiah", "transform": "temperature_c", "convert_K": True},
            "T_cold": {"sensor_id": "nws-kden", "transform": "temperature_c", "convert_K": True},
        },
        "constants": {"k": 401.0, "L": 0.5},
        "formula": lambda v: v["k"] * (v["T_hot"] - v["T_cold"]) / v["L"],
        "predicted_var": "q",
        "unit": "W/m²",
    },
    {
        "id": "EXP-DARCY-RIVER-LIVE-001",
        "equation": "River discharge (read-only, no prediction)",
        "sensors": {
            "Q": {"sensor_id": "usgs-09380000", "transform": "discharge_cfs"},
        },
        "constants": {},
        "formula": lambda v: v["Q"],
        "predicted_var": "Q",
        "unit": "cfs",
    },
]


def _get_makau(path, api_key, user):
    url = f"{MAKAU_BASE}{path}"
    headers = {
        "X-Makau-Api-Key": api_key,
        "X-Makau-User": user,
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def read_sensor(sensor_id, transform, api_key, user):
    data = _get_makau(f"/api/hequ/sensors/{sensor_id}/latest", api_key, user)
    if isinstance(data, dict):
        return data.get(transform, data.get("value", 0))
    return 0


def run_experiment(exp, api_key, user):
    result = {
        "id": exp["id"],
        "equation": exp["equation"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_readings": {},
        "status": "unknown",
    }

    values = dict(exp["constants"])

    for var_name, binding in exp["sensors"].items():
        try:
            raw = read_sensor(binding["sensor_id"], binding["transform"], api_key, user)
            val = float(raw)
            if binding.get("convert_K"):
                val = val + 273.15
            values[var_name] = val
            result["sensor_readings"][var_name] = {
                "sensor_id": binding["sensor_id"],
                "raw_value": raw,
                "converted": val,
                "unit": "K" if binding.get("convert_K") else binding["transform"],
            }
        except Exception as exc:
            result["status"] = "sensor_error"
            result["error"] = f"{var_name}: {exc}"
            return result

    try:
        predicted = exp["formula"](values)
        result["predicted_value"] = predicted
        result["predicted_var"] = exp["predicted_var"]
        result["unit"] = exp["unit"]
        result["all_values"] = values
        result["status"] = "completed"
    except Exception as exc:
        result["status"] = "formula_error"
        result["error"] = str(exc)

    return result


@functions_framework.http
def live_verify(request):
    """HTTP Cloud Function entry point."""
    import os
    api_key = os.environ.get("MAKAU_API_KEY", "")
    user = os.environ.get("MAKAU_USER", "hequ-bridge")

    if not api_key:
        return json.dumps({"error": "MAKAU_API_KEY not set"}), 500

    results = []
    for exp in EXPERIMENTS:
        r = run_experiment(exp, api_key, user)
        results.append(r)

    completed = [r for r in results if r["status"] == "completed"]
    errors = [r for r in results if r["status"] != "completed"]

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_experiments": len(EXPERIMENTS),
        "completed": len(completed),
        "errors": len(errors),
        "results": results,
    }

    return json.dumps(summary, indent=2, default=str), 200, {
        "Content-Type": "application/json"
    }
