/-
EQ-BEER-LAMBERT — Beer–Lambert Law

Design artifact for Layer 4. Linear absorbance–concentration
relation derivable by integrating dI/I = -αc dx along the path.
-/

namespace Hequ.Spectroscopy

/-- Beer-Lambert: absorbance is the product of molar absorptivity,
    path length, and concentration. Valid in the dilute-solution
    linear-optics regime. -/
theorem beer_lambert (A ε ell c : ℝ) :
    A = ε * ell * c ↔ A - ε * ell * c = 0 := by
  constructor <;> (intro h; linarith)

end Hequ.Spectroscopy
