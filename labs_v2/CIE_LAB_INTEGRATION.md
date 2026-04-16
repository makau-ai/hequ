# Cyber-Informed Engineering × hequ.ai Lab Integration

**The core insight:** Every equation in hequ.ai's corpus has failure
modes. A CYBER ATTACK is a specific way those failure modes are
triggered — through sensor manipulation, control logic alteration,
timing attacks, or value overrides. CIE's "engineering controls" are
physical mechanisms governed by THE SAME EQUATIONS that make a system
safe even when the digital layer is compromised. hequ.ai can teach
this by demonstrating: here's the equation working normally, here's
what happens when a sensor is spoofed, and here's the physical
engineering control that saves you regardless.

**References:**
- [INL Cyber-Informed Engineering](https://inl.gov/national-security/cie/)
- [DOE National CIE Strategy (2022)](https://www.energy.gov/ceser/cyber-informed-engineering)
- [CIE Principles Slide Presentation, INL](https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_132848.pdf)
- [CIE Engineered Controls Database, OSTI](https://www.osti.gov/biblio/3006995)
- [CIE Implementation Guide, NREL](https://research-hub.nrel.gov/en/publications/cyber-informed-engineering-implementation-guide-version-10-us-dep/)

---

## The 12 CIE Principles (INL) mapped to hequ.ai

| CIE Principle | What it means | hequ.ai connection |
|---|---|---|
| **1. Consequence-Focused Design** | Design against worst-case physical outcomes first | hequ.ai failure_modes define what goes wrong; CIE asks "what if an attacker triggers that failure_mode on purpose?" |
| **2. Engineered Controls** | Physical/mechanical safeguards that work without software | The EQUATIONS governing safety devices (relief valves, fuses, breakers, thermostats) are in hequ.ai's corpus |
| **3. Secure Information Architecture** | Limit which data flows where | Sensor binding integrity — hequ.ai's referential integrity validator checks that the right sensor feeds the right equation |
| **4. Design Simplification** | Remove unnecessary digital complexity | Fewer software-controlled variables = fewer attack surfaces; hequ.ai identifies which variables MUST be measured vs which can be derived |
| **5. Layered Defenses** | Multiple independent protection layers | Multiple equations checking the same physical quantity from different angles (composite verification) |
| **6. Active Defense** | Monitor for anomalous behavior in real time | hequ.ai's DOV-DSL validity envelopes ARE the anomaly detector — if a sensor reading puts the equation outside its validity envelope, something is wrong |
| **7. Interdependency Evaluation** | Understand cascade failures | hequ.ai's composite verification shows exactly how two equations couple — and how a failure in one cascades to the other |
| **8. Cyber-Secure Supply Chain** | Trust the components | hequ.ai's "board is not a CAS" principle: don't trust any single data source; verify with independent computation |
| **9. Planned Resilience** | Design to degrade gracefully | Failure_modes + use_instead: when one equation breaks, the system knows which alternative equation to switch to |
| **10. Engineering Information Control** | Protect design data | Descriptor schema freeze with SHA-256 — immutable provenance of what the system knows |
| **11. Digital Twin / Modeling** | Simulate before building | hequ.ai IS the digital twin — equation predictions compared to physical measurements in real time |
| **12. Organizational Culture** | Train engineers to think about cyber risk | THE LAB STATIONS teach this directly through hands-on demonstrations |

---

## Historical incidents that CIE addresses

Each of these is a case where an attacker (or accident) exploited
the gap between what the software believed and what the physics
actually did. hequ.ai's equations govern both sides.

### Stuxnet (2010) — centrifuge destruction
**What happened:** Malware altered PLC speed setpoints for uranium
enrichment centrifuges at Natanz, Iran. Centrifuges spun at
resonant frequencies, causing mechanical failure. The HMI showed
normal operation to operators.

**Equations involved:**
- EQ-0007 Centripetal acceleration: a = v²/r (centrifuge wall stress)
- EQ-0010 Angular momentum: L = Iω (rotor dynamics)
- EQ-0131 Griffith fracture: σ_f = √(2Eγ/πa) (when the rotor cracks)
- EQ-0006 Hooke's law: material elastic limit (when stress exceeds yield)

**CIE lesson:** A mechanical speed governor (analog, no software)
would have prevented the resonant-frequency attack. The equation
governing the governor is the SAME centripetal acceleration equation
the attack exploited — but implemented in hardware, not software.

**Lab station demo:** Station 3 (Mechanical) — run a motor at
increasing speed via software, show the equation predicts the stress
limit, then demonstrate a physical speed limiter (mechanical
governor or centrifugal clutch) that cuts out regardless of what
the software commands.

### TRITON/TRISIS (2017) — safety system bypass
**What happened:** Malware targeted the Safety Instrumented System
(SIS) at a Saudi petrochemical plant. The SIS is the LAST LINE of
defense — it's supposed to shut down the plant when conditions
become dangerous. TRITON reprogrammed the SIS controllers to NOT
trigger emergency shutdown, potentially allowing a catastrophic
release of hydrogen sulfide gas or an explosion.

**Equations involved:**
- EQ-0020 Ideal gas law: PV = nRT (pressure vessel contents)
- EQ-0044 Poiseuille's law: Q = πr⁴ΔP/(8μL) (flow through pipes)
- EQ-0042 Bernoulli: P + ½ρv² + ρgh = const (pressure dynamics)
- EQ-0006 Hooke's law: F = -kx (spring-loaded relief valve cracking pressure)

**CIE lesson:** A spring-loaded pressure relief valve opens at a
set cracking pressure determined by Hooke's law (F = kx where k is
the spring constant and x is the compression). NO SOFTWARE CAN
PREVENT IT FROM OPENING. This is the CIE principle in its purest
form: the physics of the spring IS the safety system, and no cyber
attack can change Hooke's law.

**Lab station demo:** Station 3 + Station 4 — pressurize a small
vessel (tube pressure sensor monitors P), have software "try" to
prevent the relief valve from opening by commanding the pump to
keep pressurizing. The spring-loaded valve opens anyway at F = kx.
The student sees: software said "keep going," physics said "no."

### Infusion pump vulnerabilities (ongoing)
**What happened:** 73% of networked IV infusion pumps have at least
one cybersecurity vulnerability. Attackers could potentially alter
drug dosing rates, change prescribed medications, or cause pumps
to malfunction. The equations governing drug delivery (Fick's
diffusion, Poiseuille flow through the IV line, pharmacokinetic
half-life) are the same equations an attacker would manipulate.

**Equations involved:**
- EQ-0044 Poiseuille: Q = πr⁴ΔP/(8μL) (flow rate through IV line)
- EQ-0120 Half-life: t½ = 0.693/k_e (drug elimination kinetics)
- EQ-0068 Fick diffusion: J = -D(dC/dx) (drug transport in tissue)
- EQ-0063 Michaelis-Menten: v = V_max[S]/(K_m+[S]) (enzyme kinetics)

**CIE lesson:** A mechanical flow restrictor (a physical orifice
with a fixed diameter) limits the maximum possible flow rate
regardless of what the pump software commands. The maximum flow
is governed by Poiseuille's law with the orifice dimensions —
immutable physics, not software-configurable.

**Lab station demo:** Station 4 (Fluid) — run the peristaltic pump
at software-commanded increasing flow rates. Show that with a
physical flow restrictor inline, the flow rate saturates at
Q_max = πr⁴ΔP_max/(8μL) regardless of pump commands. The student
sees: the orifice IS the safety system.

---

## Per-discipline CIE learning scenarios

### Chemical Engineer
**Scenario:** Reactor temperature control.
**Attack vector:** Compromised thermocouple sends false "temperature
is fine" signal while the reaction actually overheats.
**Equation:** Arrhenius k(T) = A·exp(-E_a/RT) — reaction rate
doubles for every ~10°C rise. If the controller doesn't see the
real temperature, the reaction runs away.
**CIE control:** Redundant analog temperature switch (bimetallic
thermostat) that trips a physical interlock at T_max regardless
of digital readings. The equation governing the thermostat IS the
same thermal expansion equation the reactor uses.
**Lab demo (Station 1):** Peltier heats a sample. Software
thermocouple (KMeter) is "spoofed" (the firmware sends a false
value to makau.ai). The station shows the Arrhenius rate
accelerating while the dashboard shows "safe." Then the analog
thermal switch (mechanical, no software) trips and kills the
Peltier power via a relay. Student learns: the physics of thermal
expansion IS the backup for the physics of chemical kinetics.

### Electrical Engineer
**Scenario:** Grid transformer overload.
**Attack vector:** SCADA system reports normal load while the actual
current exceeds the transformer rating.
**Equation:** Ohm's law V = IR — current through the transformer
generates I²R resistive heating. If the current reporting is
manipulated, the transformer overheats and catches fire.
**CIE control:** Physical fuse wire that melts at I_max, governed
by I²R heating → melting point of the fuse material. No software
can prevent the fuse from blowing.
**Lab demo (Station 2):** DAC drives increasing current through a
circuit. Software "spoofs" the AMeter reading to show safe values.
The physical fuse blows at the rated current. Student sees: the
fuse IS the equation (I²R = energy to melt), and no cyber attack
changes the melting point of copper.

### Civil / Environmental Engineer
**Scenario:** Dam spillway gate control.
**Attack vector:** PLC controlling the spillway gate is compromised.
Gate stays closed during flood, dam overtops.
**Equation:** Bernoulli P + ½ρv² + ρgh = const — water level
creates hydrostatic pressure ρgh that eventually exceeds the
structural capacity of the dam.
**CIE control:** Fuseplug spillway — a section of the dam designed
to ERODE at a specific water level, governed by the soil erosion
equation. No software controls the erosion; it's a consequence of
water pressure exceeding soil cohesion.
**Lab demo (Station 4):** Fill a small reservoir with a tube
"spillway" that the software controls (relay opens/closes the
valve). Software is "compromised" and keeps the valve closed. Water
rises until it overflows through a PHYSICAL overflow channel at a
set height. Student learns: the overflow IS the safety system.

### Biomedical Engineer
**Scenario:** Ventilator tidal volume manipulation.
**Attack vector:** Firmware update changes the PID constants
controlling tidal volume. Patient receives too much or too little
air per breath.
**Equation:** Poiseuille Q = πr⁴ΔP/(8μL) — flow through the
airway circuit. PID controller (EQ-0084) adjusts pressure to
achieve target volume. If PID gains are altered, the flow
trajectory changes.
**CIE control:** Mechanical pressure pop-off valve that limits
the maximum inspiratory pressure to a physically set value
(spring-loaded, Hooke's law). Even if the PID commands infinite
pressure, the pop-off valve opens at F = kx.
**Lab demo (Station 4):** Peristaltic pump delivers air through a
tube (simulating an airway). Software PID controls flow rate.
"Attack" changes PID gain to maximum. Pressure rises until the
spring-loaded valve opens. Tube pressure sensors show the pressure
trace: software commanded overpressure, physics limited it.

### Materials Science Engineer
**Scenario:** 3D metal printer layer temperature control.
**Attack vector:** Compromised build profile changes laser power
or scan speed, creating weak layers with different microstructure.
**Equation:** Stefan-Boltzmann j = σT⁴ — radiated power from the
melt pool. Hall-Petch σ_y = σ₀ + kd^(-1/2) — yield strength
depends on grain size, which depends on cooling rate.
**CIE control:** Passive thermal monitoring (pyrometer with analog
alarm output) that detects out-of-spec melt pool temperature
regardless of the build controller's digital reporting.
**Lab demo (Station 1):** Heat a sample with Peltier (simulating
laser). Thermal camera shows actual temperature. Software reports
a different temperature. The analog thermal alarm (ENV Pro threshold
check) triggers independently. Student sees: analog monitoring
catches what compromised digital reporting misses.

### Network / Software Engineer
**Scenario:** Sensor data injection in a SCADA historian.
**Attack vector:** Man-in-the-middle between sensor and historian
alters the reported values. All downstream analytics (including
equations) compute on false data.
**Equation:** All equations that depend on sensor input are affected.
The failure mode is not in the equation itself but in the INPUT.
**CIE control:** Physics-based plausibility checking using hequ.ai's
DOV-DSL validity envelopes. If a temperature sensor suddenly reports
-50°C in Houston, the DOV-DSL inequality "T > 200 K at sea level
in continental US" catches it instantly. This is CIE Principle 6
(Active Defense) implemented through equation physics.
**Lab demo (any station):** Inject a false sensor reading via
makau.ai's API. Show that hequ.ai's validity envelope catches the
anomaly and flags it as "outside the physics-based plausibility
window." Student learns: equations are anomaly detectors.

### Physician / Healthcare Professional
**Scenario:** Drug dosing calculation from compromised lab values.
**Attack vector:** Laboratory information system reports incorrect
creatinine levels. Cockcroft-Gault equation (EQ-0123) computes
wrong GFR. Drug is dosed based on wrong renal function estimate.
Patient receives toxic dose.
**Equation:** CrCl = ((140-age) × weight) / (72 × S_Cr) — if S_Cr
is manipulated (lower than real), the computed CrCl is too high,
the drug dose is too high, the patient is harmed.
**CIE control:** Independent point-of-care creatinine test (bedside
device, not connected to the LIS network). Physician compares the
LIS value to the independent measurement. If they disagree by >20%,
the LIS value is suspect.
**Lab lesson (data-driven, not physical):** Use SSS bridge to pull
real clinical calculation scenarios. Show: if S_Cr is altered by
20%, how does the computed GFR change? How does the drug dose
change? At what manipulation threshold does the dose become toxic?
hequ.ai computes the sensitivity: ∂Dose/∂S_Cr tells you exactly
how much a lab value manipulation matters.

---

## How hequ.ai's DOV-DSL IS a CIE anomaly detector

The DOV-DSL validity envelope for each equation is, in CIE terms,
a **physics-based intrusion detection system**. It doesn't look at
network packets or log files — it looks at whether the measured
values are physically plausible given the equation's domain of
validity.

Examples of DOV-DSL as CIE:

| Equation | DOV-DSL inequality | What it catches |
|---|---|---|
| Newton II | Ro = U/(fL) ≥ 1 | A spoofed GPS velocity that implies non-inertial regime |
| Hooke | strain < proportional_limit | A sensor reporting impossible deformation for the material |
| Ideal gas | T > 0 AND P > 0 | A temperature sensor reporting absolute zero or negative pressure |
| Fourier heat | k > 0 AND L > 0 | Impossible thermal conductivity or negative length |
| Ohm | I < I_max_fuse | Current sensor reporting beyond the physical fuse rating |
| Poiseuille | Re < 2100 | Flow rate that would imply turbulence (laminar assumption violated) |
| Arrhenius | T > 200K | A thermocouple reading that's physically implausible for the environment |

Each inequality is a PHYSICS-BASED LIMIT that no legitimate
operational condition should violate. If a sensor reading violates
it, either:
1. The equipment has genuinely failed (real failure), or
2. The sensor data has been manipulated (cyber attack)

In both cases, the correct response is the same: STOP TRUSTING THE
DIGITAL READING and fall back to analog/physical verification. This
is CIE Principle 2 (Engineered Controls) implemented through CIE
Principle 6 (Active Defense) using hequ.ai's equation knowledge as
the detection mechanism.

---

## Integration with makau.ai learning sessions

Each CIE demo follows a three-act structure in the learning session:

**Act 1: Normal operation.** The equation works, the sensor reads
correctly, the prediction matches the measurement. Student sees
green checkmarks. "This is how it's supposed to work."

**Act 2: The attack.** makau.ai's orchestrator injects a false sensor
value (simulating a compromised sensor or MITM attack). The equation
still computes — but on false data. The prediction diverges from
reality. If no physical safety system is in place, the physical
system reaches a dangerous state. Student sees: "this is what
happens when you trust software without physics."

**Act 3: The CIE control.** The physical engineering control (fuse,
relief valve, thermal switch, flow restrictor) activates. The
equation governing the safety device trumps the compromised
software. The system is safe despite the cyber attack. Student sees:
"this is why you engineer physics into the safety layer."

**Assessment:** makau.ai's pedagogy engine scores the student on:
- SENSE: did they notice the anomaly in the sensor readings?
- MODEL: did they understand which equation was affected?
- REASON: did they predict the physical consequence?
- ACT: did they identify the correct CIE control?
- SECURE: did they design a defense that works without software?
- COLLABORATE: did they communicate the risk to the team?
- REFLECT: did they update their mental model of trustworthy design?

These are makau.ai's 7 competency axes, applied directly to CIE.
The lab station IS the classroom, the equation IS the lesson, and
the physical safety device IS the answer.
