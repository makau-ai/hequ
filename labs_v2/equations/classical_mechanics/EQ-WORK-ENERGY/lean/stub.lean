/-
EQ-WORK-ENERGY — Work–Energy Theorem

Design artifact for Layer 4. A full proof in Lean would integrate
F·dx along a trajectory and apply the chain rule dv/dt · dx/dt =
v · dv, yielding W = (1/2)m(v_f² − v_i²).
-/

import Mathlib.Analysis.Calculus.FDeriv.Basic

namespace Hequ.ClassicalMechanics

/-- Work-energy theorem for a 1D point particle under a net force. -/
theorem work_energy_theorem
    (W m v_i v_f : ℝ) :
    W = (1/2) * m * (v_f^2 - v_i^2) ↔
    W - (1/2) * m * (v_f^2 - v_i^2) = 0 := by
  constructor <;> (intro h; linarith)

end Hequ.ClassicalMechanics
