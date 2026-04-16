# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-SCHRODINGER — 1D Free-Particle Schrödinger Equation
#
# $$i\hbar\, \partial_t \psi = -\frac{\hbar^2}{2m} \partial_x^2 \psi$$
#
# Wick rotation $t \to -i\tau$ turns this into the heat equation —
# the target of the Medium CoV sieve's Wick-rotation substitution.

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/quantum_mechanics/EQ-SCHRODINGER/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical (algebraic): {eq.canonical_form}")
print(f"canonical (derivative): {eq.canonical_form_derivatives}")

# %% [markdown]
# ## Cross-validation — free plane-wave solution
#
# The simplest exact solution to the free Schrödinger equation is a
# plane wave $\psi(x,t) = e^{i(kx - \omega t)}$ with dispersion
# $\omega = \hbar k^2 / (2m)$.
#
# We verify symbolically that the plane wave satisfies the PDE, then
# evaluate ψ_t and ψ_xx at (x=0, t=0) and feed those complex values
# into the atomic canonical form to check the residual vanishes.
# Chosen over a Gaussian packet because the plane wave is exact in
# closed form with no subtle prefactor; a Gaussian has a
# normalisation that's easy to get wrong.

# %%
import sympy as sp
hbar = sp.Symbol("hbar", positive=True)
m_sym = sp.Symbol("m", positive=True)
k_sym = sp.Symbol("k", real=True, positive=True)
x_sym = sp.Symbol("x", real=True)
t_sym = sp.Symbol("t", real=True)

omega = hbar * k_sym**2 / (2 * m_sym)
psi = sp.exp(sp.I * (k_sym * x_sym - omega * t_sym))
psi_t = sp.diff(psi, t_sym)
psi_xx = sp.diff(psi, x_sym, 2)

# PDE residual: iℏ ψ_t + (ℏ²/2m) ψ_xx
residual_expr = sp.I * hbar * psi_t + (hbar**2 / (2 * m_sym)) * psi_xx
residual_simp = sp.simplify(residual_expr)
print(f"Symbolic PDE residual on plane wave: {residual_simp}")
assert residual_simp == 0, "Plane wave must satisfy the free Schrödinger equation"

# Numeric values at (x=0, t=0) with ℏ=1, m=1, k=1:
subs0 = {hbar: 1.0, m_sym: 1.0, k_sym: 1.0, x_sym: 0.0, t_sym: 0.0}
psi_t_val = complex(psi_t.subs(subs0))
psi_xx_val = complex(psi_xx.subs(subs0))
print(f"ψ_t at origin = {psi_t_val}")
print(f"ψ_xx at origin = {psi_xx_val}")

# The atomic canonical form I*hbar*psi_t + (hbar²/2m)*psi_xx uses
# real-valued atomic symbols, so we can't pass complex numbers
# directly through the pint typing system. Instead we verify the
# real and imaginary parts separately by substituting into the
# sympy-parsed canonical_form directly.
cf = eq.canonical_form
subs_cf = {
    sp.Symbol("I"): sp.I,
    sp.Symbol("hbar"): 1.0,
    sp.Symbol("m"): 1.0,
    sp.Symbol("psi_t"): psi_t_val,
    sp.Symbol("psi_xx"): psi_xx_val,
}
residual_num = complex(cf.subs(subs_cf))
print(f"Canonical form residual at (x=0, t=0): {residual_num}")
assert abs(residual_num) < 1e-10, "canonical form must vanish on the exact solution"

# %% [markdown]
# ## Negative example — wrong dispersion
#
# If we artificially multiply the kinetic term by 2 (i.e., claim
# $\hbar^2/(m)$ instead of $\hbar^2/(2m)$), the PDE is no longer
# satisfied by the Gaussian — the dispersion rate is wrong. The
# residual becomes nonzero.

# %%
cf_wrong = sp.I * sp.Symbol("hbar") * sp.Symbol("psi_t") + (
    sp.Symbol("hbar")**2 / sp.Symbol("m")
) * sp.Symbol("psi_xx")
bad_residual = complex(cf_wrong.subs(subs_cf))
print(f"Wrong-coefficient residual: {bad_residual}")
assert abs(bad_residual) > 0.01, "wrong dispersion coefficient should break the PDE"
print("✓ Framework correctly exposes the wrong-dispersion violation.")

print(f"\n{eq.id} lab complete.")
