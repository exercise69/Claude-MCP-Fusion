# Claude-MCP-Fusion

**Reusable Python helpers for driving Autodesk Fusion 360 via Claude and the MCP protocol.**

This library grew out of building a real-world IoT device enclosure with an AI-assisted CAD workflow:
Claude → MCP-Bridge → Fusion 360 Python API. The helper functions abstract away the most
tedious parts of the API and document the gotchas we discovered along the way.

---

## What's in here

| File | Description |
|------|-------------|
| `f360_helpers.py` | Reusable helper library — import in any Fusion script |
| `KNOWN_ISSUES.md` | Collected API gotchas (units, Line3D, isLightBulbOn, …) |
| `examples/` | Complete scripts for real projects |

---

## Quick Start

Clone the repo somewhere on your machine. So the scripts can locate `f360_helpers.py`
**without a hard-coded personal path**, point them at the repo root in one of three ways
(checked in this order):

1. **Path file** *(recommended)* — create `~/.fusion360scripts_path` containing one line
   with the absolute repo path:
   ```
   /path/to/Claude-MCP-Fusion
   ```
   This file lives outside the repo, so your username never ends up in committed code.
2. **Environment variable** — set `FUSION360SCRIPTS` to the repo root.
3. **Auto-detect** — if neither is set, the scripts walk up from their own location
   (`__file__`) looking for `f360_helpers.py`. Works for normal Fusion script runs, but
   not when a script is run via `exec(open(...).read())` (no `__file__`), which is why the
   path file is recommended.

The example scripts use this self-contained bootstrap at the top — copy it into your own
scripts:

```python
import os, sys

def _f360_root():
    _cfg = os.path.expanduser('~/.fusion360scripts_path')
    if os.path.exists(_cfg) and open(_cfg).read().strip():
        return open(_cfg).read().strip()
    if os.environ.get('FUSION360SCRIPTS'):
        return os.environ['FUSION360SCRIPTS']
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()
    for _ in range(6):
        if os.path.exists(os.path.join(_d, 'f360_helpers.py')):
            return _d
        _d = os.path.dirname(_d)
    return os.getcwd()

_root = _f360_root()
for _p in (_root, os.path.join(_root, 'examples', 'SolarLoader')):
    if _p not in sys.path:
        sys.path.append(_p)

import f360_helpers as f

def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    comp_occ = f.new_component(root, "MyPart")
    comp = comp_occ.component

    # Create a 50 × 30 × 20 mm box
    shell = f.box(comp, 0, 0, 0, f.cm(50), f.cm(30), f.cm(20))

    # Round the vertical edges with R=2mm
    f.fillet_z_edges(comp, shell, f.cm(2))

    # Hollow it out (3mm wall)
    f.cut(comp, shell, f.box(comp,
        f.cm(3), f.cm(3), f.cm(3),
        f.cm(47), f.cm(27), f.cm(20.1)))

    print(f.bbox_str(shell))
```

> **Important:** Fusion 360 uses centimeters internally, not millimeters.
> Always wrap mm values with `f.cm(...)`. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for more.

---

## API Reference

### Units

```python
f.cm(2.5)       # 2.5 mm → 0.25 cm  (use everywhere)
f.mm(0.25)      # 0.25 cm → 2.5 mm  (for reading back values)
```

### Primitives

```python
body = f.box(comp, x0, y0, z0, x1, y1, z1)
# Creates a box body between two corners (all in cm)

body = f.cylinder(comp, cx, cy, z0, z1, diameter)
# Creates a cylinder (cx/cy = center, diameter in cm)
```

### Boolean Operations

```python
f.cut(comp, target_body, tool_body)      # Subtract tool from target
f.join(comp, target_body, tool_body)     # Unite (bodies must touch/overlap)
f.intersect(comp, target_body, tool_body) # Keep intersection only
```

> **Note:** `join()` silently does nothing if bodies don't overlap. See KNOWN_ISSUES #5.

### Edge Fillets & Chamfers

```python
f.fillet_z_edges(comp, body, r_cm)   # Round vertical (Z-parallel) edges
f.fillet_h_edges(comp, body, r_cm)   # Round horizontal (XY-parallel) edges
f.fillet_all_edges(comp, body, r_cm) # Round ALL edges (may fail on complex bodies)
f.chamfer_z_edges(comp, body, d_cm)  # Chamfer vertical edges
```

### Components

```python
occ = f.new_component(root, "MyPart")   # Create named component
comp = occ.component

occ = f.find_occurrence(root, "MyPart") # Find by name (direct children only)
f.delete_component(root, "MyPart")      # Delete component + all features
```

### Visibility & Opacity

```python
f.show(root, "Oberschale")              # isLightBulbOn = True
f.hide(root, "Unterschale")             # isLightBulbOn = False
f.set_opacity(root, "Oberschale", 0.3)  # 0.0 = transparent, 1.0 = opaque
```

### User Parameters

```python
f.set_param(des, 'wall', 2.5, 'Wall thickness mm')  # Create/update parameter
f.set_param(des, 'clearance', 0.6)

value_mm = f.get_param_mm(des, 'wall')   # Read back in mm
value_cm = f.get_param_cm(des, 'wall')   # Read back in cm
```

### Export

```python
# STL — single body (path without extension)
f.export_stl(des, body, '/tmp/Unterschale')
f.export_stl(des, body, '/tmp/Unterschale', refinement='medium')  # low|medium|high

# STEP — whole component
f.export_step(des, comp, '/tmp/Oberschale')

# 3MF — whole component (modern 3D printing format, supports colors)
f.export_3mf(des, root, '/tmp/SolarLoader_full')

# Export all visible components as STL
paths = f.export_stl_all_components(des, root, '/tmp/export')
```

### Camera & Screenshots

```python
f.fit_view(vp)                                   # Fit all visible objects
f.screenshot_fit(vp, '/tmp/render.png')          # Screenshot after fit
f.screenshot(vp, '/tmp/render.png',
    eye=(15, -20, 30), target=(2.5, 1.5, 1.5))  # Screenshot from specific angle
```

### Debug & Analysis

```python
f.list_bodies(root)      # Print all bodies (root + components) to console
f.bbox_str(body)         # "X=0.0..50.0  Y=0.0..30.0  Z=0.0..20.0 mm"
d = f.bbox_mm(body)      # Dict: xmin, xmax, ymin, ymax, zmin, zmax, width, depth, height
```

---

## The Workflow: Claude + MCP + Fusion 360

This library is designed for use with a Fusion 360 MCP bridge (e.g.
[ndoo/fusion360-mcp-bridge](https://github.com/ndoo/fusion360-mcp-bridge) or similar).
Claude writes Python scripts, which are executed inside Fusion via the MCP protocol.

All scripts need a `run(_context)` entry point:

```python
def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    vp   = app.activeViewport
    # your code here
```

### Connecting today: the official Fusion MCP connector

Recent Fusion ships a built-in MCP server (Streamable HTTP at
`http://127.0.0.1:27182/mcp`) exposing:

- `fusion_mcp_execute` — run a Python script (`featureType="script"`,
  `object.script=<code>`; the code needs `def run(_context):`). `print()` output
  comes back as the result; don't catch exceptions or you lose the traceback.
- `fusion_mcp_read` — `apiDocumentation` lookups (so you check real API
  signatures instead of guessing), `screenshot` with named directions
  (`iso-top-right`, `front`, …), and document/project queries.
- `fusion_mcp_update` — targeted model updates.

Point any MCP client at that URL — Claude Code via a project `.mcp.json`
(`{"mcpServers":{"fusion":{"type":"http","url":"http://127.0.0.1:27182/mcp"}}}`),
or the Claude desktop app's connector — and Claude drives Fusion directly. A
from-scratch bridge add-in (e.g. ndoo/fusion360-mcp-bridge) works too. MCP
servers load at **session start**, so a newly added connector needs a fresh
session.

### The method: build → verify → iterate

Scripted CAD is powerful because you can **prove** correctness instead of
eyeballing a render:

- `f.bbox_str(body)` for size/position,
- **body count** per component (`comp.bRepBodies.count` == 1 for a printable,
  welded solid),
- `body.pointContainment(point)` to prove material sits exactly where it must
  (e.g. a connecting shoulder fills a gap; a clearance stays open),
- a screenshot for overall shape — but Fusion's shading washes out thin
  features, so prefer the numeric proofs for fine detail.

Drive geometry from user parameters (`f.set_param`) so most fixes are one number.

### Best practices that prevent reprints

- **Round internal cut corners** by filleting the cut *tool* before cutting —
  sharp internal corners are crack-starters.
- **Weld** snap tabs / lips / ribs into the shell with `join()`; overlap by
  ~0.1 mm, since `join()` ignores merely-touching bodies — otherwise the STL
  silently drops them (catch it with the body-count check).
- **Keep STL/STEP/3MF exports outside the repo** — they're binaries/artifacts.
- **Look up the API** via `fusion_mcp_read` `apiDocumentation` rather than guess.

### Bundled Claude skill

[`claude-skill/fusion360-cad/`](claude-skill/fusion360-cad/) packages this whole
workflow as an installable skill for Claude Code / the Claude desktop app, so a
fresh session auto-loads the conventions, the helper reference, and the gotchas.
Drop it into your skills directory (e.g. `~/.claude/skills/`).

---

## Known Gotchas

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for a full list. The short version:

- **Everything is in cm** — wrap all mm values with `f.cm(...)`
- **`Line3D` has no `.direction`** — compute from startPoint/endPoint manually
- **Use `isLightBulbOn`**, not `isVisible` — the latter is read-only on Occurrences
- **`body.deleteMe()` isn't permanent** — delete the features instead, or the whole component
- **`join()` needs overlap** — bodies with only a gap between them won't join

---

## Example: IoT Device Enclosure (SolarLoader)

The `examples/SolarLoader/` folder contains the complete scripts for a split-shell
3D-printed enclosure for the **SolarLoader** — a solar charge controller with local
display, RS485 communication, and SD card logging, built on the Adafruit FeatherWing
ecosystem (ESP32-S3 Reverse TFT Feather + AdaloggerWing + RS485Wing).

> **Firmware & software:** [github.com/exercise69/Solar-Loader](https://github.com/exercise69/Solar-Loader)

Scripts:
- `fusion_unterschale.py` — Bottom shell: display window, USB-C slot, SD card slot,
  standoffs, M2 board screws, snap-fit connection lip
- `fusion_oberschale.py` — Top shell: RS485 cable exit, M4 mounting holes
- `SolarLoaderCase.scad` — Original OpenSCAD prototype (same geometry, for reference)

---

## License

Licensed under the **MIT License** — see [LICENSE](LICENSE). You may use, modify,
and redistribute this code freely, including commercially. The only condition is
that you keep the copyright and license notice in copies (MIT requires retaining
attribution, despite being otherwise unrestricted).

## Trademarks & Disclaimer

This is an independent, unofficial project. It is **not affiliated with, endorsed
by, or sponsored by Autodesk, Inc. or Anthropic**. "Autodesk" and "Fusion 360" are
trademarks of Autodesk, Inc.; "Claude" is a trademark of Anthropic, PBC — used here
only descriptively to indicate compatibility.

The scripts call the Autodesk® Fusion™ Python API at runtime; **no Autodesk software
is redistributed** in this repository. The software is provided **"as is", without
any warranty** — always verify generated geometry before fabricating, machining, or
otherwise relying on it. Your use of Autodesk Fusion remains subject to its own
applicable license terms.
