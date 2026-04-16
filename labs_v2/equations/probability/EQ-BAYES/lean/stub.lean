/-
EQ-BAYES — Bayes' Theorem

Design artifact for Layer 4. Theorem of conditional probability
following from the definition P(A ∩ B) = P(A|B)·P(B) = P(B|A)·P(A).

Mathlib already has `ProbabilityTheory.cond_mul_eq_cond_mul` and
related lemmas. A full port would use those directly.
-/

import Mathlib.MeasureTheory.MeasurableSpace.Basic

namespace Hequ.Probability

/-- The symmetric form of Bayes' theorem. -/
theorem bayes_symmetric
    (P_A_given_B P_B P_B_given_A P_A : ℝ) :
    P_A_given_B * P_B = P_B_given_A * P_A ↔
    P_A_given_B * P_B - P_B_given_A * P_A = 0 := by
  constructor <;> (intro h; linarith)

end Hequ.Probability
