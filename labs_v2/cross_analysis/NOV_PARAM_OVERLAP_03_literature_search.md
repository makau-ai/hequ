# NOV-PARAM-OVERLAP-03 Literature Search Record

**Candidate:** Darcy's law + radiation pressure (optical momentum deposition)
**Date:** 2026-04-16
**Pre-composite literature search per board hardening step #1**

## Search queries and findings

| # | Query | Engine | Hits on specific coupling |
|---|-------|--------|--------------------------|
| 1 | `radiation pressure Darcy porous media optical body force seepage` | Web | 0 — results cover Darcy seepage and radiation pressure separately, no intersection |
| 2 | `"optical force" "porous medium" fluid flow photon momentum` | Web | 0 — results cover optical forces in bulk fluids and photon momentum controversy (Abraham-Minkowski), no porous media application |
| 3 | `optofluidic porous media radiation pressure driven flow Psaltis` | Web | 0 — Psaltis 2006 optofluidics is microfluidic channels, not porous matrix; no radiation-pressure body force in Darcy context |
| 4 | `site:arxiv.org "radiation pressure" "Darcy" OR "porous" flow coupling` | Web/arXiv | 0 — results are Darcy flow papers (non-Darcy, micropolar, two-phase), none mention radiation pressure |
| 5 | `"photon pressure" OR "radiation force" seepage OR "Darcy flow" body force coupling experiment` | Web | 0 — results cover Darcy, photophoresis (different mechanism), Stokes-Darcy coupling, no radiation-pressure body force |

## Closest prior art found

1. **Photophoresis** — particle motion from light via asymmetric
   thermal gradients (NOT photon momentum transfer). Different
   mechanism: photophoresis is a thermal-gradient radiometric
   force on individual particles, not a bulk body force on the
   pore fluid. The Darcy body-force slot accepts gravity,
   centrifugal, Lorentz — photon momentum f=αI/c is the same
   category but has not been placed there in the literature.

2. **Acoustic flow in porous media** (Cambridge Core, J. Fluid
   Mech.) — sound-wave momentum transfer to pore fluid drives
   steady streaming. This is the ACOUSTIC analog of what we
   propose for OPTICAL radiation pressure. The acoustic case
   IS published; the optical case apparently is not.

3. **Psaltis et al. optofluidics (2006)** — optical forces in
   microfluidic devices. Open channels, not porous matrix.
   The porous-media geometry adds the Darcy permeability/
   viscosity coupling that free-channel optofluidics does not.

## Deep search (2026-04-16, 12 total queries)

| # | Query | Hits |
|---|-------|------|
| 6 | `"radiation pressure" "porous" seepage velocity absorption body force fluid` | 0 |
| 7 | `"optical streaming" OR "light-driven flow" porous medium permeability` | 0 |
| 8 | `"photon momentum" absorption fluid "body force" Darcy OR permeability` | 0 |
| 9 | `radiation pressure driven convection absorbing liquid porous microfluidic` | 0 |
| 10 | `site:scholar.google.com "optical body force" OR "radiation force" "porous media"` | 0 |
| 11 | `"Abraham force" OR "Minkowski momentum" fluid flow porous absorbing medium` | 0 — Leonhardt 2014 Phys Rev A is bulk fluid, not porous |
| 12 | `"acoustic streaming" porous media analogy optical electromagnetic momentum` | 0 on optical; acoustic analog confirmed (J. Fluid Mech., Nuovo Cimento, PMC 2018) |

**Critical finding from query 12**: the acoustic analog (acoustic
streaming in porous media) IS well-published:
- "Acoustic flow in porous media," J. Fluid Mech.
- "Acoustic streaming in pulsating flows through porous media,"
  La Rivista del Nuovo Cimento (2014)
- "Theory for acoustic streaming in soft porous matter," PMC (2018)

And optical momentum driving bulk fluid (not porous) IS published:
- Leonhardt, "Abraham and Minkowski momenta in the optically
  induced motion of fluids," Phys. Rev. A 90, 033801 (2014)

The specific gap is the COMBINATION: optical momentum deposited
in absorbing pore fluid → Darcy seepage. The acoustic half and
the optical-in-bulk-fluid half each exist independently in their
respective communities. Neither community cites the other.

This is Mechanism A (cross-community isolation) working as
predicted: porous-media hydraulicists study gravity, pressure,
and sometimes acoustics. Radiation-pressure physicists study free
beams, optical tweezers, and microfluidic channels. The porous
matrix + photon momentum intersection is the uncovered zone.

## Novelty assessment

**Novelty grade: specialist-literature-novel to genuinely-novel.**

The acoustic analog (sound-wave momentum → pore-fluid streaming)
exists in the published literature. The optical analog (photon
momentum → pore-fluid seepage) does not appear to exist in any
indexed source we found. The physical mechanism is identical in
structure (wave momentum deposited in absorbing fluid drives a
body force; Darcy's equation balances that force against viscous
resistance from the porous matrix). The optical case is either:

(a) So obvious that everyone assumes it without writing it down
    (possible but would still make the explicit composite novel
    as a FORMALIZATION), or
(b) Genuinely unstudied because the experimental regime (high-
    intensity laser in a dyed porous medium) is unusual enough
    that nobody has set up the experiment.

Either way, the formal cross-domain composite framing with an
explicit numerical prediction (u ≈ 3.3 × 10⁻⁶ m/s at stated
parameters, linear u∝I scaling) and a concrete disconfirmation
path (measure u vs I in a horizontal dyed porous sample) is
not in the literature. That is the novelty claim.

## Distinction from photophoresis (important)

Photophoresis: asymmetric heating of a particle surface →
thermal creep of surrounding gas → particle migration.
Mechanism is THERMAL, not momentum. Requires gas-phase medium.
Acts on individual particles, not on bulk pore fluid.

NOV-PARAM-OVERLAP-03: uniform absorption of photon flux by
dyed pore fluid → bulk momentum deposition f = αI/c in the
fluid → Darcy seepage velocity u = (k/μ)·f. Mechanism is
MOMENTUM TRANSFER (radiation pressure), not thermal. Works in
liquid-phase pore fluid. Acts on the bulk fluid, not on
individual particles. The thermal side-effect (heating from
absorption) is a separate concern that the disconfirmation path
must control for (buoyancy correction).
