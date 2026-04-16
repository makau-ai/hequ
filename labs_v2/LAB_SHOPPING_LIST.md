# hequ.ai Live Lab — M5Stack Shopping List v2

**Purpose:** Build a fully automated, self-resetting benchtop lab
that tests predictions from hequ.ai's 137-equation corpus 24/7
without human intervention.

**Constraint:** 100% M5Stack ecosystem for all electronics. Only
non-M5Stack items are passive physical materials (copper rod,
springs, tubing, etc.) that no electronics vendor sells.

**Architecture:** Each experiment station is an M5Stack controller
+ sensors + actuators, streaming to makau.ai via WiFi. The
orchestrator firmware runs a continuous loop:
set_conditions → wait_steady_state → measure → predict → verify → reset → repeat.

---

## Controllers

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 1 | M5Stack Core2 v1.1 | [Core2](https://shop.m5stack.com/products/m5stack-core2-esp32-iot-development-kit-v1-1) | 3 | $40 | $120 | Main experiment controllers. Touchscreen for local status, WiFi to makau.ai, I2C bus for sensors. One per experiment station. |
| 2 | ATOM Lite (ESP32-PICO) | [ATOM Lite](https://shop.m5stack.com/products/atom-lite-esp32-development-kit) | 6 | $8 | $48 | Dedicated single-sensor nodes. Deploy at remote measurement points (cold end of rod, ambient reference, outlet of tube). Tiny, battery-capable. |
| 3 | M5StickC Plus2 | [StickC Plus2](https://shop.m5stack.com/products/m5stickc-plus2-esp32-mini-iot-development-kit) | 2 | $20 | $40 | Portable handheld units with display. Use for field measurements, quick spot-checks, or as a mobile reference sensor. Built-in IMU + IR. |

**Subtotal: $208**

---

## Temperature Sensing (unlocks ~25 equations)

Equations: Fourier heat, Newton cooling, Arrhenius, Carnot, Stefan-Boltzmann, ideal gas, 1st/2nd law thermo, Gibbs, Clausius-Clapeyron, van der Waals, Soret, Dufour, Budyko, radiative forcing, all thermal composites.

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 4 | KMeter ISO Unit (MAX31855 thermocouple) | [KMeter ISO](https://shop.m5stack.com/products/kmeter-isolation-unit-with-thermocouple-temperature-sensor-max31855) | 4 | $10 | $40 | High-range thermocouple readers (-200°C to 1350°C chip, -50°C to 250°C probe). Two for Fourier rod ends, one for reaction vessel (Arrhenius), one for cooling body (Newton). 14-bit, I2C, galvanically isolated. |
| 5 | ENV Pro Unit (BME688: T+H+P+VOC) | [ENV Pro](https://shop.m5stack.com/products/env-pro-unit-with-temperature-humidity-pressure-and-gas-sensor-bme688) | 3 | $15 | $45 | All-in-one environmental: temperature, humidity, barometric pressure, VOC gas. Unlocks ideal gas (P,T simultaneously), Clausius-Clapeyron (vapor pressure), psychrometric equations, gas detection. Three units for multi-point environmental profiling. |
| 6 | Thermal Camera Unit (MLX90640) | [Thermal Cam](https://shop.m5stack.com/products/thermal-camera-unit-mlx90640) | 1 | $30 | $30 | 32×24 pixel thermal array. Visualizes temperature gradients along Fourier rod, radiation patterns (Stefan-Boltzmann), heat loss maps. Makes experiments publishable. |

**Subtotal: $115**

---

## Electrical Sensing (unlocks ~12 equations + all electromechanical composites)

Equations: Ohm, Kirchhoff, Faraday induction, Faraday electrolysis, Nernst, Coulomb (derived), DC motor composite, voice-coil composite, PID controller.

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 7 | Voltmeter Unit (ADS1115, ±36V) | [VMeter](https://shop.m5stack.com/products/voltmeter-unit-ads1115) | 3 | $8 | $24 | 16-bit voltage measurement. For Ohm (V across R), back-EMF (motor/voice-coil), Nernst cell potential, Kirchhoff loop voltages. I2C isolated. |
| 8 | Ammeter Unit (ADS1115, ±4A) | [AMeter](https://shop.m5stack.com/products/ammeter-unit-ads1115) | 3 | $8 | $24 | 16-bit current measurement. For Ohm (I through R), motor armature current, electrolysis current. 0.3mA resolution. |
| 9 | VAMeter (INA226, V+A+Power+Relay) | [VAMeter](https://shop.m5stack.com/products/m5stack-voltage-and-amperage-meter-with-m5stamps3) | 1 | $25 | $25 | Precision V+I+P with built-in relay + WiFi (StampS3). For automated power measurements: P_in = V·I vs P_mech + P_resist on motor/voice-coil composites. 2.5μA resolution. |
| 10 | ADC I2C Unit v1.1 (ADS1110) | [ADC Unit](https://shop.m5stack.com/products/adc-i2c-unit-v1-1-ads1100) | 2 | $5 | $10 | General-purpose 16-bit ADC for any analog sensor not in the M5Stack catalog (pH probe, photodiode, strain gauge). |

**Subtotal: $83**

---

## Motion / Force / Displacement Sensing (unlocks ~15 equations)

Equations: Newton F=ma, Hooke F=-kx, centripetal, work-energy, impulse-momentum, angular momentum, Stokes drag, SHO composite, Euler buckling, beam bending.

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 11 | 6-Axis IMU Unit (MPU6886) | [IMU Unit](https://shop.m5stack.com/products/6-axis-imu-unitmpu6886) | 3 | $5 | $15 | Accelerometer (±16g) + gyroscope (±2000°/s). Attach to spring-mass for SHO, pendulum for period, rotating body for ω. Three units: one on each moving body + one reference. |
| 12 | Accel Unit (ADXL345, ±16g) | [Accel](https://shop.m5stack.com/products/3-axis-digital-accelerometer-unit-adxl345) | 1 | $5 | $5 | High-precision accelerometer for Newton II (F=ma): apply known force, measure a, verify F/a = m. |
| 13 | ToF Distance Unit (VL53L0X) | [ToF](https://shop.m5stack.com/products/tof-sensor-unit) | 3 | $8 | $24 | Laser time-of-flight, 2m range, mm precision. Non-contact displacement for Hooke (spring stretch), beam deflection, pendulum amplitude. Three for multi-axis. |
| 14 | ToF 4M Unit (VL53L1X) | [ToF 4M](https://shop.m5stack.com/products/time-of-flight-distance-unit-vl53l1x) | 1 | $10 | $10 | Extended 4m range for longer-distance experiments (projectile, free fall, tube flow front tracking). |
| 15 | Ultrasonic Distance Unit I2C (RCWL-9620) | [Ultrasonic](https://shop.m5stack.com/products/ultrasonic-distance-unit-i2c-rcwl-9620) | 2 | $6 | $12 | 2cm–450cm range, ±2%. For larger displacement (Darcy flow front, spring oscillation at distance, fluid level in a tank). |
| 16 | Weight I2C Unit (HX711) | [Weight I2C](https://shop.m5stack.com/products/weight-i2c-unit-hx711) | 2 | $8 | $16 | 24-bit load cell amplifier. Direct force measurement for Hooke's law, beam loading, Stokes drag on a falling sphere, material testing (Hall-Petch, Griffith). |
| 17 | Scale Kit with Weight Unit | [Scale Kit](https://shop.m5stack.com/products/scale-kit-with-weight-unit) | 1 | $15 | $15 | Complete scale: 4 strain gauges + HX711 + platform. For mass measurement (Newton II, conservation of momentum, Arrhenius reactant mass). |
| 18 | Encoder Unit | [Encoder](https://shop.m5stack.com/products/encoder-unit) | 2 | $6 | $12 | Rotary encoder with push button. Measure shaft rotation (motor ω for DC motor composite), count oscillations (SHO period), or as a manual input dial for parameter adjustment. |

**Subtotal: $109**

---

## Pressure / Flow Sensing (unlocks ~10 equations + novel prediction)

Equations: ideal gas PV=nRT, Navier-Stokes, Bernoulli, Reynolds, Poiseuille, Darcy, Starling, Poiseuille blood-flow analog, CMP-DARCY-RADPRESS-001 (NOVEL).

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 19 | Tube Pressure Unit | [Tube Pressure](https://shop.m5stack.com/products/tube-air-pressure-unit) | 3 | $12 | $36 | Differential pressure, -100 to 200 kPa. For Poiseuille (ΔP across tube), Bernoulli (P along streamline), Darcy (pressure gradient in porous media). Three units for simultaneous multi-point pressure profiling. |
| 20 | Mini BPS Unit (QMP6988) | [Mini BPS](https://shop.m5stack.com/products/mini-bps-unit) | 2 | $5 | $10 | Barometric pressure for ideal gas law, altitude-pressure relationship, atmospheric Clausius-Clapeyron. Two for differential atmospheric measurements. |
| 21 | Water Flow Unit (hall-effect) | [Water Flow](https://shop.m5stack.com/products/water-flow-unit) | 2 | $8 | $16 | Flow rate measurement for Poiseuille (Q through known tube), Darcy (seepage velocity through porous sample). Two units: inlet + outlet for mass-balance check. |

**Subtotal: $62**

---

## Light / Optics Sensing (unlocks ~8 equations)

Equations: Stefan-Boltzmann, Planck radiation, Planck-Einstein, Snell's law, photoelectric, Beer-Lambert, CMP-DARCY-RADPRESS-001 (beam intensity I).

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 22 | Light Unit (photoresistor) | [Light](https://shop.m5stack.com/products/light-sensor-unit) | 3 | $3 | $9 | Basic light intensity. For Beer-Lambert (incident + transmitted + reference), inverse-square law, Weber-Fechner (psychophysics stimulus). |
| 23 | DLight Unit (BH1750, digital lux) | [DLight](https://shop.m5stack.com/products/dlight-unit-ambient-light-sensor-bh1750fvi-tr) | 2 | $5 | $10 | Calibrated digital lux meter for quantitative Beer-Lambert and illumination equations. More accurate than photoresistor. |
| 24 | Color Sensor Unit (TCS34725) | [Color](https://shop.m5stack.com/products/color-unit) | 1 | $5 | $5 | RGB + clear channel. Spectroscopic proxy: track color shift as concentration changes (Beer-Lambert at specific wavelengths). |

**Subtotal: $24**

---

## Chemistry / Environmental Sensing (unlocks ~12 equations)

Equations: Arrhenius, Henderson-Hasselbalch, Beer-Lambert, equilibrium constant, Raoult's law, Michaelis-Menten, logistic growth, Fick diffusion, CO₂ radiative forcing, Clausius-Clapeyron climate.

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 25 | CO2 Unit (SCD40) | [CO2](https://shop.m5stack.com/products/co2-unit-with-temperature-and-humidity-sensor-scd40) | 2 | $25 | $50 | CO₂ + T + humidity. For radiative forcing ΔF = 5.35·ln(C/C₀): seal a room, measure CO₂ buildup, verify logarithmic curve. Also reaction kinetics (CO₂ as product indicator). Two for differential. |
| 26 | Earth Moisture Unit | [Earth](https://shop.m5stack.com/products/earth-sensor-unit) | 2 | $3 | $6 | Soil moisture for Richards equation, Darcy in unsaturated media. Two for gradient measurement across a soil column. |
| 27 | MQ-5 Gas Unit (STM32G030) | [MQ-5 Gas](https://shop.m5stack.com/products/m5stack-mq-5-gas-unit-stm32g030) | 1 | $8 | $8 | Combustible gas detection for reaction kinetics monitoring, equilibrium constant (gas-phase), Arrhenius product evolution. |
| 28 | Hall Effect Unit (A3144E) | [Hall](https://shop.m5stack.com/products/hall-effect-unit-a3144e) | 2 | $3 | $6 | Magnetic field detection. For Faraday induction (detect rotating magnet), motor commutation timing, electromagnetic experiments. |

**Subtotal: $70**

---

## Actuators & Drivers (for FULL AUTOMATION — no human reset)

These are what make the lab self-resetting. Every manual action
(heating, releasing a spring, switching a circuit, pumping fluid)
is replaced by an electronically controlled actuator.

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 29 | GoPlus2 Module (2× DC motor + 4× servo) | [GoPlus2](https://shop.m5stack.com/products/goplus2-dc-motor-and-servo-driver-module-stm32f0) | 2 | $12 | $24 | Stackable on Core2. Drive DC motors (for motor/voice-coil composites) + servos (for automated spring compression, valve control, pendulum release). Two modules = 4 DC + 8 servo channels total. |
| 30 | 8-Channel Servo Driver Unit (STM32) | [8-Servo](https://shop.m5stack.com/products/8-channel-servo-driver-unit-stm32f030) | 1 | $8 | $8 | Extra servo channels for complex multi-actuator experiments. |
| 31 | H-Bridge Unit (STM32F030) | [H-Bridge](https://shop.m5stack.com/products/h-bridge-unitstm32f030) | 2 | $6 | $12 | Bidirectional DC motor control (forward/reverse/brake). For motor composite: programmatically set V_s, measure ω, reverse direction, measure again. Also drives Peltier elements for automated heating/cooling. |
| 32 | 4-Channel Relay Module v1.1 (STM32) | [4-Relay](https://shop.m5stack.com/products/4-channel-relay-13-2-module-v1-1-stm32f030) | 2 | $12 | $24 | Switch circuits on/off for automated Ohm's law cycling, Kirchhoff multi-loop switching, Faraday make/break. Four channels per module = 8 relay channels total. |
| 33 | BLDC Motor Driver Unit (STM32) | [BLDC Driver](https://shop.m5stack.com/products/bldc-motor-drive-unit-stm32) | 1 | $12 | $12 | Brushless motor driver for higher-speed/higher-precision motor experiments. PWM speed control + direction via I2C. |
| 34 | DAC 2 Unit (GP8413, 0-10V) | [DAC 2](https://shop.m5stack.com/products/dac-2-unit-gp8413) | 2 | $8 | $16 | Programmable voltage output. Generate controlled input signals: set V_s for motor, drive LED intensity for Beer-Lambert, generate PID controller setpoints. Two channels per unit. |
| 35 | Stepper Motor Driver Module (DRV8825) | [Stepmotor](https://shop.m5stack.com/products/stepmotor-driver-module-with-mega328p) | 1 | $12 | $12 | Precision linear positioning. Move a sensor along the Fourier rod to map the temperature profile point-by-point. Also: translate a weight along a beam for bending tests. |

**Subtotal: $108**

---

## Infrastructure & Connectivity

| # | Item | SKU / Link | Qty | ~$ ea | Total | Role |
|---|------|-----------|-----|-------|-------|------|
| 36 | PaHub2 (6-port I2C expander) | [PaHub2](https://shop.m5stack.com/products/pahub2-unit) | 3 | $5 | $15 | Expand I2C bus when running 8+ sensors on one controller. Each gives 6 ports. |
| 37 | RTC Unit (HYM8563) | [RTC](https://shop.m5stack.com/products/real-time-clock-rtc-unit-hym8563) | 2 | $5 | $10 | Accurate timestamps for time-dependent equations (radioactive decay, Newton cooling dT/dt, half-life). Battery-backed, survives power cycles. |
| 38 | GNSS Module (NEO-M9N + BMP280 + BMI270 + BMM150) | [GNSS Module](https://shop.m5stack.com/products/gnss-module-with-barometric-pressure-imu-magnetometer-sensors) | 1 | $45 | $45 | GPS + barometric pressure + IMU + magnetometer in one module. For geophysics: gravity variation with latitude, atmospheric pressure vs altitude, magnetic field experiments. |
| 39 | Mini Proto Board Unit | [Proto](https://shop.m5stack.com/products/mini-proto-board-unit) | 3 | $3 | $9 | General-purpose breakout for connecting passive components (resistors, springs, Peltier) to the M5Stack I2C/GPIO bus. |
| 40 | Grove-to-Pin Cable Pack | [Cables](https://shop.m5stack.com/products/grove-cable) | 5 packs | $3 | $15 | Connection cables for all units. |
| 41 | USB-C Power Cable | Standard | 6 | $3 | $18 | Power and programming for controllers. |
| 42 | 8-Encoder Unit (STM32) | [8-Encoder](https://shop.m5stack.com/products/8-encoder-unit-stm32f030) | 1 | $15 | $15 | 8 rotary encoders for multi-channel rotation sensing. For simultaneous shaft-speed measurement on multiple motors, or counting multiple oscillating systems. |

**Subtotal: $127**

---

## Passive Materials (the only non-M5Stack items)

| # | Item | Source | ~$ | Equations it enables |
|---|------|--------|-----|---------------------|
| 43 | Copper rod 30cm × 1cm | Hardware store | $5 | Fourier heat conduction |
| 44 | Aluminum rod 30cm × 1cm | Hardware store | $3 | Fourier (different k, validate scaling) |
| 45 | Spring assortment (3-5 springs, various k) | Amazon | $10 | Hooke's law, SHO composite |
| 46 | Known masses (50g, 100g, 200g, 500g, 1kg) | Amazon | $15 | Newton II, Hooke, work-energy, conservation of momentum |
| 47 | Resistor assortment (10Ω–10kΩ) | Electronics | $5 | Ohm's law, Kirchhoff, RC circuits |
| 48 | Small DC motor (with K spec on label) | Amazon | $5 | DC motor composite |
| 49 | Small speaker driver (with BL spec) | Amazon | $10 | Voice-coil composite |
| 50 | Peltier element (TEC1-12706) + heatsink | Amazon | $10 | Automated heating/cooling (replaces boiling water) |
| 51 | Clear silicone tubing (various ID) | Amazon | $8 | Poiseuille flow, Darcy porous media |
| 52 | Fine sand + glass bead packing | Hardware/Amazon | $8 | Darcy's law, CMP-DARCY-RADPRESS-001 |
| 53 | Glass cuvettes (4-pack) | Amazon | $10 | Beer-Lambert (optical path cell) |
| 54 | Food coloring / India ink | Grocery/Amazon | $5 | Beer-Lambert (absorber), Darcy+RadPress (dye) |
| 55 | Pendulum (string + steel ball) | DIY | $3 | Newton II pendulum period |
| 56 | Prism + lens | Amazon | $8 | Snell's law, refraction |
| 57 | Small peristaltic pump (12V) | Amazon | $12 | Automated fluid cycling for Darcy/Poiseuille experiments |
| 58 | Breadboard + jumper wires | Electronics | $8 | Circuit assembly |
| 59 | LED array (white + RGB, 12V) | Amazon | $8 | Controlled light source for Beer-Lambert, radiation |
| 60 | Small aquarium air pump | Amazon | $8 | Gas bubble experiments, pressure generation |

**Subtotal: $133**

---

## Grand Total

| Category | M5Stack items | Non-M5Stack | Cost |
|----------|--------------|-------------|------|
| Controllers | 11 units | — | $208 |
| Temperature | 8 units | — | $115 |
| Electrical | 9 units | — | $83 |
| Motion/Force | 16 units | — | $109 |
| Pressure/Flow | 7 units | — | $62 |
| Light/Optics | 6 units | — | $24 |
| Chemistry/Env | 7 units | — | $70 |
| Actuators/Drivers | 11 units | — | $108 |
| Infrastructure | ~20 items | — | $127 |
| Passive materials | — | 18 items | $133 |
| **TOTAL** | **~95 M5Stack items** | **18 passive items** | **~$1,039** |

---

## Equation Coverage (137 total)

| Category | Equations | Testable with this lab | Examples |
|----------|-----------|----------------------|----------|
| Classical mechanics | 10 | **10** | F=ma, Hooke, SHO, work-energy, pendulum, centripetal |
| Electromagnetism | 9 | **8** | Ohm, Kirchhoff, Faraday, Coulomb, Lorentz force, Biot-Savart |
| Thermodynamics | 10 | **10** | Ideal gas, 1st/2nd law, Carnot, Stefan-Boltzmann, Gibbs, Clausius-Clapeyron |
| Fluid dynamics | 5 | **5** | Navier-Stokes (Reynolds), Bernoulli, Poiseuille, Stokes drag, Darcy |
| Optics/radiation | 5 | **4** | Snell, Beer-Lambert, photoelectric, Planck (qualitative) |
| Quantum | 6 | **1** | Photoelectric (qualitative with light sensor) |
| Relativity/cosmo | 6 | **1** | Gravity variation with GPS altitude |
| Chemistry | 10 | **8** | Arrhenius, Nernst, Beer-Lambert, van der Waals, Faraday electrolysis |
| Biology | 10 | **6** | Fick diffusion, logistic growth (simulated), Michaelis-Menten (pH tracking) |
| Engineering | 8 | **8** | Fourier heat, PID, Kirchhoff, Euler buckling, beam bending, Nyquist |
| Medicine | 9 | **5** | Poiseuille (blood flow analog), Starling, half-life, BMI, Henderson-Hasselbalch |
| Environmental | 5 | **5** | CO₂ forcing, Darcy groundwater, Clausius-Clapeyron, Budyko |
| Materials | 3 | **2** | Hall-Petch (load+grain size), crack growth (fatigue cycling with servo) |
| Aerospace | 2 | **1** | Lift coefficient (tube pressure on airfoil) |
| **Verified composites** | 8 | **8** | ALL 8 composites testable (including CMP-DARCY-RADPRESS-001 novel) |
| | | | |
| CS/Math/Econ/Social/Linguistics/PoliSci | 38 | **2** | Weber-Fechner (light stimulus), Zipf (text corpus via makau.ai) |
| **TOTAL** | **137** | **~84** | |

---

## Automated Experiment Stations (3 stations, running 24/7)

### Station 1: Thermal (Core2 #1)
**Sensors:** 4× KMeter ISO, 2× ENV Pro, thermal camera
**Actuators:** H-Bridge driving Peltier, stepper for sensor positioning
**Experiments:** Fourier heat conduction, Newton cooling, Arrhenius
rate vs temperature, ideal gas P vs T, Carnot efficiency
**Cycle time:** ~5 min (heat up, stabilize, measure, cool down)

### Station 2: Electrical + Electromechanical (Core2 #2)
**Sensors:** 3× VMeter, 3× AMeter, VAMeter, 2× encoder, IMU
**Actuators:** GoPlus2 (motor + servo), 4-relay module, DAC
**Experiments:** Ohm's law, Kirchhoff loops, DC motor composite,
voice-coil composite, Faraday induction, PID controller
**Cycle time:** ~30 sec (switch circuit, measure, switch next)

### Station 3: Fluid + Optical + Chemical (Core2 #3)
**Sensors:** 3× tube pressure, 2× water flow, 2× light, DLight,
CO2, earth moisture, color sensor
**Actuators:** GoPlus2 (servo valves), DAC (LED intensity), relay (pump)
**Experiments:** Poiseuille flow, Darcy law, Beer-Lambert, CO₂
radiative forcing, Fick diffusion, Darcy+RadPress novel prediction
**Cycle time:** ~10 min (fill, stabilize, measure, drain)

### Remote Nodes (6× ATOM Lite + 2× StickC Plus2)
Placed at measurement points away from the stations: ambient
reference temperature, outdoor CO₂ baseline, secondary pressure
taps, flow outlet sensors. Stream independently to makau.ai.
