# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-LOTKA-VOLTERRA — Predator-Prey Prey-Balance (Fixed Point)
#
# Prey balance condition at an interior fixed point:
# $$\alpha x - \beta x y = 0$$
# which solves to $y^* = \alpha / \beta$.

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/biology/EQ-LOTKA-VOLTERRA/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — Volterra's Adriatic fish data
#
# Volterra's original 1926 analysis used post-WWI Adriatic fishing
# data where the predator-prey oscillation is clearly visible.
# Reconstructed parameter estimates from secondary sources (Cushing
# 1996, "The Lotka-Volterra Predator-Prey Equations", in *Mathematical
# Biology*): α ≈ 0.1/yr, β ≈ 0.02/(yr·arbitrary-count-unit) for the
# observed Adriatic cycle of ~12 years.
#
# At the interior fixed point, the prey birth rate exactly balances
# the predation rate: y* = α/β = 5 (arbitrary units), and
# x* = γ/δ from the predator equation (not shown here).
#
# We check that the prey-balance canonical form vanishes at y = y*.

# %%
alpha = 0.10 / ureg.year
beta = 0.02 / (ureg.year * ureg.mole)   # using mole as generic count
y_star = (alpha / beta).to(ureg.mole)
x_val = 100.0 * ureg.mole                # any positive prey population
print(f"α = {alpha}")
print(f"β = {beta}")
print(f"Fixed-point predator density y* = α/β = {y_star}")

# At y = y*, the prey balance α*x - β*x*y* = α*x - α*x = 0.
residual = eq.evaluate_with_units({
    "alpha": alpha,
    "x": x_val,
    "beta": beta,
    "y": y_star,
})
print(f"residual at interior fixed point: {residual:+.3e}")
assert abs(residual) < 1e-10

# %% [markdown]
# ## Negative example — prey population below fixed point
#
# Below the fixed point the prey population is growing (d x/dt > 0)
# and the balance condition does not hold. Feed y < y* and the
# residual becomes positive.

# %%
y_low = (y_star / 2).to(ureg.mole)
bad_residual = eq.evaluate_with_units({
    "alpha": alpha, "x": x_val, "beta": beta, "y": y_low,
})
print(f"residual at y = y*/2: {bad_residual:+.3e}  (expect > 0)")
assert bad_residual > 0, "prey population is growing, not balanced"
print("✓ Framework correctly reports non-equilibrium state.")

print(f"\n{eq.id} lab complete.")
