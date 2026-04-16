# CIE Lab Stations — Non-Destructive, Auto-Resetting, Camera-Monitored

**Design rule:** every consequence is VISIBLE and DRAMATIC but
NOTHING BREAKS. Every station returns to baseline automatically
in under 60 seconds. Every consequence is captured on camera
and by sensors. Infinite cycles, zero consumables, zero
human intervention.

**Key components for non-destructive consequences:**
- PTC resettable fuses (polyfuses) — trip on overcurrent, auto-reset on cooling
- Spring-loaded check valves — open at cracking pressure, close when pressure drops
- Bimetallic snap-action thermostats — click open at T_max, click closed on cooling
- LED indicator strips (green → yellow → red) — visible state progression
- Piezo buzzers — audible alarm at consequence
- Small flags/ribbons at exhaust ports — flutter visibly when valve opens
- ESP32-CAM or M5Stack Timer Camera — captures the moment on video
- M5Stack screen — shows live equation state, flashes red at consequence

---

## Station 1: THERMAL CIE — "The Runaway Reaction"

### What the student sees
A copper rod with a glowing LED strip along its length. As the
"reactor" (Peltier-heated end) overheats, the LEDs shift from
green → yellow → red. A "spoofed" temperature reading on the
screen shows "SAFE" even as the thermal camera shows the real
temperature climbing. Then — CLICK — the bimetallic thermostat
trips, the Peltier power cuts, a buzzer sounds, the screen
flashes "PHYSICAL SAFETY TRIP — CIE CONTROL ACTIVATED." The
thermal camera shows the hot spot cooling down. After 30 seconds,
the thermostat resets (another click), and the cycle restarts.

### How it works (non-destructive)
```
[Peltier] ─── [bimetallic thermostat KSD301, 70°C] ─── [relay] ─── [power]
    │                        │
    │                   (CLICKS OPEN at 70°C,
    │                    auto-resets at ~55°C)
    │
  [copper rod with adhesive RGB LED strip]
    │
  [KMeter #1: real T]  [KMeter #2: real T]
    │
  [thermal camera: visual gradient]
    │
  [ESP32-CAM: records the event]
```

### Components (all M5Stack + commodity)
| Part | Source | Purpose |
|------|--------|---------|
| KSD301 bimetallic thermostat (70°C NC) | Amazon ~$3 | Auto-resetting thermal cutout. Normally-closed, snaps open at 70°C, re-closes at ~55°C. Infinite cycles. |
| WS2812 RGB LED strip (30cm, adhesive) | Amazon ~$5 | Visual temperature gradient along the rod: green (cold) → red (hot). Driven by Core2 GPIO. |
| Piezo buzzer | M5Stack or Amazon ~$2 | Audible alarm when thermostat trips |
| ESP32-CAM module | Amazon ~$8 | Captures video of the thermal event. Streams to makau.ai. |
| Peltier TEC1-12706 | Amazon ~$5 | Heat source (max ~80°C on hot side with heatsink) |

### Auto-reset sequence
```
NORMAL:    Thermostat closed → Peltier heating → LEDs shift green→red → 70°C
TRIP:      Thermostat opens (click) → Peltier off → buzzer → screen RED
COOLING:   T drops naturally → LEDs shift red→green → ~55°C
RESET:     Thermostat closes (click) → buzzer off → screen GREEN
DURATION:  Trip-to-reset ≈ 30-45 seconds (copper rod thermal mass)
```

### CIE lesson demonstrated
The software controller was "compromised" — it commanded the
Peltier to keep heating even past the safe limit, and it reported
"safe" temperatures to the dashboard. But the bimetallic
thermostat doesn't read the software. It reads PHYSICS (thermal
expansion of a bimetal strip). When the real temperature hit 70°C,
the thermostat clicked open regardless of what the software said.
The equation governing the thermostat (differential thermal
expansion: Δl = α·l·ΔT) IS the safety system.

---

## Station 2: ELECTRICAL CIE — "The Overcurrent Fuse"

### What the student sees
A circuit board with a glowing LED (the "load"), an ammeter
display on the M5Stack screen showing current, and a small
PTC resettable fuse visible under a magnifier. As the software
"attack" increases current beyond the safe limit, the ammeter
climbs, the LED strip turns yellow then red. Then — the PTC
trips. The load LED goes dark. The ammeter drops to near-zero.
Buzzer sounds: "FUSE TRIPPED — CIE CONTROL." After 15 seconds,
the PTC cools and resets. The load LED re-lights. Cycle repeats.

### How it works (non-destructive)
```
[DAC output] ─── [PTC resettable fuse 500mA] ─── [load LED] ─── [GND]
                        │                              │
                   (trips at ~500mA,                   │
                    resets after cooling)               │
                        │                              │
                   [AMeter reads current]          [VMeter reads V_load]
                        │
                   [RGB LED strip: current level indicator]
                        │
                   [ESP32-CAM focused on PTC fuse]
```

### Components
| Part | Source | Purpose |
|------|--------|---------|
| PTC resettable fuse (500mA, 16V) | Amazon ~$5/pack of 10 | Polyfuse — trips on overcurrent, auto-resets when cool. Rated for 10,000+ cycles. |
| High-brightness LED (load indicator) | Amazon ~$2 | Visual "load" that goes dark when fuse trips |
| Magnifying lens (mounted over PTC) | Amazon ~$3 | So student/camera can see the tiny fuse |

### Auto-reset sequence
```
NORMAL:    DAC drives 200mA → LED bright → ammeter shows 200mA → GREEN
ATTACK:    Software ramps DAC → 300mA → 400mA → 500mA → YELLOW → RED
TRIP:      PTC resistance jumps → current drops to ~10mA → LED dark → BUZZER
COOLING:   PTC cools (no current flowing) → ~15 seconds
RESET:     PTC resistance drops → DAC can drive current again → LED relights
DURATION:  Trip-to-reset ≈ 15-20 seconds
```

### CIE lesson demonstrated
The software commanded ever-increasing current (simulating a
compromised PLC that overloads a transformer). The PTC fuse
has a physical property: above its Curie temperature (caused by
I²R self-heating at overcurrent), the polymer matrix expands
and breaks the conductive particle chains. This is Ohm's law
(I²R heating) combined with a phase transition — pure physics,
no software involved. The fuse "knows" the current is too high
because the current itself heats the fuse material.

---

## Station 3: MECHANICAL CIE — "The Overspeed Governor"

### What the student sees
A small DC motor spinning a disk with reflective tape (for
optical RPM measurement). As the software "attack" increases
the voltage, the motor speeds up. An LED strip around the disk
enclosure shifts green → yellow → red. At a critical speed,
a mechanical centrifugal brake engages — two weighted arms
swing outward and contact a friction ring, slowing the motor.
The camera captures the arms deploying. Buzzer sounds. When
the software reduces voltage, the arms retract (spring-loaded),
and the motor resumes normal speed.

### Simpler alternative (no custom centrifugal brake)
Use the GoPlus2 motor driver's BUILT-IN current limit. When the
motor draws too much current at high speed under load, the
H-bridge driver's thermal protection kicks in and reduces the
drive. The consequence is visible: motor speed drops despite
increasing voltage command. Even simpler: a software watchdog
on the encoder that commands the relay to cut motor power
when RPM exceeds threshold — but make the watchdog run on
a SEPARATE ATOM Lite (simulating an independent analog safety
system) so it's physically independent of the compromised
Core2.

```
[Core2 — "compromised" controller]
    │
    ├── [DAC → motor voltage (increasing)]
    │
    ├── [Encoder reads RPM] ──→ [display: RPM climbing]
    │
[ATOM Lite — independent safety monitor]
    │
    ├── [Encoder reads same RPM independently]
    │
    └── [Relay cuts motor power if RPM > threshold]
         │
         └── [Buzzer + RED LED: "OVERSPEED TRIP"]
```

### Components
| Part | Source | Purpose |
|------|--------|---------|
| ATOM Lite | M5Stack $8 | Independent safety monitor (separate from "compromised" Core2) |
| Relay Unit | M5Stack $5 | Physical power cutoff for motor |
| Encoder Unit | M5Stack $6 | RPM measurement (fed to both Core2 and ATOM) |
| DC motor + disk | Amazon $5 | The rotating system |
| RGB LED ring | Amazon $5 | Visual speed indicator around the disk |

### Auto-reset sequence
```
NORMAL:    Core2 drives motor at 3V → 1000 RPM → GREEN
ATTACK:    Core2 ramps to 5V → 7V → 9V → RPM climbs → YELLOW → RED
TRIP:      ATOM Lite sees RPM > threshold → relay OPENS → motor coasts down → BUZZER
COOLDOWN:  Motor speed drops below threshold
RESET:     ATOM Lite closes relay → Core2 can drive motor again
DURATION:  Trip-to-reset ≈ 10 seconds (motor inertia)
```

### CIE lesson demonstrated
Two controllers: one "compromised" (Core2 commanding dangerous
speed), one independent (ATOM Lite watching RPM and enforcing
the limit). The ATOM Lite acts as the Safety Instrumented System
(SIS) — physically separate, independently powered, monitoring
the same physical quantity. This IS the TRITON lesson: the SIS
must be independent of the primary controller because if they
run on the same hardware, compromising one compromises both.

---

## Station 4: FLUID CIE — "The Overpressure Relief"

### What the student sees
A sealed tube section with a pressure gauge (tube pressure
sensor displayed on screen) and a spring-loaded relief valve
with a small ribbon/flag at the exhaust. As the pump pressurizes
the system beyond safe limits, the pressure reading climbs,
the LED strip shifts to red — then PSSST — the relief valve
opens, the ribbon flutters, air/water vents through the valve,
pressure drops. The buzzer sounds. The camera captures the
ribbon flutter. Pressure stabilizes. Pump continues but can't
exceed the valve's cracking pressure.

### How it works (non-destructive)
```
[Peristaltic pump] ─── [sealed tube section] ─── [spring-loaded relief valve]
        │                      │                          │
   [Relay: pump on/off]   [Tube Pressure ×2]        [flag/ribbon at exhaust]
        │                      │                          │
   [Core2 — "compromised"]    [display: P climbing]   [ESP32-CAM: captures flutter]
                               │
                          [RGB LED strip: pressure level]
```

### Components
| Part | Source | Purpose |
|------|--------|---------|
| Adjustable spring relief valve (1/4" barb, 5-15 PSI adjustable) | Amazon ~$8 | Opens at set pressure, closes when P drops. Spring-loaded, infinite cycles. |
| Small ribbon/flag | Craft store ~$1 | Visual indicator at exhaust: flutters when valve vents |
| Sealed tube section (clear acrylic, capped ends) | Amazon ~$5 | Visible pressurization (if using colored water, you can see it) |
| One-way check valve | Amazon ~$3 | Prevents backflow during reset |

### Auto-reset sequence
```
NORMAL:    Pump off → P = atmospheric → GREEN
ATTACK:    Pump ON (software commands continuous pressurization) → P rises → YELLOW → RED
TRIP:      P reaches cracking pressure → valve OPENS → flag flutters → BUZZER
                                          → P drops to just below cracking
STEADY:    Pump still running but P can't exceed valve setting
           (pump pushes, valve vents — dynamic equilibrium)
RESET:     Software commands pump OFF → P drops to atmospheric → valve closes → flag still
DURATION:  Instant trip, instant reset when pump stops
```

### CIE lesson demonstrated
This IS the pressure vessel + relief valve scenario from the
CIE literature. The spring-loaded valve opens at F = kx (Hooke's
law) when the fluid pressure on the valve disc exceeds the spring
preload. The cracking pressure is set by the spring constant k
and the compression x — both PHYSICAL properties that no software
can alter. Even if the PLC commanding the pump is completely
compromised and commands "pump forever," the relief valve limits
the system pressure to a safe maximum. The student sees: the
flag flutters every time the pump tries to overpressurize.
Physics wins every cycle.

---

## Station 5: OPTICAL CIE — "The Sensor Spoof"

### What the student sees
A light sensor reading a value displayed on screen. The hequ.ai
equation (Beer-Lambert, ideal gas, whatever is running) computes
a prediction based on that reading. Then — the software injects
a FALSE sensor value (simulating a MITM attack on the sensor
wire). The screen shows the false value and the equation computes
a wrong prediction. But a SECOND, independent sensor (physically
separate, on the ATOM Lite) reads the REAL value. The screen
splits: LEFT shows the compromised reading, RIGHT shows the
independent reading. They disagree. The DOV-DSL validity
envelope flags the discrepancy. BUZZER. RED. "SENSOR INTEGRITY
VIOLATION DETECTED."

### How it works
```
[LED source (DAC-controlled)]
        │
        ├── [Light sensor #1 → Core2 "compromised"] ─── software injects false value
        │
        └── [Light sensor #2 → ATOM Lite "independent"] ─── reads real value
                                                                │
                                                         [comparison: if |S1-S2| > threshold]
                                                                │
                                                         [BUZZER + RED LED: "SPOOF DETECTED"]
```

### Components
| Part | Source | Purpose |
|------|--------|---------|
| Light sensor ×2 | M5Stack $3 each | Redundant light measurement |
| ATOM Lite | M5Stack $8 | Independent monitor (physically separate from Core2) |
| DAC + LED | M5Stack $8 + $2 | Controlled light source |

### Auto-reset sequence
```
NORMAL:    Both sensors agree → equation computes correctly → GREEN
ATTACK:    Core2 firmware injects false value for sensor #1 → equation computes wrong → YELLOW
DETECT:    ATOM Lite compares sensor #2 to Core2's reported value → disagree → RED → BUZZER
RESET:     Core2 firmware stops injecting false value → sensors agree again → GREEN
DURATION:  Instant (software-controlled attack and reset)
```

### CIE lesson demonstrated
Redundant, independent sensors on physically separate hardware
is the fundamental CIE defense against sensor manipulation. The
ATOM Lite doesn't trust the Core2's reported value — it has its
own sensor and its own judgment. This is CIE Principle 5 (Layered
Defenses) + Principle 2 (Engineered Controls): the independent
sensor is the engineering control, and the comparison logic is
the active defense.

---

## Camera and Detection Infrastructure

Every station has visual + sensor evidence of the consequence:

| Station | Camera sees | Sensors detect | Audio |
|---------|------------|----------------|-------|
| Thermal | Thermal camera: hot spot growing then cooling. RGB LED strip color shift. | KMeter: T spike then drop. Thermostat: relay state change. | Click (thermostat), buzzer |
| Electrical | Magnified PTC fuse. Load LED going dark. | AMeter: current spike then drop to ~0. VMeter: voltage redistribution. | Buzzer |
| Mechanical | Motor disk spinning faster, then slowing. LED ring color shift. | Encoder: RPM spike then drop. ATOM Lite relay: state change. | Motor whine pitch change, buzzer |
| Fluid | Flag/ribbon fluttering at relief valve exhaust. Pressure gauge on screen. | Tube Pressure: P spike then plateau at cracking pressure. Flow: Q drops when venting. | Hiss of venting air/water, buzzer |
| Optical | Split screen: two sensor readings diverging. | Two light sensors: readings disagree by > threshold. | Buzzer |

### Camera hardware
| Part | Source | Qty | Purpose |
|------|--------|-----|---------|
| ESP32-CAM module | Amazon ~$8 | 5 | One per station, captures consequence moment, streams to makau.ai |
| M5Stack Timer Camera | [M5Stack](https://shop.m5stack.com/products/esp32-psram-timer-camera-ov3660) | 2 | Higher-quality camera for stations where visual detail matters (thermal, fluid) |

---

## Updated Complete Shopping List (CIE-ready)

### Per-station additions for CIE demos
| Part | Source | Qty | ~$ ea | Total |
|------|--------|-----|-------|-------|
| KSD301 bimetallic thermostat (70°C) | Amazon | 3 | $1 | $3 |
| PTC resettable fuse (500mA, assorted) | Amazon | 1 pack (20pc) | $5 | $5 |
| Adjustable spring relief valve | Amazon | 2 | $8 | $16 |
| WS2812 RGB LED strip (1m, cuttable) | Amazon | 3 | $5 | $15 |
| Piezo buzzer | Amazon | 5 | $1 | $5 |
| ESP32-CAM module | Amazon | 5 | $8 | $40 |
| M5Stack Timer Camera | M5Stack | 2 | $20 | $40 |
| Small ribbons/flags (craft) | Craft store | 1 pack | $3 | $3 |
| Magnifying lens (mounted) | Amazon | 2 | $3 | $6 |
| ATOM Lite (independent safety monitors) | M5Stack | 3 | $8 | $24 |
| Clear acrylic tube + caps (pressure demo) | Amazon | 2 | $5 | $10 |
| One-way check valves | Amazon | 3 | $2 | $6 |

**CIE additions subtotal: ~$173**

### Grand total (previous lab + CIE additions)
| Category | Cost |
|----------|------|
| Previous lab design (sensors + actuators + controllers) | ~$950 |
| CIE demonstration components | ~$173 |
| **TOTAL** | **~$1,123** |

---

## Summary of non-destructive consequence mechanisms

| Mechanism | What happens | How it resets | Cycle time | Lifetime |
|-----------|-------------|---------------|------------|----------|
| PTC resettable fuse | Polymer expands, breaks conduction | Cools down, polymer contracts | 15-20s | 10,000+ cycles |
| Bimetallic thermostat | Bimetal strip snaps open | Cools below reset temp | 30-45s | 100,000+ cycles |
| Spring relief valve | Spring compresses, disc unseats | Pressure drops, spring closes disc | Instant | Indefinite |
| Independent safety relay (ATOM Lite) | Software trips relay on threshold | Software re-closes relay when safe | 5-10s | Indefinite |
| Sensor comparison (ATOM vs Core2) | Alert on disagreement | Agreement restored when spoof stops | Instant | Indefinite |
| RGB LED strip | Color shifts green → red | Color shifts red → green on reset | Instant | 50,000+ hours |
| Piezo buzzer | Sounds alarm | Silences on reset | Instant | Indefinite |
| Flag/ribbon at valve exhaust | Flutters when air/water vents | Stops when valve closes | Instant | Indefinite |
