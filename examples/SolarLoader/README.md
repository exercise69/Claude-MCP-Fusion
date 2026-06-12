# SolarLoader Enclosure — Example Scripts

Split-shell 3D-printed enclosure for the **SolarLoader** IoT device — a solar charge
controller with local display, RS485 communication, SD card logging, and a Li-ion
battery buffer.

> **Software / Firmware:** [github.com/exercise69/Solar-Loader](https://github.com/exercise69/Solar-Loader)

These scripts are the worked example for the patterns documented in the
[repo root README](../../README.md): a fully parametric, shared-core design driven
by Fusion User Parameters, rounded internal cut corners, snap features welded into
a single printable body, and a parameter-derived battery bay.

## Hardware Stack

| Layer | Board | Function |
|-------|-------|----------|
| Bottom | Adafruit ESP32-S3 Reverse TFT Feather | MCU + 1.14" TFT display (front-facing) |
| + | Adafruit AdaloggerFeatherWing | microSD card logging |
| + | Adafruit RS485 FeatherWing | Modbus RTU communication |
| Top | Power supply + screw terminals | RS485 cable connection |
| Bay | Li-ion cell (40 × 28 × 5 mm) | battery buffer, in a flat bay below the PCB |

All boards use the standard Adafruit FeatherWing form factor and stack vertically.
The display faces the front (bottom) of the enclosure; the RS485 cable exits the top shell.

Total PCB stack: approx. 52 × 23 × 32 mm (X × Y × Z).

## Files

| File | Description |
|------|-------------|
| `fusion_unterschale_v6.py` | **Bottom shell (current)** — Spiess-style snap lip, display window, USB-C & SD slots, living-hinge flex buttons, M2 board screws, Li-ion battery bay, rounded internal corners, thicker display bezel |
| `fusion_oberschale_v6.py` | **Top shell (current)** — matching notch grooves, RS485 cable exit, M4 mounting holes, battery retention tab |
| `solarloader_common.py` | Shared hardware constants + common user parameters (imported by both shells) |
| `solarloader_v5.py` | Shared parametric battery / inner-cavity geometry (imported by both shells; the name is just the module's origin version) |
| `SolarLoaderCase.scad` | Original OpenSCAD prototype (early geometry, for reference / comparison) |

The two shells derive all geometry from a shared parametric core, so changing one
User Parameter (`wall`, `clearance`, a `batt_*` dimension, …) propagates to every
dependent feature automatically.

## Enclosure Geometry (v6)

```
Overall (assembled):  ~58.3 × 42.3 × 52.0 mm  (X × Y × Z)
Wall thickness:        2.5 mm  (display bezel +0.5 mm via front_extra)
Split line:           Z = 22 mm (above PCB stack)

Bottom shell (Unterschale):   Z = -5.5 .. 26 mm   (display side)
Top shell    (Oberschale):    Z = 22 .. 46.5 mm   (wall side)

Hardware stack (Adafruit Feather):
  PCB footprint: X = -1.24..50.83,  Y = -0.04..22.90 mm
  Clearance:     0.6 mm all around
Battery bay grows the inner cavity in +Y (below the PCB); the case footprint
in X and the openings (USB-C, SD, display, RS485, M4) are unchanged.
```

## Features (v6)

- **Spiess-style snap connection.** A triangular-cross-section **lip** (male) runs
  along both long Y-sides of the bottom-shell tongue; the lead-in ramp is on top
  (eases insertion), the flat lock face on the bottom (catches on pull-up). The top
  shell carries matching rectangular **notch grooves** sized for the lip + `lip_gap`.
  In v6 the snap ridges are **welded into the shell** (overlap + `join`) so an STL of
  the body is one solid — and a `lip_foot` shoulder ties the tongue solidly to the
  wall rather than hanging off a thin web.
- **Living-hinge flex buttons.** D0/D1/D2 are finger-pressable pads cut free on three
  sides; the hinge strip is thinned from inside so the outer face stays flush, and an
  inner nub bridges the air gap to the tactile switch. **Reset stays a pin-hole.**
- **Display.** Recessed display area + full TFT window. Internal corners are **rounded**
  (`inner_r`) and the front bezel is thickened (`front_extra`) so the thin wall under
  the window isn't a crack-starter — without changing how deep the display seats.
- **Battery bay.** A flat Li-ion cell sits in a parameter-derived bay below the PCB; a
  **retention tab** cantilevers from the wall side to hold it. A reference dummy body
  (not for printing) can mark the cell volume.
- **Rounded internal corners** on USB-C, SD, RS485 and the display pocket (radii applied
  by filleting the cut tool before cutting).

## Fusion User Parameters

All visible in **Modify → Change Parameters**. Common parameters are shared between
both shell scripts. Parameters are **create-if-missing** — they only get created if
absent, so values you tune in *Change Parameters* survive a rebuild. To reset to code
defaults, call `define_common_params(des, overwrite=True)` (or pass `True` to a
`set_param`). The `notch_*` parameters set snap tightness (larger `notch_play` /
`notch_x_play` = looser).

| Group | Parameters |
|-------|-----------|
| Shell | `wall`, `clearance`, `fillet_r`, `split_z`, `lipo_h` |
| Snap-fit (lip) | `lip_h`, `lip_wall`, `lip_foot`, `lip_gap`, `snap_d`, `snap_h`, `snap_margin`, `snap_top` |
| Notch fit (top) | `notch_extra_d`, `notch_play`, `notch_z_play`, `notch_x_play` |
| Display | `recess_d`, `front_extra`, `inner_r` |
| USB-C | `usbc_half`, `usbc_z0`, `usbc_z1` |
| Buttons | `btn_d` (Reset pin-hole) |
| Flex buttons | `fb_pad`, `fb_slot`, `fb_hinge`, `fb_hinge_w`, `fb_nub_d`, `fb_nub_gap` |
| SD card | `sd_y0`, `sd_y1`, `sd_z0`, `sd_z1` |
| RS485 | `rs485_y0`, `rs485_y1`, `rs485_z0`, `rs485_z1` |
| Standoffs / screws | `so_od`, `so_h`, `screw_d`, `csk_d`, `csk_dep` |
| Top shell | `os_clear`, `mount_d`, `mount_x0`, `mount_x1`, `inner_r` |
| Battery / tab | `batt_w`, `batt_t`, `batt_depth`, `batt_xc`, `batt_top`, `batt_zfront`, `batt_xclear`, `batt_zclear`, `batt_floor`, `lasche_x0`, `lasche_x1`, `lasche_t`, `lasche_air`, `lasche_len` |

## How to Run

Run the bottom shell first, then the top (the top reads shared parameters). Easiest is
via Claude using the MCP `fusion_mcp_execute` tool with each file's contents, or inside
Fusion's Scripts dialog. Direct exec:

```python
exec(open('fusion_unterschale_v6.py').read()); run(None)   # bottom shell
exec(open('fusion_oberschale_v6.py').read()); run(None)    # top shell
```
