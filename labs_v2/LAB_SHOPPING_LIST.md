# hequ.ai Live Lab — M5Stack Shopping List

**Purpose:** Build a benchtop lab that can experimentally test
predictions from hequ.ai's 137-equation corpus. Every item maps
to specific equations it unlocks for live verification via the
makau.ai bridge.

**Philosophy:** Buy wide, not deep. One sensor per physical
quantity covers dozens of equations. The M5Stack ecosystem is
ideal because everything is I2C-pluggable, WiFi-native, and
~$10–$30 per unit.

---

## 1. Base Controllers (the brains)

| Item | M5Stack Product | Qty | ~Price | Why |
|------|----------------|-----|--------|-----|
| **M5Stack Core2** | [Core2 v1.1](https://shop.m5stack.com/products/m5stack-core2-esp32-iot-development-kit-v1-1) | 2 | $40 ea | Main controllers. Two units lets you run two experiments simultaneously or have one dedicated to data streaming while the other runs local display. ESP32, WiFi, Bluetooth, I2C, touchscreen, built-in IMU. |
| **M5StickC Plus2** | [StickC Plus2](https://shop.m5stack.com/products/m5stickc-plus2-esp32-mini-iot-development-kit) | 2 | $20 ea | Tiny, battery-powered, portable. Good for remote sensor placement (e.g., the "cold end" of a Fourier rod, or an outdoor temperature reference). Built-in IMU + IR transmitter. |
| **M5Stack ATOM Lite** | [ATOM Lite](https://shop.m5stack.com/products/atom-lite-esp32-development-kit) | 4 | $8 ea | Smallest ESP32 unit. Deploy as dedicated single-sensor nodes — one per sensor, streaming to makau.ai independently. Cheap enough to be disposable. |

**Subtotal: ~$152**

---

## 2. Temperature Sensors (unlock the most equations)

**Equations unlocked:** EQ-0005 (energy conservation), EQ-0020 (ideal gas PV=nRT), EQ-0021 (1st law thermo), EQ-0022 (2nd law entropy), EQ-0024 (Carnot η), EQ-0025 (Stefan-Boltzmann), EQ-0027 (Maxwell-Boltzmann), EQ-0028 (Gibbs free energy), EQ-0029 (Clausius-Clapeyron), EQ-0053 (Arrhenius), EQ-0057 (van der Waals), EQ-0088 (Fourier heat conduction), EQ-0089 (Newton cooling), EQ-0115 (radiative forcing), EQ-0117 (Clausius-Clapeyron climate), EQ-0118 (Budyko balance), EQ-0120 (half-life via T-dependent rates), CMP-FOURIER-FICK-SORET-001, CMP-FOURIER-FICK-DUFOUR-001

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **KMeter ISO Unit** (K-type thermocouple, MAX31855) | [KMeter ISO](https://shop.m5stack.com/products/kmeter-isolation-unit-with-thermocouple-temperature-sensor-max31855) | 3 | $10 ea | High-temp measurement (-50°C to 250°C probe, chip handles -200°C to 1350°C). For Fourier rod ends, Arrhenius reaction vessel, Carnot heat source/sink. 14-bit resolution, I2C. |
| **ENV Pro Unit** (BME688: T + humidity + pressure + VOC gas) | [ENV Pro](https://shop.m5stack.com/products/env-pro-unit-with-temperature-humidity-pressure-and-gas-sensor-bme688) | 2 | $15 ea | All-in-one environmental sensing. Unlocks ideal gas (P,T), Clausius-Clapeyron (vapor pressure vs T), Budyko (temperature balance), plus humidity for psychrometric equations. Also detects VOCs for air-quality equations. |
| **Thermal Camera Unit** (MLX90640) | [Thermal Camera](https://shop.m5stack.com/products/thermal-camera-unit-mlx90640) | 1 | $30 | 32×24 pixel thermal array. Visualizes temperature gradients along a conductor (Fourier), heat loss from a cooling body (Newton), radiation patterns (Stefan-Boltzmann). Not strictly needed but makes experiments visual and publishable. |

**Subtotal: ~$90**

---

## 3. Electrical Sensors (unlock circuit equations + all electromechanical composites)

**Equations unlocked:** EQ-0017 (Ohm V=IR), EQ-0013 (Faraday induction), EQ-0054 (Nernst), EQ-0062 (Faraday electrolysis), EQ-0086 (Kirchhoff), CMP-NEWTON-OHM-MOTOR-001 (DC motor), CMP-NEWTON-OHM-VOICECOIL-001 (voice coil)

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **Voltmeter Unit** (ADS1115, ±36V, 16-bit) | [VMeter](https://shop.m5stack.com/products/voltmeter-unit-ads1115) | 2 | $8 ea | Voltage measurement for Ohm's law, back-EMF in motors, Nernst cell potential. I2C isolated. |
| **Ammeter Unit** (ADS1115, ±4A, 16-bit) | [AMeter](https://shop.m5stack.com/products/ammeter-unit-ads1115) | 2 | $8 ea | Current measurement for Ohm's law, motor current, electrolysis current. 0.3mA resolution. |
| **VAMeter** (INA226, V+A+Power, relay) | [VAMeter](https://shop.m5stack.com/products/m5stack-voltage-and-amperage-meter-with-m5stamps3) | 1 | $25 | Precision V+I+P measurement with relay control. For DC motor composite verification: measure V_s, I, compute P_in = V·I, compare to P_mech + P_resist. 2.5μA resolution. |

**Subtotal: ~$57**

---

## 4. Motion / Force / Displacement Sensors (unlock mechanics)

**Equations unlocked:** EQ-0001 (Newton F=ma), EQ-0006 (Hooke F=-kx), EQ-0007 (centripetal a=v²/r), EQ-0008 (work-energy), EQ-0009 (impulse-momentum), EQ-0010 (angular momentum L=Iω), EQ-0045 (Stokes drag), EQ-0083 (Euler buckling), EQ-0085 (beam bending), EQ-0129 (Hall-Petch), CMP-NEWTON-HOOKE-SHO-001

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **6-Axis IMU Unit** (MPU6886) | [IMU Unit](https://shop.m5stack.com/products/6-axis-imu-unitmpu6886) | 2 | $5 ea | Accelerometer (±16g) + gyroscope (±2000°/s). Attach to a spring-mass system for SHO verification, to a pendulum for period measurement, to a rotating body for angular velocity. The Core2 has a built-in IMU but external units can be placed on the moving object. |
| **Accel Unit** (ADXL345, ±16g) | [Accel Unit](https://shop.m5stack.com/products/3-axis-digital-accelerometer-unit-adxl345) | 1 | $5 | Higher-precision 3-axis accelerometer. For Newton II (F=ma): apply a known force, measure acceleration, verify F/a = m. 13-bit resolution. |
| **Angle Sensor Unit** | [Angle Unit](https://shop.m5stack.com/products/angle-unit) | 1 | $5 | Rotary potentiometer. Measure angular displacement for pendulum, torsional oscillator, or any rotational equation. |
| **ToF Distance Unit** (VL53L0X) | [ToF Unit](https://shop.m5stack.com/products/tof-sensor-unit) | 2 | $8 ea | Laser time-of-flight distance sensor, 2m range, mm precision. Measure spring displacement (Hooke), beam deflection (Euler-Bernoulli bending), or pendulum amplitude. Non-contact, fast. |
| **Mini Weight Unit** (HX711 + load cell) | [Weight Unit](https://shop.m5stack.com/products/weight-unit-hx711) | 1 | $8 | Load cell for direct force measurement. Verify Hooke's law: hang known masses, measure force, plot F vs x from ToF. Also: beam bending loads, Stokes drag on a falling sphere. |
| **Vibration Sensor Unit** | [Vibration Unit](https://shop.m5stack.com/products/vibration-motor-unit) | 1 | $5 | Detect oscillation frequency. For SHO: measure the actual oscillation frequency and compare to predicted T = 2π√(m/k). |

**Subtotal: ~$54**

---

## 5. Pressure / Flow Sensors (unlock fluid dynamics + transport)

**Equations unlocked:** EQ-0020 (ideal gas PV=nRT), EQ-0041 (Navier-Stokes), EQ-0042 (Bernoulli), EQ-0043 (Reynolds number), EQ-0044 (Poiseuille), EQ-0116/EQ-0119 (Darcy), EQ-0122 (Starling capillary), EQ-0128 (Poiseuille blood flow), CMP-DARCY-RADPRESS-001 (novel prediction!)

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **Tube Pressure Unit** | [Tube Pressure](https://shop.m5stack.com/products/tube-air-pressure-unit) | 2 | $12 ea | Differential pressure sensor, -100 to 200 kPa. For Poiseuille (ΔP across a tube), Bernoulli (pressure along a streamline), Darcy (pressure gradient in porous media). Two units give you ΔP directly. |
| **Mini BPS Unit** (QMP6988 barometric) | [Mini BPS](https://shop.m5stack.com/products/mini-bps-unit) | 1 | $5 | Barometric pressure for ideal gas law, altitude equations, atmospheric Clausius-Clapeyron. |
| **Water Flow Unit** | [Water Flow](https://shop.m5stack.com/products/water-flow-unit) | 1 | $8 | Hall-effect flow sensor for pipe flow. For Poiseuille verification: measure Q through a known tube, compare to πr⁴ΔP/(8μL). |

**Subtotal: ~$37**

---

## 6. Light / Optics Sensors (unlock radiation + spectroscopy)

**Equations unlocked:** EQ-0025 (Stefan-Boltzmann j=σT⁴), EQ-0026 (Planck radiation), EQ-0034 (Planck-Einstein E=hν), EQ-0046 (Snell's law), EQ-0047 (photoelectric effect), EQ-0056 (Beer-Lambert A=εlc), CMP-DARCY-RADPRESS-001 (beam intensity I for the novel prediction)

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **Light Unit** (photoresistor) | [Light Unit](https://shop.m5stack.com/products/light-sensor-unit) | 2 | $3 ea | Basic light intensity measurement. For Beer-Lambert: measure transmitted intensity through a dye solution. For inverse-square law. Cheap enough to use in pairs (incident + transmitted). |
| **DLight Unit** (BH1750, digital lux) | [DLight Unit](https://shop.m5stack.com/products/dlight-unit-ambient-light-sensor-bh1750fvi-tr) | 1 | $5 | Calibrated digital lux meter. Better than photoresistor for quantitative Beer-Lambert and illumination equations. |
| **Laser TX/RX Unit** | [Laser Unit](https://shop.m5stack.com/products/laser-tx-unit) | 1 | $5 | Laser transmitter for optical path experiments: Beer-Lambert (attenuated beam through solution), Snell's law (refraction angle measurement). |
| **Color Sensor Unit** (TCS34725) | [Color Sensor](https://shop.m5stack.com/products/color-unit) | 1 | $5 | RGB + clear light sensing. For spectroscopic measurements: track color shift as a proxy for concentration change (Beer-Lambert at specific wavelengths). |

**Subtotal: ~$21**

---

## 7. Chemistry / Environmental Sensors (unlock chem + bio + environmental)

**Equations unlocked:** EQ-0053 (Arrhenius), EQ-0055 (Henderson-Hasselbalch pH), EQ-0056 (Beer-Lambert), EQ-0058 (equilibrium constant), EQ-0061 (Raoult's law), EQ-0063 (Michaelis-Menten), EQ-0065 (logistic growth), EQ-0068 (Fick diffusion), EQ-0115 (CO₂ radiative forcing), EQ-0117 (Clausius-Clapeyron climate)

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **CO2 Unit** (SCD40) | [CO2 Unit](https://shop.m5stack.com/products/co2-unit-with-temperature-and-humidity-sensor-scd40) | 1 | $25 | CO₂ concentration + T + humidity. For radiative forcing ΔF = 5.35·ln(C/C₀): measure indoor CO₂ buildup over time in a closed room, verify logarithmic relationship. Also: reaction kinetics (CO₂ as a product indicator). |
| **Earth Moisture Unit** | [Earth Unit](https://shop.m5stack.com/products/earth-sensor-unit) | 1 | $3 | Soil moisture for Richards equation (unsaturated soil hydraulics). Analog output proportional to water content. |
| **pH Sensor Unit** (if available, or use an external pH probe with ADC) | External probe + ADC Unit | 1 | $15 | For Henderson-Hasselbalch pH = pKa + log([A⁻]/[HA]). M5Stack doesn't have a dedicated pH unit; use an industrial pH probe connected via the ADC Unit. |
| **MQ Gas Sensor Unit** (various: MQ-2 smoke, MQ-5 combustible, MQ-135 air quality) | [MQ-5 Gas](https://shop.m5stack.com/products/m5stack-mq-5-gas-unit-stm32g030) | 1 | $8 | Gas concentration for reaction kinetics, Arrhenius (monitor reaction product gas evolution), equilibrium constant (gas-phase equilibria). |

**Subtotal: ~$51**

---

## 8. Actuators / Output Units (for controlled experiments)

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **DC Motor Driver Unit** | [Motor Driver](https://shop.m5stack.com/products/motor-driver-module) | 1 | $10 | Drive a DC motor for CMP-NEWTON-OHM-MOTOR-001 verification: control V_s, measure ω with encoder, verify ω = V_s/K - τ_L·R/K². |
| **Servo Unit** | [Servo Unit](https://shop.m5stack.com/products/servo-unit) | 2 | $4 ea | Controlled angular positioning. For pendulum release angle, beam loading position, or any experiment needing precise mechanical actuation. |
| **Relay Unit** | [Relay Unit](https://shop.m5stack.com/products/relay-unit) | 2 | $5 ea | Switch circuits on/off for transient experiments: Ohm's law step response, RC circuit charging (Kirchhoff), Faraday induction (make/break). |
| **DAC Unit** (GP8413) | [DAC Unit](https://shop.m5stack.com/products/dac-2-unit-gp8413) | 1 | $8 | Programmable voltage output (0-10V). Generate controlled input signals for PID controller verification (EQ-0084), transfer function testing. |

**Subtotal: ~$40**

---

## 9. Communication / Timing / Infrastructure

| Item | M5Stack Product | Qty | ~Price | Purpose |
|------|----------------|-----|--------|---------|
| **RTC Unit** (real-time clock) | [RTC Unit](https://shop.m5stack.com/products/real-time-clock-rtc-unit-hym8563) | 1 | $5 | Accurate timestamps for time-dependent equations: radioactive decay N(t)=N₀e^(-λt), Newton's cooling dT/dt, half-life t½. |
| **GPS Unit** | [GPS Unit](https://shop.m5stack.com/products/mini-gps-bds-unit-at6558) | 1 | $12 | Lat/lon/altitude for geophysics equations (gravity variation with latitude, atmospheric pressure vs altitude). Also provides precise UTC timestamps. |
| **Proto Board Unit** | [Proto Unit](https://shop.m5stack.com/products/mini-proto-board-unit) | 2 | $3 ea | General-purpose prototyping for connecting non-M5Stack sensors (pH probe, custom load cell, photodiode arrays). |
| **Hub Unit** (I2C port expander) | [PaHub2](https://shop.m5stack.com/products/pahub2-unit) | 2 | $5 ea | Expand I2C ports when running many sensors simultaneously. Each PaHub2 gives 6 additional I2C ports. |
| **Grove cables** | [Grove cables pack](https://shop.m5stack.com/products/grove-cable) | 3 packs | $3 ea | Connection cables for all units. |
| **USB-C cables** | Standard | 4 | $3 ea | Power and programming. |

**Subtotal: ~$56**

---

## 10. Experiment-Specific Additions (non-M5Stack, local hardware store)

| Item | Source | ~Price | Equations |
|------|--------|--------|-----------|
| Copper rod, 30cm × 1cm | Hardware store | $5 | Fourier heat conduction |
| Springs (assorted k values) | Amazon/hardware | $10 | Hooke's law, SHO |
| Known masses (50g, 100g, 200g, 500g) | Amazon | $15 | Newton II, Hooke, Work-Energy |
| Resistor assortment (100Ω–10kΩ) | Electronics supplier | $5 | Ohm's law, Kirchhoff |
| Small DC motor (with specs) | Amazon | $5 | DC motor composite |
| Small speaker driver (with BL spec) | Amazon | $10 | Voice-coil composite |
| Glass cuvettes + food coloring | Amazon | $10 | Beer-Lambert |
| Clear tubing + funnel | Hardware store | $5 | Poiseuille flow |
| Sand + container | Hardware store | $5 | Darcy's law |
| Pendulum (string + weight) | DIY | $2 | Newton II pendulum period |
| Magnifying lens / prism | Amazon | $8 | Snell's law |
| Styrofoam cup (calorimetry) | Kitchen | $0 | First law of thermodynamics |

**Subtotal: ~$80**

---

## Grand Total

| Category | Items | Cost |
|----------|-------|------|
| Base controllers | 8 units | $152 |
| Temperature | 6 units | $90 |
| Electrical | 5 units | $57 |
| Motion/Force | 9 units | $54 |
| Pressure/Flow | 4 units | $37 |
| Light/Optics | 5 units | $21 |
| Chemistry/Environment | 4 units | $51 |
| Actuators | 6 units | $40 |
| Infrastructure | ~12 items | $56 |
| Non-M5Stack lab supplies | ~12 items | $80 |
| **TOTAL** | **~71 items** | **~$638** |

---

## Equation Coverage Summary

With this lab kit, you can directly test predictions from
**~85 of the 137 equations** in the corpus:

| Discipline | Total equations | Testable | Key sensors needed |
|------------|----------------|----------|--------------------|
| Physics (mechanics) | 10 | 10 | IMU, ToF, weight, angle |
| Physics (E&M) | 9 | 7 | VMeter, AMeter, relay, motor |
| Physics (thermo) | 10 | 9 | KMeter, ENV Pro, tube pressure |
| Physics (fluids) | 5 | 5 | Tube pressure, water flow, ENV Pro |
| Physics (optics/radiation) | 5 | 4 | Light, DLight, laser, thermal cam |
| Physics (quantum) | 6 | 2 | Light (photoelectric qualitative), laser |
| Physics (relativity/cosmo) | 6 | 1 | GPS (gravity/altitude only) |
| Chemistry | 10 | 7 | KMeter, pH, CO2, light, VMeter |
| Biology & Biochemistry | 10 | 5 | KMeter, CO2, earth moisture, light |
| Engineering | 8 | 7 | VMeter, AMeter, DAC, servo, IMU |
| Medicine & Pharmacology | 9 | 4 | Tube pressure, KMeter, ENV Pro |
| Environmental & Earth Sci | 5 | 5 | CO2, ENV Pro, earth moisture, GPS |
| Materials Science | 3 | 2 | Weight, ToF (crack/deformation) |
| Aerospace | 2 | 1 | Tube pressure (lift measurement) |
| **Subtotal physical sciences** | **~98** | **~80** | |
| Computer Science | 9 | 0 | (computational, not physical) |
| Economics & Finance | 9 | 0 | (market data feeds, not sensors) |
| Social Sciences | 7 | 1 | Light (Weber-Fechner stimulus) |
| Mathematics | 9 | 0 | (pure math, not measurable) |
| Linguistics | 2 | 0 | (text corpus, not sensors) |
| Political Science | 2 | 0 | (voting data, not sensors) |
| **Subtotal non-physical** | **~38** | **~1** | |
| **GRAND TOTAL** | **137** | **~81** | |

The non-physical equations (economics, CS, linguistics, political
science) need DATA FEEDS not sensors — market APIs, text corpora,
voting records. Those connect through makau.ai's event and
knowledge-base APIs rather than through M5Stack hardware.

---

## First Three Experiments to Run (in order)

### Experiment 1: Fourier Heat Conduction
**Equipment:** Core2 + 2× KMeter ISO + copper rod + hot water
**Equation:** q = k·(T_hot − T_cold)/L
**What you verify:** linear temperature gradient at steady state
**Cost of just this experiment:** ~$60

### Experiment 2: Ohm's Law
**Equipment:** Core2 + VMeter + AMeter + 120Ω resistor + battery
**Equation:** V = I·R
**What you verify:** voltage and current readings satisfy V/I = R
**Cost of just this experiment:** ~$56

### Experiment 3: Simple Harmonic Oscillator (Newton+Hooke composite)
**Equipment:** Core2 + IMU (on mass) + spring + known mass
**Equation:** T = 2π√(m/k)
**What you verify:** measured period matches predicted from m and k
**Cost of just this experiment:** ~$50
