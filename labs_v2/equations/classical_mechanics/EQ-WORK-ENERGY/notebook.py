# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-WORK-ENERGY — Work–Energy Theorem
#
# $$W = \tfrac{1}{2} m (v_f^2 - v_i^2)$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/classical_mechanics/EQ-WORK-ENERGY/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — marble on a frictionless ramp
#
# A 0.050 kg steel marble released from rest at the top of a
# frictionless 0.200 m ramp drop.
#
# - **Mass**: `m = 0.0500 kg` (Pasco ME-6825A kit spec).
# - **Standard gravity**: `g = 9.80665 m/s²` (NIST SP 811).
# - **Height drop**: `h = 0.200 m` (calibrated Pasco ramp scale).
#
# Two *independent* derivations from these three inputs:
# - Work by gravity (F·d for constant force): `W = m·g·h`
# - Final speed via energy conservation: `v_f = √(2 g h)`
#
# The work-energy theorem asserts that these two independently-derived
# values satisfy `W = ½ m (v_f² − v_i²)` — a genuine consistency check
# between two separate principles (force × displacement vs. energy
# conservation), not a self-consistent round-trip.

# %%
import math

m = 0.0500 * ureg.kilogram
g = 9.80665 * ureg.meter / ureg.second**2
h = 0.200 * ureg.meter
W = (m * g * h).to(ureg.joule)

v_f_mag = math.sqrt(2.0 * g.magnitude * h.magnitude)
v_f = v_f_mag * ureg.meter / ureg.second
v_i = 0.0 * ureg.meter / ureg.second

print(f"m={m}, g={g}, h={h}")
print(f"W = m·g·h = {W}")
print(f"v_f = √(2gh) = {v_f}")

residual = eq.evaluate_with_units({"W": W, "m": m, "v_i": v_i, "v_f": v_f})
print(f"residual W − ½m(v_f² − v_i²) = {residual:+.3e}")
assert abs(residual) < 1e-10

# %% [markdown]
# ## Negative example — variable-mass rocket
#
# For a rocket burning fuel, mass decreases and the fixed-mass
# work-energy theorem is invalid. 1000 kg → 600 kg rocket accelerating
# from 0 to 2000 m/s: the actual dry-mass KE is ~1.2 GJ, but the
# constant-mass formula with m_avg = 800 kg gives ~1.6 GJ. Plugging
# the actual W with the average m into the formula exposes the
# ~400 MJ discrepancy (energy carried off by propellant).

# %%
W_actual = 1.2e9 * ureg.joule
m_avg = 800.0 * ureg.kilogram
v_i_r = 0.0 * ureg.meter / ureg.second
v_f_r = 2000.0 * ureg.meter / ureg.second

bad_residual = eq.evaluate_with_units({
    "W": W_actual, "m": m_avg, "v_i": v_i_r, "v_f": v_f_r,
})
print(f"Rocket residual: {bad_residual:+.3e} J  (expect ~-400 MJ)")
assert abs(bad_residual) > 1e8
print("✓ Framework correctly exposes the constant-mass assumption violation.")

print(f"\n{eq.id} lab complete.")
