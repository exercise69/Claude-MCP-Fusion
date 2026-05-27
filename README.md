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

Copy `f360_helpers.py` to a folder on your machine, then import it at the top of any
Fusion 360 Python script:

```python
import sys
sys.path.append('/path/to/Claude-MCP-Fusion')
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
3D-printed enclosure for a Feather-based IoT stack:

- `fusion_unterschale.py` — Bottom shell with display window, USB-C slot, SD card slot,
  standoffs, board screw holes, and a snap-fit connection lip
- `fusion_oberschale.py` — Top shell with RS485 cable exit and M4 mounting holes
- `SolarLoaderCase.scad` — Original OpenSCAD prototype (same geometry, for reference)

---

## License

MIT — use freely, no attribution required.
