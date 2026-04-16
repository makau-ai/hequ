/-
EQ-BLACK-SCHOLES — Black–Scholes PDE

Design artifact for Layer 4. The pricing PDE for a European option
on a geometric-Brownian-motion underlying under the risk-neutral
measure.

A full Lean formalisation would require stochastic calculus, which
mathlib's MeasureTheory.Stochastic is beginning to cover as of
2024-2025 (ongoing work). The transformation to the heat equation
under x = log(S), τ = T − t is the first target of the Medium-scope
change-of-variables sieve.
-/

namespace Hequ.Finance

/-- Black-Scholes PDE as an algebraic identity on the option value
    and its partial derivatives. -/
theorem black_scholes_pde
    (V V_t V_S V_SS S σ r : ℝ) :
    V_t + (1/2) * σ^2 * S^2 * V_SS + r * S * V_S - r * V = 0 ↔
    V_t + (1/2) * σ^2 * S^2 * V_SS + r * S * V_S - r * V = 0 := by
  exact Iff.rfl

/-- Identity with the heat equation under the substitution
    x = log(S), τ = T − t, u = exp(r·τ)·V. Proof deferred to the
    Medium-scope change-of-variables sieve. -/
theorem black_scholes_heat_identity : True := by trivial

end Hequ.Finance
