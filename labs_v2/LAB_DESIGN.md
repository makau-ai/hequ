# hequ.ai Automated Lab Design

**Goal:** A fully self-resetting benchtop lab that verifies
equations 24/7 with zero human interaction AND serves as an
interactive learning platform when a student is present.

**Core design principles:**
1. No gravity-dependent actions (no pouring, no hanging)
2. No consumables (no boiling water, no depleting chemicals)
3. All positioning via servo/stepper (deterministic home)
4. All thermal via Peltier (heats AND cools electronically)
5. All fluid via peristaltic pump (bidirectional, sealed loop)
6. All switching via relay (no manual contacts)
7. Every station has a HOME state reachable in <30 seconds
8. Every station streams to makau.ai in both auto and learning mode

---

## Physical Layout

```
┌─────────────────────────────────────────────────────────┐
│                    HEQU.AI LAB BENCH                     │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ STATION 1│  │ STATION 2│  │ STATION 3│  │STATION 4│  │
│  │ THERMAL  │  │ELECTRICAL│  │MECHANICAL│  │ FLUID  │  │
│  │          │  │          │  │          │  │        │  │
│  │ Peltier  │  │ Circuit  │  │ Spring + │  │ Tube + │  │
│  │ + copper │  │ board +  │  │ pendulum │  │ porous │  │
│  │ rod      │  │ motor    │  │ + mass   │  │ sample │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       │             │             │             │        │
│  ┌────┴─────────────┴─────────────┴─────────────┴────┐  │
│  │              M5Stack Core2 Controllers             │  │
│  │     WiFi → makau.ai → hequ.ai Cloud Function      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────┐                          ┌─────────────┐  │
│  │ STATION 5│                          │  OPTICAL     │  │
│  │  OPTICAL │                          │  (enclosed   │  │
│  │ LED+cuve-│                          │   light-     │  │
│  │ tte+det  │                          │   tight box) │  │
│  └──────────┘                          └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

Each station is on a ~30cm × 20cm baseplate, self-contained,
independently powered via USB-C, and communicates only via WiFi.
No wires between stations. Stations can be rearranged, removed,
or added without reconfiguring the others.

---

## Station 1: THERMAL

**Equations:** Fourier heat conduction, Newton cooling, Arrhenius
rate law, Carnot efficiency, ideal gas PV=nRT, Clausius-Clapeyron,
Stefan-Boltzmann, Soret/Dufour composites.

### Physical setup
```
[Peltier HOT side]─[thermocouple 1]── copper rod ──[thermocouple 2]─[Peltier COLD side]
       │                                                                    │
   heatsink                                                             heatsink
   + fan                                                                + fan
       │                                                                    │
       └──── H-Bridge #1 ──── Core2 #1 ──── H-Bridge #2 ────────────────────┘
                                  │
                              ENV Pro (ambient T, P, humidity)
                              Thermal Camera (gradient visualization)
```

### Components
| Part | M5Stack SKU | Qty | Purpose |
|------|------------|-----|---------|
| Core2 | Controller | 1 | Station brain |
| KMeter ISO | Thermocouple | 3 | T_hot, T_cold, T_mid (optional 3rd point for linearity check) |
| H-Bridge Unit | Motor driver | 2 | Drive Peltier modules (bidirectional: heat or cool) |
| ENV Pro | Environmental | 1 | Ambient T, P, humidity for reference |
| Thermal Camera | MLX90640 | 1 | Visual gradient map for learning mode |
| **Non-M5Stack** | | | |
| Peltier TEC1-12706 | Amazon | 2 | One for hot end, one for cold end |
| Aluminum heatsinks + 5V fans | Amazon | 2 | Dissipate Peltier waste heat |
| Copper rod 30cm × 1cm | Hardware | 1 | The conductor under test |
| Thermal paste | Amazon | 1 | Peltier-to-rod contact |

### Auto-reset cycle (Fourier experiment)
```
PHASE         DURATION    ACTION
SET           60s         H-Bridge #1 forward → Peltier heats hot end to 80°C
                          H-Bridge #2 forward → Peltier cools cold end to 10°C
                          (PID loop on Core2 using KMeter feedback)
STABILIZE     120s        Wait for dT/dt < 0.1°C/s at both ends
                          (linear gradient establishes)
MEASURE       10s         Read T_hot, T_cold, T_mid
                          Compute q = k·(T_hot - T_cold)/L
                          Stream all readings to makau.ai
VERIFY        1s          Compare prediction to measured gradient linearity
                          Record to ledger
RESET         60s         Both H-Bridges reverse → cool hot end, warm cold end
                          Target: both ends within 2°C of ambient
IDLE          30s         Confirm reset complete, all readings at ambient
TOTAL CYCLE   ~4.5 min
```

### Newton cooling variant
Same hardware, different cycle:
1. SET: Heat one end to 80°C, disconnect Peltier (relay off)
2. MEASURE: Record T(t) every 2 seconds as it cools
3. VERIFY: Fit exponential T(t) = T_env + (T_0 - T_env)·exp(-h·t)
4. RESET: Peltier cools back to ambient

### Arrhenius variant
Add a small sealed reaction chamber on the hot end:
- Effervescent tablet in water at controlled temperature
- CO2 sensor (SCD40) measures gas evolution rate
- Repeat at 3 different temperatures (20°C, 40°C, 60°C)
- Fit k(T) = A·exp(-E_a/RT), estimate E_a
- RESET: Peristaltic pump flushes chamber with fresh water

---

## Station 2: ELECTRICAL

**Equations:** Ohm V=IR, Kirchhoff voltage/current laws, Faraday
induction, DC motor composite, voice-coil composite, PID
controller, RC circuit transients.

### Physical setup
```
┌─── Relay Matrix (4-ch relay module × 2) ───┐
│                                              │
│  R1=10Ω  R2=100Ω  R3=1kΩ  R4=10kΩ         │
│  C1=10μF  C2=100μF                          │
│  DC motor (with encoder)                     │
│  Speaker driver (voice coil)                 │
│  Inductor (for Faraday)                      │
│                                              │
└──── VMeter ──── AMeter ──── Core2 #2 ────────┘
                                │
                            DAC (set V_s)
                            Encoder (read ω)
                            VAMeter (precision P)
```

### Components
| Part | M5Stack SKU | Qty | Purpose |
|------|------------|-----|---------|
| Core2 | Controller | 1 | |
| 4-Ch Relay Module | Relay | 2 | Switch between R1/R2/R3/R4, connect/disconnect C, motor, coil |
| VMeter | Voltage | 2 | Measure voltage at multiple points in the circuit |
| AMeter | Current | 2 | Measure current through different branches |
| VAMeter | Precision V+A+P | 1 | High-precision power measurement for motor |
| DAC 2 Unit | Voltage source | 1 | Programmable V_s (0-10V) |
| GoPlus2 | Motor driver | 1 | Drive DC motor and servos |
| Encoder | Rotation | 1 | Measure motor shaft speed (ω) |
| **Non-M5Stack** | | | |
| Resistor assortment | Electronics | 1 set | 10Ω, 100Ω, 1kΩ, 10kΩ (through-hole, solderable) |
| Capacitor assortment | Electronics | 1 set | 10μF, 100μF electrolytic |
| Small DC motor | Amazon | 1 | With known K on datasheet |
| Small speaker driver | Amazon | 1 | With known BL on datasheet |
| Breadboard | Electronics | 1 | Component mounting |

### Auto-reset cycle (Ohm's law sweep)
```
PHASE         DURATION    ACTION
SET R1        2s          Relay #1 ON → connects R1=10Ω into circuit
                          DAC sets V_s = 5.0V
MEASURE R1    2s          VMeter reads V across R1
                          AMeter reads I through R1
                          Compute: V/I should = 10Ω
SET R2        2s          Relay #1 OFF, Relay #2 ON → R2=100Ω
                          DAC keeps V_s = 5.0V
MEASURE R2    2s          V/I should = 100Ω
SET R3        2s          Switch to R3=1kΩ
MEASURE R3    2s
SET R4        2s          Switch to R4=10kΩ
MEASURE R4    2s
SWEEP V       10s         For current R: sweep DAC from 1V to 10V in 10 steps
                          At each step: measure V, I, verify linearity
VERIFY        1s          Fit V vs I, verify slope = R for each resistor
RESET         2s          All relays OFF, DAC to 0V
TOTAL CYCLE   ~30 seconds for a full Ohm sweep across 4 resistors
```

### DC motor variant
1. Relay connects motor + encoder
2. DAC sweeps V_s from 2V to 10V in 5 steps
3. At each step: measure V_s (VMeter), I (AMeter), ω (encoder)
4. Verify: ω = V_s/K - τ_L·R/K² at each V_s
5. Plot speed-torque curve
6. RESET: DAC to 0V, wait for motor to stop (encoder reads ω → 0)

### RC transient variant
1. Relay connects R + C in series
2. DAC steps from 0V to 5V (step input)
3. VMeter samples V_C(t) at 100 Hz for 5 seconds
4. Verify: V_C(t) = V_s·(1 - exp(-t/RC))
5. RESET: Relay shorts C to discharge, wait for V_C < 0.1V

---

## Station 3: MECHANICAL

**Equations:** Newton F=ma, Hooke F=-kx, SHO composite, work-
energy, impulse-momentum, angular momentum, centripetal,
pendulum period.

### Physical setup
```
┌─── Vertical rail (aluminum extrusion, 40cm) ───┐
│                                                  │
│  [Servo arm]─────[spring]─────[mass + IMU]      │
│       │              │             │             │
│    (compresses)   (k known)    (m known)        │
│                                                  │
│  [ToF sensor at bottom]──── measures x(t) ──────│
│                                                  │
│  [Pendulum pivot]─[string]─[bob + IMU #2]       │
│       │                        │                 │
│  [Servo releases bob]     (swings freely)       │
│                                                  │
└──── Weight sensor (base) ──── Core2 #3 ─────────┘
```

### Components
| Part | M5Stack SKU | Qty | Purpose |
|------|------------|-----|---------|
| Core2 | Controller | 1 | |
| IMU Unit (MPU6886) | Motion | 2 | On spring mass + on pendulum bob |
| ToF Distance (VL53L0X) | Displacement | 2 | Measure spring extension, pendulum position |
| Weight I2C (HX711) | Force | 1 | Measure static force (verify F=-kx) |
| 8-Servo Driver | Servo control | 1 | Drive spring compressor + pendulum release |
| **Non-M5Stack** | | | |
| Linear servo/actuator | Amazon | 1 | Compress spring to set amplitude |
| Standard servo | Amazon | 1 | Pendulum release mechanism (hold + release) |
| Springs (3 different k) | Amazon | 1 set | 10, 25, 50 N/m |
| Masses (50g, 100g, 200g) | Amazon | 1 set | Known masses for F=ma and SHO |
| Aluminum extrusion 40cm | Amazon | 1 | Vertical rail for guided motion |
| Pendulum string + bob | DIY | 1 | For pendulum period measurement |
| Latch mechanism | 3D print/buy | 1 | Electromagnetic latch for pendulum release |

### Auto-reset cycle (SHO experiment)
```
PHASE         DURATION    ACTION
SET           5s          Servo compresses spring by x_0 (e.g., 5cm)
                          ToF confirms displacement = x_0
RELEASE       0.1s        Servo releases (spring-loaded detent)
MEASURE       10s         IMU records acceleration a(t) at 200 Hz
                          ToF records position x(t) at 50 Hz
                          Weight sensor records F(t) if mass contacts base
ANALYZE       1s          FFT of x(t) → extract period T_measured
                          Compare to T_predicted = 2π√(m/k)
                          Compute: |T_meas - T_pred| / T_pred
VERIFY        1s          Pass if relative error < 5%
RESET         5s          Servo retracts, re-compresses spring
                          Wait for oscillation to damp out
                          (or servo catches mass at equilibrium)
TOTAL CYCLE   ~22 seconds
```

### Pendulum variant
1. Servo arm holds pendulum bob at angle θ_0
2. Electromagnetic latch releases bob
3. IMU on bob records angular acceleration α(t)
4. ToF or IMU-derived angle tracks θ(t)
5. Extract period T, compare to T = 2π√(L/g)
6. RESET: Servo arm catches bob on the return swing (or wait for damping)

---

## Station 4: FLUID

**Equations:** Poiseuille Q=πr⁴ΔP/(8μL), Darcy Q=-KA(dh/dl),
Bernoulli, Reynolds number, Fick diffusion, Stokes drag,
Darcy+RadPress novel composite.

### Physical setup
```
┌─── Closed-loop fluid circuit ───────────────────┐
│                                                   │
│  [Reservoir]──[Pump]──[Tube/Porous sample]──┐    │
│       ↑                    │                 │    │
│       └────────────────────┘                 │    │
│                                              │    │
│  Pressure taps: [P1]────[P2]────[P3]        │    │
│                                              │    │
│  Flow sensor: [inlet]────[outlet]            │    │
│                                              │    │
│  [LED/Laser]──[cuvette]──[light sensor]      │    │
│  (Beer-Lambert or RadPress experiments)      │    │
│                                              │    │
└──── Core2 #4 + Relay (pump on/off) ──────────┘
```

### Components
| Part | M5Stack SKU | Qty | Purpose |
|------|------------|-----|---------|
| Core2 | Controller | 1 | |
| Tube Pressure Unit | Pressure | 3 | ΔP across tube section (3-point profile) |
| Water Flow Unit | Flow | 2 | Inlet + outlet flow rate |
| Light Unit | Light | 2 | Incident + transmitted (Beer-Lambert) |
| DLight Unit | Calibrated lux | 1 | Quantitative intensity |
| DAC 2 Unit | LED control | 1 | Set LED/laser intensity for optical experiments |
| Relay Unit | Pump on/off | 1 | Control peristaltic pump |
| Color Sensor | Spectroscopy | 1 | Track dye concentration (Fick diffusion proxy) |
| **Non-M5Stack** | | | |
| Peristaltic pump 12V | Amazon | 1 | Bidirectional, ~10-100 mL/min |
| Silicone tubing (various ID) | Amazon | 1 set | 2mm, 4mm, 6mm for Poiseuille scaling |
| Glass/acrylic tube 30cm | Amazon | 1 | The Poiseuille test section |
| Porous sample (glass beads in tube) | Hardware | 1 | For Darcy's law |
| Glass cuvettes | Amazon | 4 | Beer-Lambert optical path |
| India ink / food dye | Amazon | 1 | Absorber for Beer-Lambert + Darcy+RadPress |
| Small reservoir (~500mL) | Amazon | 1 | Closed-loop fluid supply |
| T-connectors + valves | Hardware | 1 set | Split flow for different experiments |

### Auto-reset cycle (Poiseuille experiment)
```
PHASE         DURATION    ACTION
FILL          15s         Pump ON forward → fluid fills the tube circuit
                          Flow sensors confirm flow established
SET           10s         Pump runs at constant speed (known Q)
                          Wait for steady state (P readings stable)
MEASURE       10s         Read P1, P2, P3 simultaneously
                          Read Q_in, Q_out
                          ΔP = P1 - P3
                          Verify: Q_measured ≈ πr⁴ΔP/(8μL)
VARY          30s         Change pump speed in 5 steps
                          At each step: measure Q and ΔP
                          Build the Q vs ΔP curve (should be linear)
VERIFY        1s          Fit Q = (πr⁴/(8μL))·ΔP, extract r⁴/(8μL)
                          Compare to known tube dimensions
RESET         15s         Pump OFF
                          Wait for flow to stop (flow sensors → 0)
                          Optionally pump reverse to drain
TOTAL CYCLE   ~80 seconds
```

### Darcy variant
Replace the glass tube with the porous-bead sample. Same cycle.
Q = -KA(dh/dl) where K is the porous permeability.

### Beer-Lambert variant
1. Pump fills cuvette with dyed solution at known concentration
2. DAC sets LED intensity
3. Light sensors measure incident I_0 and transmitted I
4. Compute A = -log10(I/I_0), verify A = εlc
5. RESET: Pump flushes cuvette with clear water

---

## Station 5: OPTICAL (enclosed light-tight box)

**Equations:** Beer-Lambert A=εlc, Stefan-Boltzmann j=σT⁴, Snell's
law, photoelectric (qualitative), inverse-square law.

### Physical setup
```
┌─── Light-tight enclosure (black acrylic box, ~30cm cube) ───┐
│                                                               │
│  [LED array (DAC-controlled)]                                │
│       │                                                       │
│  [Aperture/collimator]──[cuvette holder]──[detector array]   │
│                                                               │
│  ToF sensors at known distances from LED (inverse-square)    │
│  Light sensors at 3 distances: 10cm, 20cm, 30cm              │
│                                                               │
│  [Thermal emitter (nichrome wire + relay)]──[thermal cam]    │
│  (for Stefan-Boltzmann: measure radiated power vs T)         │
│                                                               │
└──── Core2 #5 (or ATOM Lite) ─────────────────────────────────┘
```

---

## Learning Mode Architecture

When a student connects (via makau.ai learner session), any
station switches from AUTO mode to LEARNING mode:

### Auto mode (24/7, no human)
```
while True:
    set_conditions(next_experiment_params)
    wait_steady_state()
    measure()
    predict(equation)
    verify(prediction vs measurement)
    record_to_ledger()
    reset()
```

### Learning mode (interactive, student present)
```
on_student_connect(session_id):
    pause_auto_cycle()
    display_welcome(station_screen)

    for step in lesson.steps:
        display_instruction(step.text)      # M5Stack touchscreen
        if step.requires_student_action:
            wait_for_student_input()         # touch button, adjust dial
        set_conditions(step.params)          # station does the physics
        measure()
        display_live_data(readings)          # real-time graph on screen
        prompt_prediction(step.question)     # "what do you think q will be?"
        student_answers(via makau.ai)
        reveal_result(measured vs predicted)
        record_assessment(session_id)        # mastery scoring

    resume_auto_cycle()
```

### Learning session data flow
```
Student → makau.ai learner session → hequ.ai station
  │                                       │
  │  "set T_hot to 80°C"                 │
  │  ←── station executes ────────────── │
  │  "what will T_cold be?"              │
  │  student answers: "40°C"             │
  │  ←── station measures: T_cold = 52°C │
  │  "the equation predicts 52°C because │
  │   Fourier's law says q = k·ΔT/L"    │
  │                                       │
  └── assessment: partial understanding ──┘
       mastery: 0.6 → scaffold next step
```

### What makau.ai sees in learning mode
```
POST /api/events/sensor  ← live readings from the station
POST /api/events/pedagogy:assessment  ← mastery score update
GET /api/learner/profile  ← competency levels
POST /api/interventions/alerts  ← if student is stuck
```

The station IS the lab equipment AND the tutor simultaneously.
The M5Stack touchscreen shows the experiment happening in real
time with the equation overlaid. The student sees physics
happening, makes predictions, gets immediate feedback from
real measured data, and the makau.ai pedagogy engine tracks
their learning progress.

---

## Orchestration Firmware Architecture

Each Core2 runs the same base firmware with station-specific
configuration loaded from a YAML file on the SD card:

```cpp
// Pseudocode — actual implementation in Arduino/MicroPython
void loop() {
    if (learning_mode_active()) {
        run_learning_step();
    } else {
        ExperimentConfig exp = get_next_experiment();
        set_conditions(exp.params);
        wait_for_steady_state(exp.stability_criteria);
        SensorReadings readings = measure_all();
        float predicted = evaluate_equation(exp.formula, readings);
        VerificationResult result = verify(predicted, readings, exp.tolerance);
        post_to_makau(result);
        reset_to_home();
    }
}
```

### Configuration per station (SD card)
```yaml
station_id: thermal-01
experiments:
  - id: fourier-conduction
    formula: "k * (T_hot - T_cold) / L"
    set_params:
      peltier_hot_target_C: 80
      peltier_cold_target_C: 10
    measure:
      T_hot: {sensor: kmeter-1, unit: C}
      T_cold: {sensor: kmeter-2, unit: C}
    constants:
      k: 401.0
      L: 0.30
    stability: {max_dT_dt: 0.1, window_s: 10}
    tolerance: 0.05
    reset:
      peltier_hot_target_C: 25
      peltier_cold_target_C: 25
```

---

## Bill of Materials (all stations combined)

| Station | M5Stack items | Non-M5Stack | Station cost |
|---------|--------------|-------------|-------------|
| Thermal | Core2 + 3 KMeter + 2 H-Bridge + ENV Pro + Thermal Cam | 2 Peltier + heatsinks + copper rod | ~$180 |
| Electrical | Core2 + 2 VMeter + 2 AMeter + VAMeter + 2 Relay + DAC + GoPlus2 + Encoder | Resistors + caps + motor + speaker + breadboard | ~$160 |
| Mechanical | Core2 + 2 IMU + 2 ToF + Weight + 8-Servo | Linear actuator + springs + masses + rail + pendulum | ~$130 |
| Fluid | Core2 + 3 Tube Pressure + 2 Flow + 2 Light + DLight + DAC + Relay + Color | Pump + tubing + tube + porous sample + cuvettes + dye + reservoir | ~$180 |
| Optical | ATOM Lite + 3 Light + DLight + DAC + Thermal Cam | LED array + box + nichrome wire + aperture | ~$100 |
| Infrastructure | 6 ATOM Lite (remote nodes) + 2 StickC (portable) + 3 PaHub2 + RTC + GNSS + cables | USB power + mounting | ~$200 |
| **TOTAL** | | | **~$950** |

---

## What This Lab Enables

### Continuous autonomous verification (24/7)
- ~80 of the 137 equations verified against live measurements
- Every experiment cycle produces a new data point in the ledger
- Drift detection: if equipment degrades, residuals trend upward
- Statistical power accumulates: 100+ cycles per equation per day

### Interactive learning sessions
- Student connects via makau.ai → station switches to learning mode
- Real physics happening in front of them, not a simulation
- Predictions vs measurements with immediate feedback
- Mastery tracking across all 7 makau.ai competency axes
- Station resumes auto-mode when student disconnects

### Novel prediction testing
- Station 4 (Fluid) + Station 5 (Optical) can test CMP-DARCY-RADPRESS-001
  by combining the porous sample with the LED/laser intensity control
  and the flow measurement. This is the experiment that would validate
  the first novel prediction from hequ.ai's discovery engine.

### Remote access
- Every station streams to makau.ai continuously
- Any station can be operated remotely via makau.ai's API
- Students don't need to be physically present
- hequ.ai's Cloud Function can trigger experiments programmatically
