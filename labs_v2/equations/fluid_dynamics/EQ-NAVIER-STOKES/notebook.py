# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-NAVIER-STOKES — 1D Incompressible Navier–Stokes (Momentum)
#
# $$\rho\,u_t + \rho u\, u_x + P_x - \mu\, u_{xx} - \rho g = 0$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/fluid_dynamics/EQ-NAVIER-STOKES/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical (algebraic): {eq.canonical_form}")

# %% [markdown]
# ## Cross-validation — Plane Poiseuille flow (steady, pressure-driven)
#
# For steady fully-developed flow of a viscous incompressible fluid
# between two flat plates separated by 2h, with a constant pressure
# gradient −dP/dx = G > 0 and no gravity in the flow direction,
# the analytic solution is the parabolic profile
# $u(y) = (G/(2\mu))(h^2 - y^2)$. At the centreline (y=0), u = G h² / (2μ).
#
# At the centreline with steady flow: u_t = 0 (steady), u_x = 0
# (fully developed), u_xx = -G/μ (from the parabolic second
# derivative), and all gravity in the streamwise direction = 0.
# The NS momentum equation then gives:
#   ρ·0 + ρ·u·0 + (-G) - μ·(-G/μ) - 0 = -G + G = 0.
#
# Reference: Kundu & Cohen, *Fluid Mechanics* 6e §9.2, worked example.

# %%
# Water at 20 °C, Kundu & Cohen values.
rho = 998.0 * ureg.kilogram / ureg.meter**3
mu = 1.0e-3 * ureg.pascal * ureg.second
G = 10.0 * ureg.pascal / ureg.meter    # pressure gradient magnitude
h = 0.01 * ureg.meter                  # half-gap
u_centreline = (G * h**2 / (2 * mu)).to(ureg.meter / ureg.second)
print(f"Centreline velocity: {u_centreline}")

u_t = 0.0 * ureg.meter / ureg.second**2    # steady
u_x = 0.0 / ureg.second                    # fully developed
u_xx = -(G / mu).to(1.0 / (ureg.meter * ureg.second))
P_x = -G
g = 0.0 * ureg.meter / ureg.second**2

residual = eq.evaluate_with_units({
    "rho": rho, "u_t": u_t, "u": u_centreline, "u_x": u_x,
    "P_x": P_x, "mu": mu, "u_xx": u_xx, "g": g,
})
print(f"NS residual at centreline (Poiseuille): {residual:+.3e}")
assert abs(residual) < 1e-10

# %% [markdown]
# ## Negative example — inviscid substitution
#
# Setting μ = 0 in a viscous-dominated flow breaks the momentum
# balance: the viscous term disappears, and the remaining pressure
# gradient has no way to balance against the now-absent viscous
# dissipation.

# %%
mu_inviscid = 0.0 * ureg.pascal * ureg.second
# u_xx = -G/μ diverges in the limit, but we use the physical
# (measured) u_xx from the viscous solution and pair it with μ=0.
bad_residual = eq.evaluate_with_units({
    "rho": rho, "u_t": u_t, "u": u_centreline, "u_x": u_x,
    "P_x": P_x, "mu": mu_inviscid, "u_xx": u_xx, "g": g,
})
print(f"NS residual with μ=0 (viscous state): {bad_residual:+.3e}")
assert abs(bad_residual) > 1.0
print("✓ Framework correctly exposes the inviscid/viscous mismatch.")

print(f"\n{eq.id} lab complete.")
