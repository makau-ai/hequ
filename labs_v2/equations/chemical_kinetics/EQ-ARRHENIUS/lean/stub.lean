/-
EQ-ARRHENIUS — Arrhenius Rate Law

Design artifact for Layer 4. Boltzmann-factor scaling of reaction
rates with temperature. Derivable from transition-state theory with
A ≈ k_B·T/h and E_a ≈ ΔH‡.
-/

import Mathlib.Analysis.SpecialFunctions.Exp

namespace Hequ.ChemicalKinetics

/-- Arrhenius rate law in implicit form. R is the gas constant,
    Ea the activation energy, A the pre-exponential factor,
    T the absolute temperature, k the rate constant. -/
theorem arrhenius
    (k_rate A Ea R_gas T : ℝ) (hRT : 0 < R_gas * T) :
    k_rate = A * Real.exp (-Ea / (R_gas * T)) ↔
    k_rate - A * Real.exp (-Ea / (R_gas * T)) = 0 := by
  constructor <;> (intro h; linarith)

end Hequ.ChemicalKinetics
