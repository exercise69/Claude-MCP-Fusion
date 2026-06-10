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
| `fusion_unterschale_v4.py` | Bottom shell v4 — **Spiess-style snap lip** (triangular ridge, recommended) |
| `fusion_oberschale_v4.py` | Top shell v4 — **matching notch grooves** for the v4 lip (recommended) |
| `solarloader_common.py` | Shared hardware constants + common user parameters (imported by both v4 scripts) |
| `fusion_unterschale_v3.py` | Bottom shell v3 — fully parametrised, cantilever-clip snap |
| `fusion_oberschale_v2.py` | Top shell v2 — fully parametrised (shares common params with bottom shell) |
| `fusion_unterschale_v2.py` | Bottom shell v2 — recessed display area, hardcoded values |
| `fusion_unterschale.py` | Bottom shell v1 — flat display face |
| `fusion_oberschale.py` | Top shell v1 — hardcoded values |
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

**v4 — Spiess-style snap connection (recommended):**

The v4 pair replaces the v3 cantilever clips with a **Spiess-style snap lip/notch**:

- **Lip (male, on the bottom shell tongue):** a continuous triangular-cross-section
  ridge running along both long Y-sides of the Steckzunge. The lead-in **ramp is on
  top** (eases insertion as the top shell descends), the flat **lock face is on the
  bottom** (catches the notch floor on pull-up).
  - `snap_d` = 0.8 mm overhang, `snap_h` = 1.2 mm lock height, `snap_margin` = 3.0 mm
    end inset, `snap_top` = 2.0 mm lip-end overhang above the lock face
  - `Lip_front` / `Lip_back` are **separate bodies** (can be repositioned/rotated
    individually in Fusion, then joined via Modify → Combine)
- **Notch (female, in the top shell inner long walls):** matching rectangular grooves
  sized for the lip + `lip_gap` tolerance.
- **RS485 cutout:** the right tongue wall is interrupted over the RS485 terminal
  (`rs485_y0`..`rs485_y1`, 5..18 mm) so the perimeter rim doesn't clash with the screw
  terminal.

Everything else (display recess, TFT window, USB-C/SD slots, button pin holes,
standoffs, M2 screws, M4 lid mounts) carries over from v3/v2.

**Bottom shell v3 (fully parametrised, cantilever clips):**
- All 25 design knobs registered as Fusion User Parameters (Modify → Change Parameters)
- Recessed display area (Adafruit-style): 41 × 21 mm, 1.3 mm deep → 1.2 mm remaining wall (3 perimeters @ 0.4 mm nozzle)
  - Covers display module, D0/D1/D2 buttons (X=7.6 mm) and Reset (X=44.5 mm)
- TFT opening: 25.5 × 15.4 mm full cutout (centred on TFT glass at X=26.26, Y=11.35)
- USB-C slot in left wall: 10 × 4.5 mm (Z=0..4.5 mm)
- SD card slot in right wall: 14.5 × 4.7 mm
- 3× D0/D1/D2 button pin holes + Reset (Ø2.5 mm through recess wall)
- 4× standoffs Ø5 mm, h=2.5 mm (PCB mounting)
- M2 countersunk screw holes through display face
- Snap-fit connection lip (4 mm high, 1.6 mm wall, 0.25 mm gap) + 2 cantilever clips
- `lipo_h` parameter prepared for future LiPo battery add-on (0 mm = no LiPo)

**Top shell v2 (recommended — fully parametrised):**
- 8 shell-specific Fusion User Parameters + shares common params with bottom shell
- RS485 cable exit in right wall: 13 × 9 mm
- 2 snap-fit windows matching bottom shell clips
- 2× M4 mounting holes (Ø4.2 mm) through lid

## Fusion User Parameters

All parameters visible in **Modify → Change Parameters**. Common parameters are shared between both shell scripts:

| Group | Parameters |
|-------|-----------|
| Shell | `wall`, `clearance`, `fillet_r`, `split_z`, `lipo_h` |
| Snap-fit (v4) | `lip_h`, `lip_wall`, `lip_gap`, `snap_d`, `snap_h`, `snap_margin`, `snap_top` |
| Notch fit (v4 top) | `notch_extra_d`, `notch_play`, `notch_z_play`, `notch_x_play` |
| Snap-fit (v3) | `lip_h`, `lip_wall`, `lip_gap`, `clip_w`, `clip_h`, `clip_ramp`, `clip_p` |
| Display recess | `recess_d` |
| USB-C | `usbc_half`, `usbc_z0`, `usbc_z1` |
| Buttons | `btn_d` |
| SD card | `sd_y0`, `sd_y1`, `sd_z0`, `sd_z1` |
| RS485 | `rs485_y0`, `rs485_y1`, `rs485_z0`, `rs485_z1` |

> **v4 parameter behaviour (create-if-missing):** the v4 scripts only *create*
> parameters that don't exist yet — they no longer overwrite values you've changed
> in Fusion. So you can tune e.g. `snap_d` or `notch_play` in *Change Parameters*,
> rebuild, and your value sticks. To reset everything to the code defaults, call
> `define_common_params(des, overwrite=True)` (or pass `True` to the per-script
> `set_param` calls). The `notch_*` parameters control snap-fit tightness — increase
> `notch_play` / `notch_x_play` for a looser fit, decrease for tighter.
| Standoffs | `so_od`, `so_h`, `screw_d`, `csk_d`, `csk_dep` |
| Top shell | `os_clear`, `rs485_y0`, `rs485_y1`, `rs485_z0`, `rs485_z1`, `mount_d`, `mount_x0`, `mount_x1` |

## How to Run

Execute in Fusion 360 via MCP bridge (run bottom shell first, then top):

```python
# Bottom shell v4 — Spiess-style lip (recommended)
exec(open('fusion_unterschale_v4.py').read()); run(None)

# Top shell v4 — matching notch grooves (recommended)
exec(open('fusion_oberschale_v4.py').read()); run(None)
```

Or trigger via Claude using the MCP `fusion_mcp_execute` tool.
