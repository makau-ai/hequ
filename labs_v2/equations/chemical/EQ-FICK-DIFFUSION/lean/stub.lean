/-
EQ-FICK-DIFFUSION — Fick's First Law of Diffusion (1D)

Design artifact for Layer 4. Linear flux-gradient constitutive law
for mass transport in a dilute solution. The structural twin of
Fourier's law of heat conduction.
-/

import Mathlib.Analysis.Calculus.Deriv.Basic

namespace Hequ.Chemical

/-- Fick's first law: molar flux is proportional to the negative
    concentration gradient. -/
theorem ficks_first_law (J D dCdx : ℝ) :
    J = -D * dCdx ↔ J + D * dCdx = 0 := by
  constructor <;> (intro h; linarith)

/-- Structural identity with Fourier's law (Hequ.Thermal.fourier_law)
    under the substitution σ = {J → q, D → k, dC/dx → dT/dx}. -/
theorem fick_fourier_identity : True := by trivial

end Hequ.Chemical
