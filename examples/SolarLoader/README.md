# SolarLoader Enclosure — Example Scripts

Split-shell 3D-printed enclosure for the **SolarLoader** IoT device — a solar charge
controller with local display, RS485 communication, and SD card logging.

> **Software / Firmware:** [github.com/exercise69/Solar-Loader](https://github.com/exercise69/Solar-Loader)

## Hardware Stack

| Layer | Board | Function |
|-------|-------|----------|
| Bottom | Adafruit ESP32-S3 Reverse TFT Feather | MCU + 1.14" TFT display (front-facing) |
| + | Adafruit AdaloggerFeatherWing | microSD card logging |
| + | Adafruit RS485 FeatherWing | Modbus RTU communication |
| Top | Power supply + screw terminals | RS485 cable connection |

All boards use the standard Adafruit FeatherWing form factor and stack vertically.
The display faces the front (bottom) of the enclosure; the RS485 cable exits the top shell.

Total PCB stack: approx. 52 × 23 × 32 mm (X × Y × Z).

## Files

| File | Description |
|------|-------------|
| `fusion_unterschale.py` | Bottom shell v1 — flat display face |
| `fusion_unterschale_v2.py` | Bottom shell v2 — recessed display area (Adafruit-style, recommended) |
| `fusion_oberschale.py` | Top shell — RS485 cable exit, M4 mounting holes |
| `SolarLoaderCase.scad` | Original OpenSCAD prototype (same geometry, for reference / comparison) |

## Enclosure Geometry

```
Overall (assembled):  58.3 × 29.1 × 42.5 mm
Wall thickness:        2.5 mm
Split line:           Z = 22 mm (above PCB stack)

Bottom shell (Unterschale):   Z = -5.04 .. 22 mm
Top shell    (Oberschale):    Z = 22 .. 37.5 mm

Hardware stack (Adafruit Feather):
  PCB footprint: X = -1.24..50.83,  Y = -0.04..22.90 mm
  Clearance:     0.6 mm all around
```

## Features

**Bottom shell (v2 — recommended):**
- Recessed display area (Adafruit-style): 41 × 21 mm, 1.5 mm deep → 1 mm remaining wall
  - Covers display module, D0/D1/D2 buttons (X=7.6 mm) and Reset (X=44.5 mm)
- TFT opening: 25.5 × 15.4 mm full cutout (centred on TFT glass at X=26.26, Y=11.35)
- USB-C slot in left wall: 10 × 4.5 mm (Z=0..4.5 mm)
- SD card slot in right wall: 14.5 × 4.7 mm
- 3× D0/D1/D2 button pin holes + Reset (Ø2.5 mm through 1 mm recess wall)
- 4× standoffs Ø5 mm, h=2.5 mm (PCB mounting — outside recess area)
- M2 countersunk screw holes through display face
- Snap-fit connection lip (4 mm high, 1.5 mm wall, 0.25 mm gap) + 2 cantilever clips

**Top shell:**
- RS485 cable exit in right wall: 13 × 9 mm
- 2× M4 mounting holes (Ø4.2 mm) through lid

## How to Run

Execute in Fusion 360 via MCP bridge:

```python
# Run bottom shell (v2 — recessed display)
exec(open('fusion_unterschale_v2.py').read())

# Run top shell
exec(open('fusion_oberschale.py').read())
```

Or trigger via Claude using the MCP `fusion_mcp_execute` tool.
