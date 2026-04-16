# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-BLACK-SCHOLES — Black–Scholes PDE

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/finance/EQ-BLACK-SCHOLES/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical (algebraic): {eq.canonical_form}")
print(f"canonical (derivative): {eq.canonical_form_derivatives}")

# %% [markdown]
# ## Cross-validation — closed-form call satisfies the PDE
#
# The Merton (1973) closed-form solution for a European call —
# derived via the replicating-portfolio argument, a separate route
# from solving the PDE directly — must satisfy the PDE. Computing
# the Greeks from the closed form via `scipy.stats.norm` and
# substituting into the PDE yields an independent consistency check.

# %%
import numpy as np
from scipy.stats import norm

S = 100.0
K = 100.0
r_val = 0.05
sigma_val = 0.20
tau = 0.25

sqrt_tau = np.sqrt(tau)
d1 = (np.log(S / K) + (r_val + sigma_val**2 / 2) * tau) / (sigma_val * sqrt_tau)
d2 = d1 - sigma_val * sqrt_tau
Nd1 = norm.cdf(d1); Nd2 = norm.cdf(d2); nd1 = norm.pdf(d1)

V = S * Nd1 - K * np.exp(-r_val * tau) * Nd2
V_S = Nd1
V_SS = nd1 / (S * sigma_val * sqrt_tau)
V_t = -(S * nd1 * sigma_val) / (2 * sqrt_tau) - r_val * K * np.exp(-r_val * tau) * Nd2
print(f"Call V = ${V:.4f}, Δ={V_S:.4f}, Γ={V_SS:.6f}, Θ={V_t:.4f}")

residual = eq.evaluate_with_units({
    "V":     V    * ureg.dollar,
    "V_t":   V_t  * ureg.dollar / ureg.second,
    "V_S":   V_S  * ureg.dimensionless,
    "V_SS":  V_SS * (1.0 / ureg.dollar),
    "S":     S    * ureg.dollar,
    "sigma": sigma_val * (1.0 / ureg.second**0.5),
    "r":     r_val * (1.0 / ureg.second),
})
print(f"PDE residual at closed-form ATM call: {residual:+.3e}")
assert abs(residual) < 1e-8

# %% [markdown]
# ## Negative example — volatility smile
#
# Using ATM vol to price an OTM put while the true smile-aware vol
# is different → PDE residual nonzero.

# %%
sigma_atm = 0.20
sigma_otm = 0.32
K_otm = 80.0

d1_o = (np.log(S / K_otm) + (r_val + sigma_otm**2 / 2) * tau) / (sigma_otm * np.sqrt(tau))
d2_o = d1_o - sigma_otm * np.sqrt(tau)
Nd1_o = norm.cdf(d1_o); Nd2_o = norm.cdf(d2_o); nd1_o = norm.pdf(d1_o)
V_otm = S * Nd1_o - K_otm * np.exp(-r_val * tau) * Nd2_o
V_S_otm = Nd1_o
V_SS_otm = nd1_o / (S * sigma_otm * np.sqrt(tau))
V_t_otm = -(S * nd1_o * sigma_otm) / (2 * np.sqrt(tau)) - r_val * K_otm * np.exp(-r_val * tau) * Nd2_o

bad_residual = eq.evaluate_with_units({
    "V":    V_otm    * ureg.dollar,
    "V_t":  V_t_otm  * ureg.dollar / ureg.second,
    "V_S":  V_S_otm  * ureg.dimensionless,
    "V_SS": V_SS_otm * (1.0 / ureg.dollar),
    "S":    S        * ureg.dollar,
    "sigma": sigma_atm * (1.0 / ureg.second**0.5),
    "r":    r_val * (1.0 / ureg.second),
})
print(f"PDE residual with wrong σ: {bad_residual:+.4f}")
assert abs(bad_residual) > 1e-3
print("✓ Framework correctly exposes the volatility-smile violation.")

print(f"\n{eq.id} lab complete.")
