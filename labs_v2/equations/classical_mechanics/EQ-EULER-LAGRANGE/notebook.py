# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-EULER-LAGRANGE — Euler–Lagrange Equation (1D)
#
# $$\frac{d}{dt}\!\left(\frac{\partial L}{\partial \dot q}\right) - \frac{\partial L}{\partial q} = 0$$
#
# Stationary condition for the action $S = \int L\,dt$ under
# fixed-endpoint variations. Foundational for classical mechanics;
# every force law derivable from a potential also derivable from
# an Euler–Lagrange equation on an appropriate Lagrangian.

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/classical_mechanics/EQ-EULER-LAGRANGE/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — simple harmonic oscillator
#
# For $L = \tfrac{1}{2} m \dot x^2 - \tfrac{1}{2} k x^2$:
# - $\partial L / \partial \dot x = m \dot x$, so
#   $\frac{d}{dt}(\partial L / \partial \dot x) = m \ddot x$.
# - $\partial L / \partial x = -k x$.
# - The EL equation gives $m \ddot x + k x = 0$ — Hooke's law.
#
# We pick a reference oscillator with k = 4 N/m, m = 1 kg, at
# a time where x = 1 m and ẍ = -4 m/s². The EL form then asserts
# that $\frac{d}{dt}(m \dot x) - \partial L / \partial x =
# m \ddot x - (-k x) = -4 + 4 = 0$.

# %%
m = 1.0 * ureg.kilogram
k = 4.0 * ureg.newton / ureg.meter
x = 1.0 * ureg.meter
x_ddot = -4.0 * ureg.meter / ureg.second**2

# d/dt(dL/dqdot) = m * d²x/dt² — a force (newtons)
d_dt_dL_dqdot = (m * x_ddot).to(ureg.newton)
# dL/dq = -k * x — also a force (newtons), with sign
dL_dq = (-k * x).to(ureg.newton)

print(f"m·ẍ = {d_dt_dL_dqdot}")
print(f"∂L/∂x = {dL_dq}")

residual = eq.evaluate_with_units({
    "d_dt_dL_dqdot": d_dt_dL_dqdot,
    "dL_dq": dL_dq,
})
print(f"residual = {residual:+.3e}")
assert abs(residual) < 1e-10, "Euler-Lagrange must vanish on the oscillator trajectory"

# %% [markdown]
# ## Negative example — trajectory off the solution manifold
#
# If the body is not on the solution trajectory (e.g., we impose
# ẍ = 0 while still in a harmonic potential), the EL form does not
# vanish — exactly what the framework is supposed to detect.

# %%
x_ddot_bad = 0.0 * ureg.meter / ureg.second**2
d_dt_dL_dqdot_bad = (m * x_ddot_bad).to(ureg.newton)
bad_residual = eq.evaluate_with_units({
    "d_dt_dL_dqdot": d_dt_dL_dqdot_bad,
    "dL_dq": dL_dq,  # still -k*x
})
print(f"Off-trajectory (ẍ=0 in a harmonic well): residual = {bad_residual:+.3f}")
assert abs(bad_residual) > 1.0, "off-trajectory state should not satisfy EL"
print("✓ Framework correctly rejects a non-stationary trajectory.")

print(f"\n{eq.id} lab complete.")
