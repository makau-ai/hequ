# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-ARRHENIUS — Arrhenius Rate Law
#
# $$k = A \exp\!\left(-\frac{E_a}{R T}\right)$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/chemical_kinetics/EQ-ARRHENIUS/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — extrapolation from independent measurements
#
# The honest way to test Arrhenius is: **fit A and E_a from rate
# constants measured at two temperatures, then predict a rate constant
# at a third temperature and compare to a separately-measured value**.
#
# Published rate constants for the acid-catalysed hydrolysis of
# methyl acetate (1 M HCl, data from Moelwyn-Hughes, *The Chemical
# Statics and Kinetics of Solutions*, Academic Press 1971, and
# collated in Atkins *Physical Chemistry* 11th ed., §19.7):
#
# | T (°C) | k (s⁻¹) (measured)     |
# |--------|------------------------|
# | 15     | 1.09 × 10⁻⁵            |
# | 25     | 3.11 × 10⁻⁵  (test)    |
# | 35     | 8.55 × 10⁻⁵            |
#
# We fit A and E_a from the 15 °C and 35 °C points, then **predict**
# k at 25 °C and compare to the measured value. If Arrhenius holds
# within the experimental uncertainty (~5%), the residual is small.

# %%
import math

R = 8.314462618 * ureg.joule / (ureg.mole * ureg.kelvin)
T1 = (15.0 + 273.15) * ureg.kelvin
T3 = (35.0 + 273.15) * ureg.kelvin
k1 = 1.09e-5 / ureg.second
k3 = 8.55e-5 / ureg.second

# Fit: ln k = ln A - Ea/(RT). Two unknowns, two points.
ln_k1 = math.log(k1.magnitude)
ln_k3 = math.log(k3.magnitude)
invT1 = 1.0 / T1.magnitude
invT3 = 1.0 / T3.magnitude
# slope = -Ea/R
slope = (ln_k3 - ln_k1) / (invT3 - invT1)
Ea_fitted = (-slope * R.magnitude) * ureg.joule / ureg.mole
A_fitted = math.exp(ln_k1 - slope * invT1) / ureg.second
print(f"Fitted Ea = {Ea_fitted.to(ureg.kilojoule / ureg.mole):.3f}")
print(f"Fitted A  = {A_fitted:.3e}")

# Predict at the intermediate temperature T2 = 25 °C:
T2 = (25.0 + 273.15) * ureg.kelvin
k2_predicted = A_fitted * math.exp((-Ea_fitted / (R * T2)).magnitude)
print(f"Predicted k at 25 °C: {k2_predicted:.3e}")

# Compare to the independently-measured value:
k2_measured = 3.11e-5 / ureg.second
rel_err = abs((k2_predicted.magnitude - k2_measured.magnitude) / k2_measured.magnitude)
print(f"Measured k at 25 °C:  {k2_measured}")
print(f"Relative error: {rel_err*100:.2f}%")

# Feed the predicted k (from the fit) into the canonical form with
# the fitted parameters — consistency check, should be zero.
residual = eq.evaluate_with_units({
    "k_rate": k2_predicted,
    "A": A_fitted,
    "Ea": Ea_fitted,
    "R": R,
    "T": T2,
})
print(f"residual (fitted prediction self-check): {residual:+.3e}")
assert abs(residual) < 1e-12

# The real falsification: compare the PREDICTION to the independent
# MEASUREMENT. Arrhenius passes if the relative error is small.
print(f"\nArrhenius extrapolation error: {rel_err*100:.2f}%  "
      f"({'PASS' if rel_err < 0.15 else 'FAIL'} at 15% threshold)")
assert rel_err < 0.15, "Arrhenius should extrapolate to 25 °C within 15%"

# %% [markdown]
# ## Negative example — low-T tunneling regime
#
# Arrhenius assumes temperature-independent A and E_a. At low T,
# quantum tunneling through the barrier makes the effective rate
# *much* higher than the classical Arrhenius prediction (Truhlar &
# Garrett, Annu. Rev. Phys. Chem. 35, 159 (1984); canonical example:
# the H + H₂ → H₂ + H reaction below 200 K).
#
# If we fit at T = 288-308 K and extrapolate to 150 K, the classical
# Arrhenius prediction is orders of magnitude below the real rate.

# %%
T_cold = 150.0 * ureg.kelvin
k_classical = A_fitted * math.exp((-Ea_fitted / (R * T_cold)).magnitude)
# "Measured" k with tunneling enhancement: 1000× classical
k_tunneling = k_classical * 1000.0
print(f"Classical Arrhenius k at 150 K: {k_classical:.3e}")
print(f"Measured k (with tunneling):    {k_tunneling:.3e}")

bad_residual = eq.evaluate_with_units({
    "k_rate": k_tunneling,
    "A": A_fitted,
    "Ea": Ea_fitted,
    "R": R,
    "T": T_cold,
})
# evaluate_with_units returns a plain float — no .magnitude.
print(f"residual: {bad_residual:+.3e}  (should be ≈ k_tunneling value)")
assert abs(bad_residual) > 0.1 * abs(k_tunneling.magnitude)
print("✓ Framework correctly exposes non-Arrhenius (tunneling) regime.")

print(f"\n{eq.id} lab complete.")
