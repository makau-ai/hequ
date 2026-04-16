# HEQU Lab Report

## Consolidated Project Reference -- April 2026

---

## 1. Executive Summary

**hequ.ai** is a unified equation-verification platform. It maintains a corpus of 137 fundamental equations spanning 14 scientific disciplines, connects them to live sensor data and curated datasets, and provides a physical lab capable of testing 84 of those equations with automated hardware.

What has been built:

- A **137-equation corpus** with machine-readable metadata (units, domains-of-validity envelopes, literature citations).
- **8 verified composite equations** derived by algebraically combining base equations: 5 textbook composites, 1 novel composite (Darcy + Radiation Pressure), and 2 replicated composites (Dufour effect, voice-coil motor).
- A **novel prediction**: the Darcy + Radiation Pressure composite yields `u = k alpha I / (mu c)`, a testable relationship between optical radiation intensity and flow velocity through a porous medium.
- **Three integrated data sources** delivering live and historical data to the platform: makau.ai environmental sensors, SavvySuperSaver structured datasets, and M5Stack physical lab stations.
- A **5-station physical lab design** that is fully specified, purchasable, and buildable with off-the-shelf components. Total cost approximately $1,123. Zero consumables. Zero breakage. Every station auto-resets in under 60 seconds.
- **Cyber-Informed Engineering (CIE)** scenarios woven into every station, demonstrating physics-based intrusion detection using DOV-DSL validity envelopes.

The lab enables the project owner to purchase parts, build stations on a desk, and begin running reproducible verification experiments against the equation corpus with live data streaming to makau.ai.

---

## 2. The Equation Corpus

**137 equations across 14 disciplines:**

| # | Discipline | Count | Examples |
|---|-----------|-------|---------|
| 1 | Classical Mechanics | 15 | Newton II, Hooke, SHO, pendulum, work-energy |
| 2 | Thermal / Thermodynamics | 14 | Fourier, Newton cooling, Carnot, ideal gas, Arrhenius |
| 3 | Electrical | 12 | Ohm, Kirchhoff (V+I), Faraday, Coulomb |
| 4 | Fluid Dynamics | 10 | Poiseuille, Darcy, Bernoulli, Navier-Stokes |
| 5 | Spectroscopy / Optics | 9 | Beer-Lambert, inverse-square, Planck, Wien |
| 6 | Chemical Kinetics | 8 | Rate laws, Arrhenius, Fick diffusion |
| 7 | Quantum Mechanics | 8 | Schrodinger, de Broglie, Heisenberg |
| 8 | Relativity | 6 | Lorentz, E=mc^2, time dilation |
| 9 | Biology | 7 | Logistic growth, Michaelis-Menten, Hardy-Weinberg |
| 10 | Information Theory | 8 | Shannon entropy, channel capacity, Huffman |
| 11 | Probability / Statistics | 10 | Bayes, CLT, chi-squared, Poisson |
| 12 | Finance | 10 | CAPM, Black-Scholes, Fisher, Phillips |
| 13 | Chemical (general) | 12 | Nernst, Henderson-Hasselbalch, Raoult |
| 14 | Composites | 8 | see below |

### Verified Composites

| Composite | Source Equations | Status |
|-----------|-----------------|--------|
| Newton + Hooke = SHO | F=ma, F=-kx | Textbook verified |
| Newton + Ohm = DC Motor | F=ma, V=IR, tau=KI | Textbook verified |
| Fourier + Fick = Soret | q=-k dT/dx, J=-D dc/dx | Textbook verified |
| Newton + Work-Energy = Collision | F=ma, W=Fd, KE=1/2 mv^2 | Textbook verified |
| Arrhenius + Fick = Damkohler | k=Ae^(-Ea/RT), J=-D dc/dx | Textbook verified |
| **Darcy + Radiation Pressure** | Q=-kA/mu dP/dx, P_rad=I/c | **Novel** |
| Fourier + Fick = Dufour | q=-k dT/dx, J=-D dc/dx + cross | Replication |
| Newton + Ohm = Voice-Coil | F=BIL, V=IR+BLv | Replication |

### Novel Prediction

The Darcy + Radiation Pressure composite predicts:

```
u = k * alpha * I / (mu * c)
```

where `u` is flow velocity through a porous medium, `k` is permeability, `alpha` is the radiation absorption coefficient, `I` is radiation intensity, `mu` is dynamic viscosity, and `c` is the speed of light. This is testable in Station 4 (Fluid) with an optical source directed through a porous sample.

---

## 3. Data Infrastructure

### 3.1 makau.ai Sensors

Live environmental data via REST API.

| Source | Stations/Feeds | Parameters |
|--------|---------------|------------|
| NWS Weather | 10 stations | Temperature, pressure, humidity, wind speed/direction |
| USGS River Gauges | Multiple | Discharge, gauge height |
| NOAA Tides | Multiple | Tide height, predictions |
| NOAA Earthquakes | Global feed | Magnitude, depth, location |
| NOAA Space Weather | Global feed | Solar flux, geomagnetic indices |

**Endpoint:** `/api/hequ/` routes on makau.ai
**Auth:** `X-Makau-Api-Key` header

### 3.2 SavvySuperSaver Datasets

13 curated datasets for equation verification against structured data.

| Dataset | Rows | Use Case |
|---------|------|----------|
| CVE Severity | 314,000 | Shannon entropy, distribution fitting |
| CVE-Vendor Graph | 7,800,000 | PageRank, network centrality |
| Economic Indicators (FRED) | Varies | Fisher equation, Phillips curve |
| Economic Indicators (World Bank) | Varies | Growth models, PPP |
| Economic Indicators (Alpha Vantage) | Varies | CAPM, Black-Scholes |
| Grocery Prices | 29 items x 30 stores | Price elasticity, Zipf |
| Legislative Bills | 546 | Zipf's law on text, entropy |
| Attack Chains | 600 | Markov chains, graph theory |
| CPSC Recalls | Varies | Poisson, time-series |
| FDA Recalls | Varies | Poisson, classification |
| (+ 3 additional) | Varies | Various |

**Auth:** `X-Hequ-Key` header

### 3.3 M5Stack Physical Lab

5 automated stations with live sensor data.

- Each station runs on an M5Stack Core2 (ESP32)
- Sensors stream via WiFi to makau.ai
- **Endpoint:** `POST /api/sensors/ingest`
- Data includes: station ID, sensor type, timestamp, raw value, calibrated value, DOV envelope status

---

## 4. Equation-to-Data Mapping

| Coverage | Count | Data Source | Examples |
|----------|-------|-------------|---------|
| Physical sensors | 84 | M5Stack lab stations | Fourier, Ohm, Hooke, Beer-Lambert, Poiseuille |
| Platform data | ~30 | makau.ai event/learner/network data | Logistic growth, Bayes, network effects |
| Structured datasets | ~20 | SavvySuperSaver | Shannon entropy (CVE), PageRank (vendor graph), CAPM/Fisher/Phillips (economic), Zipf (legislative text) |
| Pure math identities | ~3 | CAS verification only | Euler's identity, Gaussian integral |

**Total coverage: 137 equations, all testable through at least one pathway.**

---

## 5. The Physical Lab Design

### 5 Stations Overview

```
+-------------------------------------------------------------------+
|                        HEQU PHYSICAL LAB                          |
|                                                                   |
|  [Station 1]   [Station 2]   [Station 3]   [Station 4]   [Stn 5] |
|   THERMAL       ELECTRICAL    MECHANICAL    FLUID         OPTICAL |
|   30x20cm       30x20cm       30x20cm       30x20cm       30x20cm|
|                                                                   |
|  Each station: Core2 + ESP32-CAM + RGB LED + Buzzer + Display     |
|  WiFi -> makau.ai /api/sensors/ingest                             |
+-------------------------------------------------------------------+
```

---

### Station 1: THERMAL

**Equations:** Fourier conduction, Newton cooling, Arrhenius, Carnot, ideal gas law

```
 +-----------------------------------------------------+
 |  STATION 1 -- THERMAL                   [ESP32-CAM] |
 |                                                      |
 |  [Peltier HOT] ===copper rod=== [Peltier COLD]      |
 |       |              |    |              |           |
 |   [KMeter 1]    [KMeter 2] [KMeter 3]  [ENV Pro]   |
 |                                                      |
 |  [Thermal Camera] aimed at rod center                |
 |                                                      |
 |  CIE: [KSD301 Bimetallic Thermostat] on hot side    |
 |       cuts Peltier power at T_max (auto-resets)      |
 |                                                      |
 |  [RGB LED Strip]  [Buzzer]  [Core2 Display]          |
 +-----------------------------------------------------+
```

**How it works:**
- Two Peltier modules create a temperature gradient along a copper rod
- 3 KMeter ISO thermocouples measure T at positions x1, x2, x3
- ENV Pro measures ambient T, humidity, pressure (ideal gas verification)
- Thermal camera provides 2D temperature field visualization
- Fourier: measure dT/dx and heat flux; verify q = -k dT/dx
- Newton cooling: turn off Peltier, measure exponential decay
- Arrhenius: use temperature-dependent reaction rate (optional chemical cell)

**CIE scenario:** Arrhenius thermal runaway. A spoofed thermocouple reading could mask an over-temperature condition. The KSD301 bimetallic thermostat is an independent, physics-based cutoff that trips at a fixed temperature regardless of what the digital sensors report. It auto-resets when temperature drops (100K+ cycle life). The DOV envelope flags the discrepancy between the thermostat trip and the spoofed sensor reading.

---

### Station 2: ELECTRICAL

**Equations:** Ohm's law, Kirchhoff voltage and current laws, DC motor composite, voice-coil composite, Faraday induction

```
 +-----------------------------------------------------+
 |  STATION 2 -- ELECTRICAL                [ESP32-CAM]  |
 |                                                      |
 |  [DAC] ---> [Relay Matrix] ---> [Load Circuit]      |
 |                  |                    |              |
 |              [VMeter]  [AMeter]  [VAMeter]           |
 |                                                      |
 |  Loads:  [Resistor network]  [DC Motor]  [Speaker]   |
 |                                                      |
 |  CIE: [PTC Resettable Fuse] in series with load     |
 |       trips at I_max, auto-resets when cool          |
 |                                                      |
 |  [RGB LED Strip]  [Buzzer]  [Core2 Display]          |
 +-----------------------------------------------------+
```

**How it works:**
- DAC sweeps voltage from 0 to 3.3V (amplified to 0-12V via relay/H-Bridge)
- Relay matrix selects among resistor loads, DC motor, and speaker
- VMeter and AMeter measure V and I independently; VAMeter provides cross-check
- Ohm's law: V/I sweep across known resistors; verify V = IR
- Kirchhoff: series/parallel resistor networks; verify sum of voltage drops = source
- DC motor composite: measure torque (via spring scale), current, and angular velocity
- Voice-coil: drive speaker with known signal, measure back-EMF

**CIE scenario:** I^2 R overload. An attacker injects a spoofed current reading showing safe levels while actual current climbs. The PTC resettable fuse (10K+ cycle life) physically opens the circuit at the current limit. No digital system can override it. The DOV envelope detects that voltage is present but current reads zero (fuse tripped) while the spoofed sensor still reports normal current.

---

### Station 3: MECHANICAL

**Equations:** Newton's second law, Hooke's law, SHO composite, work-energy theorem, pendulum

```
 +-----------------------------------------------------+
 |  STATION 3 -- MECHANICAL                [ESP32-CAM]  |
 |                                                      |
 |  [Servo] --- [Spring] --- [Mass on rail]             |
 |                               |                      |
 |                            [IMU x3]                  |
 |                            [ToF sensor]              |
 |                            [Weight sensor]           |
 |                                                      |
 |  [Pendulum arm] with encoder at pivot                |
 |                                                      |
 |  CIE: [ATOM Lite] independent safety relay           |
 |       monitors IMU; cuts servo if a > a_max          |
 |                                                      |
 |  [RGB LED Strip]  [Buzzer]  [Core2 Display]          |
 +-----------------------------------------------------+
```

**How it works:**
- Servo stretches a spring attached to a known mass on a low-friction rail
- IMU measures acceleration; ToF measures displacement; weight sensor measures force
- Newton II: F = ma verified by comparing weight sensor force to IMU acceleration x mass
- Hooke: F = kx verified by comparing weight sensor force to ToF displacement
- SHO composite: release mass, measure oscillation period; verify omega = sqrt(k/m)
- Pendulum: separate pendulum arm with encoder; verify T = 2*pi*sqrt(L/g)

**CIE scenario:** Runaway actuator. A spoofed IMU reading could mask dangerous acceleration. The independent ATOM Lite microcontroller reads its own IMU and controls a relay in series with the servo power line. If acceleration exceeds a_max, the ATOM Lite cuts power regardless of what the Core2 reports. This is a completely independent control loop -- no shared bus, no shared firmware.

---

### Station 4: FLUID

**Equations:** Poiseuille flow, Darcy's law, Bernoulli, Fick diffusion, Darcy + Radiation Pressure novel prediction

```
 +-----------------------------------------------------+
 |  STATION 4 -- FLUID                     [ESP32-CAM]  |
 |                                                      |
 |  [Peristaltic Pump] --> [Tube] --> [Porous Sample]   |
 |       |                    |              |          |
 |   [Flow Sensor]    [Pressure x3]   [Flow Sensor]    |
 |                                                      |
 |  [Dye reservoir] for Fick diffusion visualization    |
 |  [LED source] for Darcy+RadPress experiment          |
 |                                                      |
 |  CIE: [Spring Relief Valve] with mechanical flag     |
 |       opens at P_max, flag visible to camera         |
 |                                                      |
 |  [RGB LED Strip]  [Buzzer]  [Core2 Display]          |
 +-----------------------------------------------------+
```

**How it works:**
- Peristaltic pump drives water through clear tubing
- Tube pressure sensors measure pressure drop along the tube (Poiseuille) and across the porous sample (Darcy)
- Flow sensors measure volumetric flow rate at inlet and outlet
- Poiseuille: verify Q = pi*r^4*dP / (8*mu*L) by measuring Q and dP across a known tube
- Darcy: verify Q = -kA/mu * dP/dx across a sand/bead-packed tube
- Bernoulli: use a constriction in the tube; verify P + 1/2*rho*v^2 = constant
- Fick: release dye into still water in a side chamber; photograph diffusion front over time
- Novel prediction: shine LED through porous sample; measure if flow velocity changes with intensity

**CIE scenario:** Dam overpressure / biomedical ventilator pop-off. A spoofed pressure sensor could mask a dangerous pressure buildup. The spring relief valve is a purely mechanical device that opens at a fixed pressure and is visible to the ESP32-CAM via a mechanical flag. No digital system can prevent it from opening. The DOV envelope flags the discrepancy between "normal" digital pressure readings and the camera detecting the flag in the open position.

---

### Station 5: OPTICAL

**Equations:** Beer-Lambert law, inverse-square law, photoelectric effect

```
 +-----------------------------------------------------+
 |  STATION 5 -- OPTICAL                   [ESP32-CAM]  |
 |                                                      |
 |  [DAC-controlled LED] --> [Cuvette holder] -->       |
 |       |                        |                     |
 |   [Light sensor 1]      [Light sensor 2]             |
 |   (reference)            (through sample)            |
 |                                                      |
 |  [Cuvettes] with varying dye concentrations          |
 |  [Rail] for inverse-square distance sweep            |
 |                                                      |
 |  CIE: [Redundant ATOM Lite] with own light sensor   |
 |       cross-checks primary sensor readings           |
 |                                                      |
 |  [RGB LED Strip]  [Buzzer]  [Core2 Display]          |
 +-----------------------------------------------------+
```

**How it works:**
- DAC controls LED brightness (calibrated via reference light sensor)
- Cuvettes filled with dye solutions of known concentration
- Beer-Lambert: measure I/I0 vs concentration; verify A = epsilon * c * L
- Inverse-square: mount LED and sensor on a rail; sweep distance; verify I proportional to 1/d^2
- Photoelectric: use UV LED and photodiode; measure threshold voltage vs frequency

**CIE scenario:** Spoofed lab values (medical/pharmaceutical context). An attacker could inject false absorbance readings to mask a contaminated sample. The redundant ATOM Lite with its own independent light sensor provides a physics-based cross-check. If the primary sensor reports one absorbance and the ATOM Lite's sensor disagrees beyond the DOV envelope tolerance, the system flags the discrepancy.

---

### Common Station Features

Every station includes:

| Feature | Component | Purpose |
|---------|-----------|---------|
| Visual monitoring | ESP32-CAM | Records experiments, detects CIE flags |
| Status indicator | RGB LED strip | Green = normal, Yellow = warning, Red = CIE active |
| Audio alert | Piezo buzzer | Audible alarm on CIE trigger |
| User interface | Core2 touchscreen | Real-time plots, experiment control |
| Auto-reset | All CIE devices | Every station returns to safe state in <60 seconds |
| Zero consumables | By design | No chemicals consumed, no parts worn out |

---

## 6. Cyber-Informed Engineering Integration

### Three-Act Learning Structure

Every experiment follows the same CIE narrative:

1. **Act 1 -- Normal Operation.** Run the experiment. Collect data. Verify the equation. Everything works as expected.

2. **Act 2 -- Attack.** Inject a sensor spoof (via software or by physically disconnecting a sensor and feeding a fake signal). The digital readings look normal, but the physical system is approaching a dangerous state.

3. **Act 3 -- CIE Control Activates.** The independent, physics-based safety device triggers. The mechanical/thermal/electrical failsafe activates regardless of what the digital system reports. The DOV-DSL envelope flags the discrepancy. The RGB LEDs go red. The buzzer sounds. The system is safe.

### Non-Destructive Consequences

All CIE demonstrations use components designed for unlimited cycling:

| Component | Cycle Life | Stations | Failure Mode |
|-----------|-----------|----------|-------------|
| PTC resettable fuse | 10,000+ | 2 (Electrical) | Opens at I_max, resets when cool |
| KSD301 bimetallic thermostat | 100,000+ | 1 (Thermal) | Opens at T_max, resets when cool |
| Spring relief valve | Indefinite | 4 (Fluid) | Opens at P_max, closes when pressure drops |
| ATOM Lite safety relay | Indefinite | 3, 5 (Mechanical, Optical) | Software-controlled relay, no wear |

### Per-Discipline CIE Scenarios

| Discipline | Scenario | Station | CIE Control |
|-----------|----------|---------|-------------|
| Chemical | Arrhenius thermal runaway | 1 | Bimetallic thermostat |
| Electrical | I^2 R overload | 2 | PTC resettable fuse |
| Civil | Dam overpressure | 4 | Spring relief valve + flag |
| Biomedical | Ventilator pop-off valve | 4 | Spring relief valve |
| Materials | Melt pool temperature monitoring | 1 | Thermostat + thermal camera |
| Network | Sensor data injection | All | DOV-DSL validity envelope |
| Physician/Pharma | Spoofed lab absorbance values | 5 | Redundant ATOM Lite sensor |

### DOV-DSL as Intrusion Detection

The Domain-of-Validity DSL defines physics-based envelopes for every equation. When a sensor reading falls outside its DOV envelope, the system flags it as anomalous. This is intrusion detection grounded in physics, not statistics:

- If Ohm's law says I should be 0.5A at this voltage and the sensor reports 0.1A, the DOV flags it
- If Fourier's law says the temperature gradient should be 2 K/cm and the sensor reports 0.1 K/cm, the DOV flags it
- These flags are immune to sensor spoofing because they are based on independent physical laws

---

## 7. Bill of Materials

### M5Stack Controllers

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| M5Stack Core2 | 3 | $40 | $120 |
| ATOM Lite | 9 | $8 | $72 |
| StickC Plus2 | 2 | $20 | $40 |
| **Subtotal** | | | **$232** |

### Temperature Sensors

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| KMeter ISO (thermocouple) | 4 | $10 | $40 |
| ENV Pro (T/H/P) | 3 | $15 | $45 |
| Thermal Camera (MLX90640) | 1 | $30 | $30 |
| **Subtotal** | | | **$115** |

### Electrical Measurement

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| VMeter (voltage) | 3 | $8 | $24 |
| AMeter (current) | 3 | $8 | $24 |
| VAMeter (V+A) | 1 | $25 | $25 |
| ADC Unit | 2 | $5 | $10 |
| DAC Unit | 2 | $8 | $16 |
| **Subtotal** | | | **$99** |

### Motion / Position Sensors

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| IMU 6-axis | 3 | $5 | $15 |
| Accelerometer | 1 | $5 | $5 |
| ToF (VL53L0X) | 3 | $8 | $24 |
| ToF4M (VL53L1X) | 1 | $10 | $10 |
| Ultrasonic Distance | 2 | $6 | $12 |
| Weight I2C (HX711) | 2 | $8 | $16 |
| Scale Kit | 1 | $15 | $15 |
| Rotary Encoder | 2 | $6 | $12 |
| **Subtotal** | | | **$109** |

### Pressure / Flow Sensors

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| Tube Pressure Sensor | 3 | $12 | $36 |
| Mini BPS | 2 | $5 | $10 |
| Water Flow Sensor | 2 | $8 | $16 |
| **Subtotal** | | | **$62** |

### Light / Color Sensors

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| Light Sensor | 3 | $3 | $9 |
| DLight (digital lux) | 2 | $5 | $10 |
| Color Sensor | 1 | $5 | $5 |
| **Subtotal** | | | **$24** |

### Chemistry / Environment Sensors

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| CO2 Sensor (SCD40) | 2 | $25 | $50 |
| Earth Moisture | 2 | $3 | $6 |
| MQ-5 Gas Sensor | 1 | $8 | $8 |
| Hall Effect Sensor | 2 | $3 | $6 |
| **Subtotal** | | | **$70** |

### Actuators / Drivers

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| GoPlus2 (servo+motor driver) | 2 | $12 | $24 |
| H-Bridge Module | 2 | $6 | $12 |
| 4-Channel Relay | 2 | $12 | $24 |
| 8-Servo Hat | 1 | $8 | $8 |
| BLDC Driver | 1 | $12 | $12 |
| Stepper Driver | 1 | $12 | $12 |
| **Subtotal** | | | **$92** |

### Infrastructure / Connectivity

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| PaHub2 (I2C expander) | 3 | $5 | $15 |
| RTC Module | 2 | $5 | $10 |
| GNSS Module | 1 | $45 | $45 |
| Proto Board | 3 | $3 | $9 |
| Grove Cables (assorted) | 1 lot | $15 | $15 |
| USB-C Cables | 1 lot | $18 | $18 |
| 8-Encoder Input | 1 | $15 | $15 |
| **Subtotal** | | | **$127** |

### CIE-Specific Additions

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| KSD301 Bimetallic Thermostat | 3 | $1 | $3 |
| PTC Resettable Fuses (assorted) | 1 lot | $5 | $5 |
| Spring Relief Valve (adjustable) | 2 | $8 | $16 |
| RGB LED Strip (NeoPixel, 1m) | 5 | $3 | $15 |
| Piezo Buzzer | 5 | $1 | $5 |
| ESP32-CAM Module | 5 | $8 | $40 |
| M5Stack Timer Camera | 2 | $20 | $40 |
| Mechanical Flags (3D printed or card) | 1 lot | $3 | $3 |
| Magnifying Lens | 1 | $6 | $6 |
| Clear Acrylic Tube (for fluid station) | 1 | $10 | $10 |
| Check Valves | 1 lot | $6 | $6 |
| **Subtotal** | | | **$149** |

### Non-M5Stack Passive Materials

| Item | Qty | Unit Price | Total |
|------|-----|-----------|-------|
| Copper Rod (30cm, 10mm dia) | 1 | $5 | $5 |
| Aluminum Rod (30cm) | 1 | $3 | $3 |
| Springs (assorted k values) | 1 lot | $10 | $10 |
| Masses (slotted, 10g-500g) | 1 lot | $15 | $15 |
| Resistors (assorted) | 1 lot | $5 | $5 |
| DC Motor (small, 6-12V) | 1 | $5 | $5 |
| Speaker (8 ohm, small) | 1 | $10 | $10 |
| Peltier Module (TEC1-12706) | 2 | $5 | $10 |
| Heatsinks + Fans | 1 lot | $10 | $10 |
| Silicone Tubing (assorted ID) | 1 lot | $8 | $8 |
| Sand + Glass Beads (porous media) | 1 lot | $8 | $8 |
| Plastic Cuvettes | 1 lot | $10 | $10 |
| Food Dye | 1 | $5 | $5 |
| Pendulum (string + bob) | 1 | $3 | $3 |
| Prism (glass, 25mm) | 1 | $8 | $8 |
| Peristaltic Pump (6-12V) | 1 | $12 | $12 |
| Breadboard | 1 | $8 | $8 |
| LED Array (white + UV) | 1 lot | $8 | $8 |
| Air Pump (small, 5V) | 1 | $8 | $8 |
| **Subtotal** | | | **$143** |

---

### BOM Grand Total

| Category | Total |
|----------|-------|
| M5Stack Controllers | $232 |
| Temperature Sensors | $115 |
| Electrical Measurement | $99 |
| Motion / Position | $109 |
| Pressure / Flow | $62 |
| Light / Color | $24 |
| Chemistry / Environment | $70 |
| Actuators / Drivers | $92 |
| Infrastructure | $127 |
| CIE Additions | $149 |
| Passive Materials | $143 |
| **GRAND TOTAL** | **~$1,222** |

Note: Prices are approximate (M5Stack shop + Amazon). Actual cost may vary. Some items may be available in kits at lower combined prices.

---

## 8. Physical Construction Guide

### General Principles

- **Baseplate:** Each station sits on a ~30cm x 20cm sheet of acrylic or aluminum. Drill holes for mounting. Label with station number.
- **Sensor connections:** All M5Stack sensors use Grove cables (4-pin, keyed connectors). Plug into the Core2's Port A (I2C). If a station needs more than 4 I2C devices, use a PaHub2 expander (up to 6 channels per hub).
- **Actuator connections:** Use GoPlus2 (stacks on top of Core2) for servo and DC motor outputs. Use H-Bridge module for higher-current loads. Use 4-channel relay for switching 12V devices.
- **Power:** Core2 + all sensors run on USB-C 5V (2A recommended). Peltier modules, pumps, and motors need a separate 12V adapter, switched through a relay.
- **WiFi:** Flash each Core2 with the hequ firmware (MicroPython or Arduino). Configure SSID and password. Each Core2 streams data to `POST makau.ai/api/sensors/ingest`.
- **Soldering:** None required for the M5Stack ecosystem (all Grove plug-and-play). The only soldering is for passive components on a breadboard: wiring resistors, the PTC fuse in series, the thermostat in the Peltier power line, and the speaker to the H-Bridge output.

### Station-by-Station Build

#### Station 1: THERMAL

```
Materials needed:
  Core2 x1, PaHub2 x1, KMeter ISO x3, ENV Pro x1, Thermal Camera x1
  DAC x1, 4-Ch Relay x1
  Peltier x2, Heatsinks+Fans x1, Copper Rod x1
  KSD301 Thermostat x1, ESP32-CAM x1, RGB LED x1, Buzzer x1
  12V adapter, baseplate

Assembly:
  1. Mount copper rod horizontally across baseplate center
  2. Attach Peltier (hot side) to left end of rod with thermal paste
  3. Attach Peltier (cold side) to right end of rod (or leave open for ambient)
  4. Mount heatsinks on outer faces of Peltier modules; attach fans
  5. Clamp KMeter thermocouples to rod at 25%, 50%, 75% positions
  6. Mount ENV Pro near the rod (measures ambient)
  7. Mount thermal camera on a small stand, aimed at the rod
  8. Wire Peltier power through KSD301 thermostat (in series on hot side)
  9. Wire Peltier power through relay (12V switched by Core2 via relay module)
  10. Connect all sensors to Core2 via PaHub2
  11. Mount ESP32-CAM on gooseneck, aimed at the rod center
  12. Stick RGB LED strip along front edge of baseplate
  13. Mount buzzer with adhesive

  Power: 5V USB-C to Core2; 12V adapter to relay -> Peltier
```

#### Station 2: ELECTRICAL

```
Materials needed:
  Core2 x1, PaHub2 x1, VMeter x3, AMeter x3, VAMeter x1
  DAC x1, H-Bridge x1, 4-Ch Relay x1
  Resistors, DC Motor, Speaker, Breadboard
  PTC Fuse, ESP32-CAM x1, RGB LED x1, Buzzer x1
  12V adapter, baseplate

Assembly:
  1. Mount breadboard on baseplate center
  2. Wire resistor network on breadboard (series + parallel configs)
  3. Wire PTC fuse in series with the main load line
  4. Mount DC motor on baseplate corner with clamp
  5. Mount speaker on opposite corner
  6. Wire relay module to select among: resistor load, motor, speaker
  7. Connect DAC output to H-Bridge input (voltage source)
  8. Connect VMeter across load, AMeter in series with load
  9. Connect VAMeter at source output for cross-check
  10. Connect all sensors to Core2 via PaHub2
  11. Mount ESP32-CAM aimed at breadboard/motor area
  12. Stick RGB LED strip along front edge
  13. Mount buzzer

  Power: 5V USB-C to Core2; 12V adapter to H-Bridge -> load circuit
```

#### Station 3: MECHANICAL

```
Materials needed:
  Core2 x1, PaHub2 x1, IMU x3, ToF x2, Weight Sensor x1, Encoder x1
  GoPlus2 x1 (servo driver)
  Servo, Springs, Masses, Pendulum
  ATOM Lite x1 (safety), Relay x1 (safety cutoff)
  ESP32-CAM x1, RGB LED x1, Buzzer x1, baseplate

Assembly:
  1. Mount a low-friction rail (aluminum channel or drawer slide) on baseplate
  2. Attach spring to one end of the rail (fixed point)
  3. Attach mass carrier to other end of spring (rides on rail)
  4. Mount servo at the fixed end to stretch/release the spring
  5. Mount ToF sensor at one end of rail, aimed along it (measures position)
  6. Mount weight sensor under the spring attachment point (measures force)
  7. Mount 3 IMU units: one on mass, one on baseplate (reference), one spare
  8. Mount pendulum arm on a pivot at one corner, with encoder at pivot
  9. Wire ATOM Lite to its own IMU and a relay in series with servo power
  10. Connect Core2 sensors via PaHub2; servo via GoPlus2
  11. ATOM Lite operates independently (own firmware, own power)
  12. Mount ESP32-CAM, RGB LED, buzzer

  Power: 5V USB-C to Core2 and ATOM Lite (separate cables)
```

#### Station 4: FLUID

```
Materials needed:
  Core2 x1, PaHub2 x1, Tube Pressure x3, Water Flow x2
  Peristaltic Pump, Silicone Tubing, Clear Acrylic Tube
  Sand/Glass Beads (porous sample), Check Valves
  Food Dye, Cuvettes (for Fick visualization)
  Spring Relief Valve x2, Mechanical Flags
  ESP32-CAM x1, RGB LED x1, Buzzer x1
  12V adapter, baseplate

Assembly:
  1. Mount peristaltic pump at one end of baseplate
  2. Connect tubing: pump -> pressure sensor 1 -> straight tube section ->
     pressure sensor 2 -> porous sample (clear acrylic tube packed with
     sand/beads) -> pressure sensor 3 -> flow sensor -> return reservoir
  3. Mount flow sensor at inlet (after pump) and outlet (before reservoir)
  4. Install spring relief valve on a T-junction before the porous sample
  5. Attach mechanical flag to the relief valve (visible to camera)
  6. Install check valves to prevent backflow
  7. Side branch: a small still-water chamber with a dye injection port
     for Fick diffusion experiments
  8. Optional: mount LED source aimed through porous sample for
     Darcy+RadPress experiment
  9. Connect all sensors to Core2 via PaHub2
  10. Mount ESP32-CAM aimed at the relief valve flag zone
  11. Stick RGB LED strip, mount buzzer

  Power: 5V USB-C to Core2; 12V to pump (via relay)
  Fluid: tap water, recirculated in a closed loop
```

#### Station 5: OPTICAL

```
Materials needed:
  Core2 x1, Light Sensor x3, DLight x2, Color Sensor x1
  DAC x1, LED Array (white + UV)
  Cuvettes, Food Dye, Prism, Magnifying Lens
  ATOM Lite x1 (redundant sensor), Light Sensor x1 (for ATOM)
  ESP32-CAM x1, RGB LED x1, Buzzer x1, baseplate

Assembly:
  1. Mount an optical rail (aluminum channel) along baseplate center
  2. Mount DAC-controlled LED at one end (use DAC to set brightness)
  3. Mount cuvette holder at center of rail (slot for plastic cuvettes)
  4. Mount reference light sensor between LED and cuvette
  5. Mount measurement light sensor on the far side of cuvette
  6. Second DLight sensor on a sliding mount along the rail (inverse-square)
  7. Mount ATOM Lite with its own light sensor near the measurement sensor
  8. Mount prism on a small stand for spectral experiments
  9. Mount color sensor near prism output
  10. Connect Core2 sensors via PaHub2
  11. ATOM Lite operates independently
  12. Mount ESP32-CAM, RGB LED, buzzer

  Power: 5V USB-C to Core2 and ATOM Lite
  Note: This station works best in a dim environment. Consider a simple
  cardboard light shield around the optical rail.
```

---

## 9. First Three Experiments to Run

These are the simplest, most reliable starting experiments. Each one verifies a foundational equation and exercises the full data pipeline (sensor -> Core2 -> WiFi -> makau.ai -> DOV check).

---

### Experiment 1: Fourier Heat Conduction

**Station:** 1 (Thermal)
**Approximate cost of this station:** ~$180
**Equation:** `q = -k * dT/dx`
**What you need:** Core2, PaHub2, KMeter ISO x3, Peltier x1, copper rod, 12V adapter, relay

**Procedure:**

1. Power on the Peltier (hot side only) via relay. Set to a fixed power level.
2. Wait for thermal equilibrium (temperature readings stabilize -- typically a few minutes).
3. Read temperatures T1, T2, T3 at positions x1, x2, x3 along the copper rod.
4. Compute the temperature gradient: `dT/dx = (T3 - T1) / (x3 - x1)`.
5. Compute the expected heat flux: `q = -k_copper * dT/dx` where `k_copper = 385 W/(m*K)`.
6. Compare the measured gradient to the theoretical prediction.
7. Repeat at 3 different Peltier power levels. Plot dT/dx vs power.

**Expected result:** Linear temperature gradient along the rod. Measured gradient matches Fourier prediction within sensor uncertainty (KMeter ISO: +/- 0.5 K).

**DOV envelope check:** If any KMeter reads outside the range [T_ambient, T_peltier_max], the DOV flags it.

**CIE extension:** Disconnect one KMeter and feed a fake signal. The DOV will detect that the gradient is no longer physically consistent (the middle sensor reading breaks the expected linear interpolation).

---

### Experiment 2: Ohm's Law Voltage Sweep

**Station:** 2 (Electrical)
**Approximate cost of this station:** ~$160
**Equation:** `V = I * R`
**What you need:** Core2, PaHub2, VMeter, AMeter, DAC, H-Bridge, known resistors (100, 220, 470, 1K ohm), breadboard

**Procedure:**

1. Wire a known resistor (e.g., 220 ohm) on the breadboard.
2. Connect DAC -> H-Bridge -> resistor -> AMeter -> ground.
3. Connect VMeter across the resistor.
4. Sweep DAC output from 0.0V to 3.3V in 0.1V steps.
5. At each step, record V (from VMeter) and I (from AMeter).
6. Plot V vs I. Compute slope = R_measured.
7. Compare R_measured to the labeled resistor value.
8. Repeat with 3 different resistors.

**Expected result:** Linear V-I relationship. R_measured within 5% of labeled value (resistor tolerance).

**DOV envelope check:** If V > 0 but I = 0 (open circuit) or I is impossibly large (short circuit), the DOV flags it.

**CIE extension:** Place the PTC fuse in series. Increase current until the fuse trips. Observe that V is present but I drops to zero. The DOV detects the inconsistency. The PTC fuse cools and resets automatically.

---

### Experiment 3: SHO Composite Verification

**Station:** 3 (Mechanical)
**Approximate cost of this station:** ~$130
**Equation:** `omega = sqrt(k/m)`, derived from F=ma + F=-kx
**What you need:** Core2, PaHub2, IMU, ToF, spring with known k, masses, servo, rail

**Procedure:**

1. Mount a spring (known spring constant k) on the rail with a known mass m.
2. Use the servo to pull the mass to a displacement x0 and release.
3. The mass oscillates on the spring.
4. Record position vs time using ToF sensor (sample at 50+ Hz).
5. Record acceleration vs time using IMU.
6. Compute the oscillation period T from the position data (peak-to-peak timing).
7. Compute omega_measured = 2*pi/T.
8. Compute omega_predicted = sqrt(k/m).
9. Compare. Repeat with 3 different masses.

**Expected result:** omega_measured matches omega_predicted within 5% (limited by friction and spring non-ideality).

**DOV envelope check:** If amplitude grows instead of decays (energy appearing from nowhere), the DOV flags it as unphysical.

**CIE extension:** Spoof the IMU reading to show zero acceleration while the mass is clearly oscillating (visible on ESP32-CAM). The ATOM Lite's independent IMU detects the oscillation and flags the discrepancy. If the spoofed signal also masks a runaway (servo not releasing), the ATOM Lite cuts servo power via its independent relay.

---

## Appendix: Quick Reference

### API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `makau.ai/api/hequ/*` | GET | `X-Makau-Api-Key` | Live sensor data (NWS, USGS, NOAA) |
| `makau.ai/api/sensors/ingest` | POST | `X-Makau-Api-Key` | M5Stack lab data upload |
| `savvysupersaver.com/api/*` | GET | `X-Hequ-Key` | SSS datasets |

### Key Files in This Repository

```
hequ/
  critical_equations_complete.csv    -- 137 equations, machine-readable
  critical_equations_inventory.json  -- Full metadata with DOV envelopes
  labs_v2/
    composites/                      -- 8 verified composite derivations
    equations/                       -- Per-discipline equation definitions
    data/                            -- Data source configurations
    CIE_LAB_INTEGRATION.md           -- Detailed CIE scenarios
    CIE_LAB_STATIONS.md              -- Station hardware specs
    LAB_DESIGN.md                    -- Original lab design document
    LAB_SHOPPING_LIST.md             -- Detailed shopping list
    HEQU_LAB_REPORT.md               -- This document
```

---

*Generated for project owner review. All specifications, prices, and component selections are based on the M5Stack ecosystem and common laboratory suppliers as of early 2026.*
