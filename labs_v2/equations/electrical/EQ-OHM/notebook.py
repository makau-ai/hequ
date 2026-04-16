# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-OHM — Ohm's Law
#
# $$V = I R$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/electrical/EQ-OHM/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — measured R, source V, predicted I
#
# - **R = 220 Ω ±1%** — carbon-film resistor, 4-band colour code
#   red-red-brown-gold; tolerance from Vishay/Dale CCF series
#   datasheet. Independent of any V or I reading on *this* resistor.
# - **V = 2.000 V ±0.012%** — set on a Keithley 2400 Sourcemeter on
#   its 2 V source range (datasheet Table 4-1).
# - **Prediction**: I = V/R = 9.091 mA from Ohm's law.
#
# A real lab measurement via the Keithley's current-sense input
# (10 mA range, ±0.035% + 500 nA accuracy) would find I within
# ±10 µA of the prediction. The consistency check below uses the
# predicted I value; a separately-acquired DMM reading would close
# the falsification loop.

# %%
R = 220.0 * ureg.ohm
V = 2.000 * ureg.volt
I_predicted = (V / R).to(ureg.ampere)
print(f"R = {R}, V = {V}")
print(f"I_predicted = V/R = {I_predicted}")

residual = eq.evaluate_with_units({"V": V, "I": I_predicted, "R": R})
print(f"residual V − I·R = {residual:+.3e}")
assert abs(residual) < 1e-9

# %% [markdown]
# ## Negative example — silicon diode
#
# Shockley equation `I = I_s(e^{qV/kT} − 1)` is exponential, not
# linear. Fitting R from one diode point and testing at another
# produces a large residual.

# %%
import math
I_s = 1e-12
V_T = 0.02585

V1 = 0.70 * ureg.volt
I1 = I_s * (math.exp(V1.magnitude / V_T) - 1) * ureg.ampere
R_bad = (V1 / I1).to(ureg.ohm)
print(f"Diode point 1: V={V1}, I={I1:.3e}, R_bad={R_bad:.3e}")

V2 = 0.50 * ureg.volt
I2 = I_s * (math.exp(V2.magnitude / V_T) - 1) * ureg.ampere
bad_residual = eq.evaluate_with_units({"V": V2, "I": I2, "R": R_bad})
print(f"Diode point 2: V={V2}, I={I2:.3e}")
print(f"residual V − I·R_bad: {bad_residual:+.3e}")
assert abs(bad_residual) > 0.01
print("✓ Framework correctly exposes the diode as non-ohmic.")

print(f"\n{eq.id} lab complete.")
