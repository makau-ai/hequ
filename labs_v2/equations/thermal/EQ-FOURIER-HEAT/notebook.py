# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-FOURIER-HEAT — Fourier's Law of Heat Conduction (1D)
#
# $$q = -k \frac{dT}{dx}$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/thermal/EQ-FOURIER-HEAT/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — copper bar steady-state
#
# - **k = 401 W/(m·K)** for pure copper at 298 K — NIST SRD reference,
#   measured via guarded-hot-plate steady-state axial conduction rigs
#   calibrated against reference materials (ASTM C177, ±3%).
# - **Imposed gradient**: 373 K at x=0, 273 K at x=1 m → `dT/dx = -100 K/m`.
# - **Prediction**: `q = -k · dT/dx = 40,100 W/m²`.
#
# An independent calorimetric flux measurement (electric power into
# the hot reservoir = steady loss through the bar) would find q within
# ~±1,200 W/m² (from the ±3% k uncertainty). The consistency check
# below uses the predicted value.

# %%
k = 401.0 * ureg.watt / (ureg.meter * ureg.kelvin)
dT_dx = -100.0 * ureg.kelvin / ureg.meter
q_predicted = (-k * dT_dx).to(ureg.watt / ureg.meter**2)
print(f"k = {k}")
print(f"dT/dx = {dT_dx}")
print(f"q_predicted = {q_predicted}")

residual = eq.evaluate_with_units({"q": q_predicted, "k": k, "dT_dx": dT_dx})
print(f"residual q + k·(dT/dx) = {residual:+.3e}")
assert abs(residual) < 1e-6

# %% [markdown]
# ## Negative example — silicon nanowire ballistic regime
#
# Fourier fails when the wire length is shorter than the phonon mean
# free path (~40 nm in bulk Si at 300 K). Liu & Asheghi (JAP 98,
# 123523, 2005) measured `k_nano ≈ 25 W/(m·K)` for 22-nm Si wires,
# 6× below bulk. Using bulk k with a nanowire gradient predicts the
# wrong flux.

# %%
k_bulk = 148.0 * ureg.watt / (ureg.meter * ureg.kelvin)
k_nano = 25.0 * ureg.watt / (ureg.meter * ureg.kelvin)
dT_dx_nano = -1.0e8 * ureg.kelvin / ureg.meter
q_true = (-k_nano * dT_dx_nano).to(ureg.watt / ureg.meter**2)
bad_residual = eq.evaluate_with_units({
    "q": q_true, "k": k_bulk, "dT_dx": dT_dx_nano,
})
print(f"True nanowire flux: {q_true}")
print(f"residual with bulk k: {bad_residual:+.3e}  (large nonzero expected)")
assert abs(bad_residual) > 1e9
print("✓ Framework correctly exposes the ballistic (non-Fourier) regime.")

print(f"\n{eq.id} lab complete.")
