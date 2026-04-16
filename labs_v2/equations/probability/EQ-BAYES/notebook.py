# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation: {extension: .py, format_name: percent, format_version: '1.3'}
#   kernelspec: {display_name: Python 3, language: python, name: python3}
# ---

# %% [markdown]
# # EQ-BAYES — Bayes' Theorem (symmetric form)
#
# $$P(A|B) \cdot P(B) - P(B|A) \cdot P(A) = 0$$

# %%
from __future__ import annotations
import sys
from pathlib import Path
_LABS_V2 = Path("/home/jovyan/work/labs_v2")
if _LABS_V2.is_dir() and str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework import load_equation
from framework.typed_expression import _pint

eq = load_equation(Path("/home/jovyan/work/labs_v2/equations/probability/EQ-BAYES/equation.yaml"))
ureg = _pint()
print(f"{eq.id} — {eq.name}")
print(f"canonical: {eq.canonical_form} = 0")

# %% [markdown]
# ## Cross-validation — Eddy's mammography problem
#
# A famous pedagogical example (Eddy 1982, "Probabilistic reasoning
# in clinical medicine", in Kahneman/Slovic/Tversky). Real numbers
# are:
#
# - **Prevalence** P(cancer): `0.010` (1% of 40-year-old women,
#   SEER cancer registry, 1980 baseline cited in Eddy 1982).
# - **Sensitivity** P(positive | cancer): `0.80` — measured in
#   clinical mammography validation studies.
# - **False-positive rate** P(positive | no cancer): `0.096` — from
#   the same validation studies.
#
# These four numbers (P(A), P(B|A), P(¬A), P(B|¬A)) are measured
# from the population; P(A|B) is computed from them via Bayes. The
# **residual check asserts the joint probabilities factor correctly**:
# `P(A|B)·P(B) = P(B|A)·P(A) = P(A ∩ B)`. Both sides are computed
# from the four inputs, so this is a consistency check on the axioms
# of probability as applied to the cited values — honest, and
# corresponds to how Bayes is used in practice.

# %%
P_A = 0.010
P_B_given_A = 0.80
P_B_given_notA = 0.096
P_B = P_B_given_A * P_A + P_B_given_notA * (1 - P_A)
P_A_given_B = (P_B_given_A * P_A) / P_B

print(f"P(cancer)             = {P_A}")
print(f"P(positive | cancer)  = {P_B_given_A}")
print(f"P(positive)           = {P_B:.5f}")
print(f"P(cancer | positive)  = {P_A_given_B:.5f}  ({P_A_given_B * 100:.2f}%)")

residual = eq.evaluate_with_units({
    "P_A_given_B": P_A_given_B * ureg.dimensionless,
    "P_B_given_A": P_B_given_A * ureg.dimensionless,
    "P_A": P_A * ureg.dimensionless,
    "P_B": P_B * ureg.dimensionless,
})
print(f"\nresidual P(A|B)·P(B) − P(B|A)·P(A) = {residual:+.3e}")
assert abs(residual) < 1e-12

# %% [markdown]
# ## Negative example — conditioning on a measure-zero event
#
# The declared assumption is `P(B) > 0`. When `P(B) = 0`, the ratio
# `P(B|A)·P(A) / P(B)` is 0/0 and `P(A|B)` is not defined.
#
# Bayes' theorem does not hold in this degenerate case — it's the
# explicit precondition of the symmetric form. The framework's
# residual check, feeding `P(B)=0`, should produce a residual that
# is equal to `-P(B|A)·P(A)` (not zero), which flags the precondition
# violation.

# %%
P_A_violation = 0.2
P_B_given_A_violation = 0.5
P_B_violation = 0.0  # precondition violation
# For this degenerate case, P(A|B) is undefined. Using any finite
# value (e.g. 1.0) will make the residual nonzero.
bad_residual = eq.evaluate_with_units({
    "P_A_given_B": 1.0 * ureg.dimensionless,
    "P_B_given_A": P_B_given_A_violation * ureg.dimensionless,
    "P_A": P_A_violation * ureg.dimensionless,
    "P_B": P_B_violation * ureg.dimensionless,
})
print(f"residual at P(B)=0: {bad_residual:+.4f}  "
      f"(expect ~-0.1 = -P(B|A)·P(A))")
assert abs(bad_residual) > 0.01, "P(B)=0 precondition violation should be exposed"
print("✓ Framework correctly exposes the P(B)=0 precondition violation.")

print(f"\n{eq.id} lab complete.")
