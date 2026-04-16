# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-BEER-LAMBERT — Beer–Lambert Law
#
# $$A = \varepsilon \ell c$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/spectroscopy/EQ-BEER-LAMBERT/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — NADH at 340 nm
#
# - **ε = 6220 M⁻¹cm⁻¹** — NADH at 340 nm, Horecker & Kornberg, J.
#   Biol. Chem. 175, 385 (1948). Primary source; used in clinical
#   enzymology to this day.
# - **ℓ = 1.00 cm** — standard quartz cuvette.
# - **A = 0.4500 ± 0.002** — Shimadzu UV-1800 spectrophotometer
#   reading.
#
# Inverse-form prediction: `c = A / (ε·ℓ) = 7.235 × 10⁻⁵ M`.
# An independent concentration measurement (mass of fresh NADH
# dissolved in known volume) would falsify.

# %%
eps_NADH = 6220.0 * ureg.liter / (ureg.mole * ureg.centimeter)
ell = 1.00 * ureg.centimeter
A_measured = 0.4500 * ureg.dimensionless
c_predicted = (A_measured / (eps_NADH * ell)).to(ureg.mole / ureg.liter)
print(f"A = {A_measured}, ε = {eps_NADH}")
print(f"c_predicted = {c_predicted}")

residual = eq.evaluate_with_units({
    "A": A_measured, "epsilon": eps_NADH, "ell": ell, "c": c_predicted,
})
print(f"residual = {residual:+.3e}")
assert abs(residual) < 1e-12

# %% [markdown]
# ## Negative example — saturated concentration
#
# Above ~10⁻² M, the linear relation breaks. A saturation model
# `A(c) = ε·ℓ·c / (1 + k_s c)` gives the correct nonlinear A; the
# linear formula then produces a nonzero residual.

# %%
c_high = 0.020 * ureg.mole / ureg.liter
k_sat = 30.0 / (ureg.mole / ureg.liter)
A_true = ((eps_NADH * ell * c_high) / (1 + k_sat * c_high)).to(ureg.dimensionless)
print(f"True A at 20 mM: {A_true:.3f}")
bad_residual = eq.evaluate_with_units({
    "A": A_true, "epsilon": eps_NADH, "ell": ell, "c": c_high,
})
print(f"residual with linear formula: {bad_residual:+.3f}")
assert abs(bad_residual) > 10.0
print("✓ Framework correctly exposes the saturation regime.")

print(f"\n{eq.id} lab complete.")
