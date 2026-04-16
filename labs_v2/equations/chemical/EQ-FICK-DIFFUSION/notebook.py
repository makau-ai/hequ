# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-FICK-DIFFUSION — Fick's First Law (1D)
#
# $$J = -D \frac{dC}{dx}$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/chemical/EQ-FICK-DIFFUSION/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — sucrose through a dialysis membrane
#
# - **D = 5.23 × 10⁻¹⁰ m²/s** for sucrose in water at 25 °C —
#   Gladden & Dole, J. Am. Chem. Soc. 75, 3900 (1953); CRC Handbook
#   (97th ed.). Measured via tracer-diffusion.
# - **Donor**: 0.100 M = 100 mol/m³; **acceptor**: 0 mol/m³ (sink).
# - **Membrane thickness**: 1.00 mm.
# - **Prediction**: `J = -D · dC/dx = +5.23 × 10⁻⁵ mol/(m²·s)`.

# %%
D = 5.23e-10 * ureg.meter**2 / ureg.second
C_d = 100.0 * ureg.mole / ureg.meter**3
C_a = 0.0 * ureg.mole / ureg.meter**3
ell = 1.0e-3 * ureg.meter
dC_dx = ((C_a - C_d) / ell).to(ureg.mole / ureg.meter**4)
J_predicted = (-D * dC_dx).to(ureg.mole / (ureg.meter**2 * ureg.second))
print(f"D = {D}")
print(f"dC/dx = {dC_dx}")
print(f"J_predicted = {J_predicted}")

residual = eq.evaluate_with_units({"J": J_predicted, "D": D, "dC_dx": dC_dx})
print(f"residual J + D·(dC/dx) = {residual:+.3e}")
assert abs(residual) < 1e-20

# %% [markdown]
# ## Negative example — concentrated regime
#
# At 1.0 M sucrose the measured D drops to 3.6 × 10⁻¹⁰ m²/s (Ribeiro
# et al., J. Chem. Eng. Data 51, 1836, 2006). Using the dilute D with
# the concentrated gradient gives the wrong flux.

# %%
C_d_conc = 1000.0 * ureg.mole / ureg.meter**3
dC_dx_conc = ((0.0 * ureg.mole / ureg.meter**3 - C_d_conc) / ell).to(ureg.mole / ureg.meter**4)
D_measured = 3.6e-10 * ureg.meter**2 / ureg.second
J_true = (-D_measured * dC_dx_conc).to(ureg.mole / (ureg.meter**2 * ureg.second))
bad_residual = eq.evaluate_with_units({"J": J_true, "D": D, "dC_dx": dC_dx_conc})
print(f"Actual flux at 1.0 M: {J_true}")
print(f"residual with dilute D: {bad_residual:+.3e}")
assert abs(bad_residual) > 1e-5
print("✓ Framework correctly exposes the non-dilute regime.")

print(f"\n{eq.id} lab complete.")
