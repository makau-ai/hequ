# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-LORENTZ-FACTOR — Lorentz Factor γ
#
# $$\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}$$
# Implicit form: $\gamma^2 (1 - v^2/c^2) - 1 = 0$.

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/relativity/EQ-LORENTZ-FACTOR/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — GPS satellite clock correction
#
# GPS satellites orbit at v ≈ 3874 m/s, which produces a measurable
# time dilation. The Lorentz factor at this speed is
# γ ≈ 1 + v²/(2c²) = 1 + 8.35×10⁻¹¹, consistent with published GPS
# relativistic correction budgets (Ashby, *Relativity in the Global
# Positioning System*, Living Rev. Relativity 6 (2003), §3).
#
# We plug in the measured orbital speed and the defined value of c
# (NIST: exactly 299 792 458 m/s) and check that the canonical form
# vanishes.

# %%
c_val = 299_792_458.0 * ureg.meter / ureg.second     # defined SI
v_val = 3874.0 * ureg.meter / ureg.second            # GPS orbital
import math
gamma_val = 1.0 / math.sqrt(1 - (v_val.magnitude / c_val.magnitude) ** 2)
print(f"v = {v_val}")
print(f"γ(v) = {gamma_val:.15f}")
print(f"γ - 1 = {gamma_val - 1:.3e}  (expect ~8.35e-11)")

# Wrap gamma as a dimensionless pint Quantity.
gamma_q = gamma_val * ureg.dimensionless
residual = eq.evaluate_with_units({
    "gamma": gamma_q, "v": v_val, "c": c_val,
})
print(f"residual = {residual:+.3e}")
assert abs(residual) < 1e-10

# %% [markdown]
# ## Negative example — γ = 1 at a non-zero velocity
#
# Claiming γ = 1 at a non-zero v is the Newtonian approximation —
# it agrees to leading order but breaks the exact Lorentz relation.
# The canonical form then has a residual of order (v/c)².

# %%
gamma_newton = 1.0 * ureg.dimensionless
bad_residual = eq.evaluate_with_units({
    "gamma": gamma_newton, "v": v_val, "c": c_val,
})
print(f"γ=1 (Newtonian) residual: {bad_residual:+.3e}")
# For v_gps ≈ 3874 m/s, (v/c)² ≈ 1.67e-10
assert abs(bad_residual) > 1e-11
print("✓ Framework correctly detects the deviation from exact Lorentz.")

print(f"\n{eq.id} lab complete.")
