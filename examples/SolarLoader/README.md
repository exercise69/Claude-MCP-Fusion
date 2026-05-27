# SolarLoader Enclosure — Example Scripts

Split-shell 3D-printed enclosure for an ESP32-S3 Reverse TFT Feather + 3 FeatherWings
IoT stack (solar charge controller + display + RS485 + SD logging).

## Files

| File | Description |
|------|-------------|
| `fusion_unterschale.py` | Bottom shell — display face, USB-C, SD slot, standoffs, snap-fit lip |
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

**Bottom shell:**
- Display window: 25.5 × 15.4 mm (centred on TFT glass)
- USB-C slot in left wall: 10 × 6.3 mm
- SD card slot in right wall: 14.5 × 4.7 mm
- 3× D0/D1/D2 button pin holes + Reset (Ø2.5 mm through display face)
- 4× standoffs Ø5 mm, h=2.5 mm (PCB mounting)
- M2 countersunk screw holes through display face
- Snap-fit connection lip (4 mm high, 1.5 mm wall, 0.25 mm gap)

**Top shell:**
- RS485 cable exit in right wall: 13 × 9 mm
- 2× M4 mounting holes (Ø4.2 mm) through lid

## How to Run

Execute in Fusion 360 via MCP bridge:

```python
# Run bottom shell
exec(open('fusion_unterschale.py').read())

# Run top shell
exec(open('fusion_oberschale.py').read())
```

Or trigger via Claude using the MCP `fusion_mcp_execute` tool.
