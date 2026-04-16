"""Run a live equation verification against makau.ai sensors.

Reads sensor_bindings.yaml, picks experiments with live sensor IDs
(not null or m5-* prefixed), calls makau.ai's /api/hequ/ endpoints,
computes predictions, and records results to the discovery ledger.

This is the first time hequ.ai closes the loop from equation
prediction to real measured data.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/run_live_verification.py

Requires: MAKAU_API_BASE environment variable (defaults to https://makau.ai)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.makau_bridge import MakauBridge, MakauBridgeError

BINDINGS_PATH = _LABS_V2 / "framework" / "sensor_bindings.yaml"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


def load_experiments():
    with BINDINGS_PATH.open() as f:
        doc = yaml.safe_load(f)
    return doc.get("experiments") or []


def is_live_experiment(exp: dict) -> bool:
    """An experiment is live if all its sensor bindings have
    non-null, non-local sensor IDs (i.e., not m5-* prefixed)."""
    bindings = exp.get("bindings", {})
    for var_name, binding in bindings.items():
        sid = binding.get("sensor_id")
        if not sid or sid.startswith("m5-") or sid == "null":
            return False
    return True


def run_experiment(bridge: MakauBridge, exp: dict) -> dict:
    """Run one live experiment and return the result dict."""
    exp_id = exp.get("id", "unknown")
    eq_id = exp.get("equation_id", "unknown")
    formula = exp.get("formula", "")
    tolerance = exp.get("tolerance", 0.05)
    bindings = exp.get("bindings", {})
    constants = exp.get("constants", {})

    print(f"\n{'='*60}")
    print(f"Experiment: {exp_id}")
    print(f"Equation:   {eq_id}")
    print(f"Formula:    {formula}")
    print(f"{'='*60}")

    # Step 1: Read live sensor values
    sensor_values = {}
    for var_name, binding in bindings.items():
        sid = binding["sensor_id"]
        transform = binding.get("transform", "value")
        try:
            reading = bridge.sensor_latest(sid)
            sensor_values[var_name] = reading.value
            print(f"  {var_name} = {reading.value} "
                  f"(from {sid}, key={transform}, "
                  f"at {reading.timestamp})")
        except MakauBridgeError as exc:
            print(f"  {var_name}: SENSOR READ FAILED ({exc})")
            return {
                "experiment_id": exp_id,
                "status": "sensor_error",
                "error": str(exc),
            }

    # Step 2: Compute prediction from formula
    import sympy as sp
    all_vars = {**sensor_values, **constants}
    sym_locals = {n: sp.Symbol(n, positive=True) for n in all_vars}
    try:
        expr = sp.sympify(formula, locals=sym_locals)
        predicted = float(expr.subs(
            {sym_locals[k]: v for k, v in all_vars.items()}
        ).evalf())
        print(f"\n  Predicted {exp.get('predicted_variable', '?')} "
              f"= {predicted:.6g} {exp.get('predicted_unit', '')}")
    except Exception as exc:
        print(f"  FORMULA EVAL FAILED: {exc}")
        return {
            "experiment_id": exp_id,
            "status": "formula_error",
            "error": str(exc),
        }

    # Step 3: Build result
    result = {
        "experiment_id": exp_id,
        "equation_id": eq_id,
        "formula": formula,
        "sensor_values": sensor_values,
        "constants": constants,
        "predicted_value": predicted,
        "predicted_variable": exp.get("predicted_variable", ""),
        "predicted_unit": exp.get("predicted_unit", ""),
        "tolerance": tolerance,
        "status": "completed",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    print(f"\n  Status: COMPLETED")
    print(f"  Sensor values: {sensor_values}")
    print(f"  Constants:     {constants}")
    print(f"  Prediction:    {predicted:.6g}")

    return result


def record_to_ledger(result: dict) -> None:
    """Append a live_sensor_verification record to the ledger."""
    record = {
        "timestamp_utc": result.get("timestamp_utc",
                         datetime.now(timezone.utc).isoformat()),
        "kind": "live_sensor_verification",
        **result,
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"  Ledger record written: kind=live_sensor_verification")


def main() -> int:
    experiments = load_experiments()
    live_exps = [e for e in experiments if is_live_experiment(e)]

    print(f"Total experiments in bindings: {len(experiments)}")
    print(f"Live experiments (real sensors): {len(live_exps)}")

    if not live_exps:
        print("\nNo live experiments found. All sensor IDs are null "
              "or local (m5-*). Connect sensors and update "
              "sensor_bindings.yaml.")
        return 0

    bridge = MakauBridge()
    results = []

    for exp in live_exps:
        try:
            result = run_experiment(bridge, exp)
            results.append(result)
            record_to_ledger(result)
        except Exception as exc:
            print(f"  EXPERIMENT FAILED: {exc}")
            results.append({
                "experiment_id": exp.get("id", "?"),
                "status": "error",
                "error": str(exc),
            })

    # Summary
    print(f"\n{'='*60}")
    print(f"LIVE VERIFICATION SUMMARY")
    print(f"{'='*60}")
    completed = sum(1 for r in results if r.get("status") == "completed")
    errors = sum(1 for r in results if r.get("status") != "completed")
    print(f"  Completed: {completed}")
    print(f"  Errors:    {errors}")
    for r in results:
        status = r.get("status", "?")
        eid = r.get("experiment_id", "?")
        if status == "completed":
            pred = r.get("predicted_value", 0)
            unit = r.get("predicted_unit", "")
            print(f"  ✅ {eid}: {pred:.6g} {unit}")
        else:
            err = r.get("error", "unknown")
            print(f"  ❌ {eid}: {status} — {err[:80]}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
