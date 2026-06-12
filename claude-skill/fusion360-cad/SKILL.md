---
name: fusion360-cad
description: >-
  Drive Autodesk Fusion 360 to build, edit, measure, render, or export
  parametric 3D models by scripting its Python API — via the Fusion MCP
  connector tools (fusion_mcp_execute / fusion_mcp_read / fusion_mcp_update) or a
  fallback HTTP bridge. Use this whenever the user wants to design, generate,
  modify, inspect, dimension, or 3D-print a part, enclosure, housing, case, lid,
  bracket, mount, or any CAD geometry in Fusion 360 — including parametric user
  parameters, snap-fit / tongue-and-groove joints, welding separate bodies into
  one printable solid, internal-corner radii, STL/STEP/3MF export for printing,
  f360_helpers usage, and debugging Fusion scripts (e.g. a model that came out
  10x too big from a mm/cm mix-up). Trigger even when the user doesn't say
  "script" or name Fusion explicitly but is clearly modeling a printable part.
  Do NOT use this for installing or configuring the connector itself, choosing
  filament or finding print services, standalone STL/mesh repair or format
  conversion outside Fusion, slicing/G-code questions, other CAD tools (Blender,
  Inventor, FreeCAD), or click-by-click manual-UI beginner tutorials that don't
  involve scripting.
---

# Fusion 360 parametric CAD via scripting

You design Fusion 360 models **programmatically** — Python scripts that build
parametric geometry, which you then verify and refine in a loop. This is far
more precise and reproducible than clicking the UI or generating blobs: every
dimension is a number, every part is a parameter, and you can prove correctness
before anyone prints a thing.

## How you talk to Fusion

Fusion must be **running with a design open** — the bridge lives inside the
Fusion process. Two ways to send scripts, in order of preference:

1. **MCP connector tools** (preferred — direct, no shell round-trip):
   - `fusion_mcp_execute` — run Python. Shape:
     `featureType="script"`, `object.script="<code>"`. The code MUST define
     `def run(_context):` as entry point. Anything you `print()` comes back as
     the tool output; uncaught exceptions come back as the error — so **do not
     wrap your run() in try/except**, or you lose the traceback you need to fix
     the bug.
   - `fusion_mcp_read` — `queryType="screenshot"` (with `direction` like
     `iso-top-right`, `front`, `top`; `transparentBackground`), or
     `queryType="apiDocumentation"` (with `searchPattern`) to look up real API
     signatures, or `document`/`projects` queries.
   - `fusion_mcp_update` — targeted model updates.
2. **Fallback CLI bridge** (if the connector isn't loaded this session): the
   Fusion MCP bridge is a Streamable-HTTP MCP server at
   `http://127.0.0.1:27182/mcp`, tool `fusion_mcp_execute`. You can write a tiny
   client that does the MCP handshake (`initialize` → `notifications/initialized`
   → `tools/call`) and POSTs the script. Keep such a client **outside any
   temp dir** (those get wiped on reboot) and **outside the git repo**.

Note: MCP servers load at **session start**. A newly added connector / config
only appears in a fresh session.

## Two non-negotiable conventions

- **Fusion's internal unit is centimeters, not millimeters.** This is the #1
  source of silent 10×-scale bugs. Wrap every mm value: `f.cm(2.5)` → `0.25`.
  When in doubt, multiply mm by 0.1.
- **Every script needs `def run(_context):`** as its entry point, and should
  fetch `app/des/root/vp` at the top (see the bootstrap below).

## The f360_helpers library

If `f360_helpers.py` (from this repo) is on the path it removes most API tedium
(boxes, cuts, fillets, params, exports, camera). Full function list + the script
bootstrap: **read `references/helpers.md`**. If no helper library is present, the
same patterns work with the raw `adsk.core` / `adsk.fusion` API — just more
verbose.

Use this bootstrap at the top of scripts so the import works regardless of who
runs it (no hard-coded user path committed — it checks `~/.fusion360scripts_path`,
then `$FUSION360SCRIPTS`, then walks up from `__file__`):

```python
import os, sys
def _f360_root():
    cfg = os.path.expanduser('~/.fusion360scripts_path')
    if os.path.exists(cfg) and open(cfg).read().strip():
        return open(cfg).read().strip()
    if os.environ.get('FUSION360SCRIPTS'):
        return os.environ['FUSION360SCRIPTS']
    try:
        d = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()
    for _ in range(6):
        if os.path.exists(os.path.join(d, 'f360_helpers.py')):
            return d
        d = os.path.dirname(d)
    return os.getcwd()
sys.path.append(_f360_root())
import f360_helpers as f
```

## Build → verify → iterate (this is the whole method)

Don't build blind and hope. Each change is a small loop:

1. **Build** a feature with a script (parametric — derive geometry from
   `set_param` values so changes propagate automatically).
2. **Verify objectively** — pick the cheapest proof that actually settles the
   question, don't just eyeball a render:
   - `f.bbox_str(body)` to confirm position/size in mm.
   - **Body count** per component (`comp.bRepBodies.count`) — for a printable
     part you want **exactly one** welded solid. Two bodies usually means a snap
     tab / lip / rib didn't fuse (see Welding below).
   - **`body.pointContainment(point)`** to prove material is (or isn't) where it
     must be — e.g. that a connecting shoulder actually fills a gap, or that a
     clearance stays open. Points are in cm and may need
     `point.transformBy(occ.transform)` for world coords. This is how you settle
     "is the rim actually attached?" without guessing from a pale render.
   - A **screenshot** to confirm overall shape — but know Fusion's default
     shading washes out thin features, so prefer numeric proofs for fine detail.
3. **Iterate** — adjust a parameter or the script and repeat. Because geometry
   is parameter-derived, most fixes are one number.

## Best practices that prevent reprints

- **Round internal corners.** Sharp internal corners are stress risers /
  crack-starters and printers will flag them. Round a rectangular cut by
  filleting the **cut tool's** edges (parallel to the through-axis) *before*
  cutting, so the resulting pocket/window/slot has radii. Cleaner than trying to
  select the cut edges afterward.
- **Weld features into one solid.** Snap knobs, tabs, ribs, lips created as
  separate bodies will export as separate shells — an STL of "the shell body"
  silently omits them. Make them **overlap** the parent by a small epsilon
  (e.g. 0.1 mm) and `join()`. `join()` does nothing on merely-touching
  (coincident-face) bodies — it needs real overlap. Verify with the body count.
- **Mating clearance vs. attachment are different problems.** A tongue that must
  slide into the other shell needs a gap on its *mating* face, but still has to
  be solidly attached to its *own* wall — solve attachment with a shoulder/foot
  that overlaps the wall, not by removing the clearance.
- **Keep exports outside git.** STL/STEP/3MF are build artifacts and binaries —
  write them to a folder **outside** any repo so they aren't published. Export
  `body` for STL, `component` for STEP/3MF. Give STL paths **without** the
  `.stl` extension (the API appends it). Offer both STL (for slicers) and STEP
  (raw data many print services prefer).
- **Look up the API, don't guess.** Use `fusion_mcp_read` `apiDocumentation`
  before reaching for an unfamiliar class/method. It's cheaper than a failed
  script and a guess.
- **Version by copy when asked to "keep the old one."** Make `*_v2` scripts /
  components rather than overwriting, and hide or delete superseded versions
  only on request.

## Gotchas (read before debugging)

The Fusion API has sharp edges that produce silent failures or confusing errors
(units, `Line3D` has no `.direction`, `isLightBulbOn` not `isVisible`,
`deleteMe()` regenerates in a parametric timeline, `join()` needs overlap, STL
double-extension, deep occurrence nesting, world-transform chains). When a
script misbehaves or you're about to touch one of these, **read
`references/gotchas.md`** — each entry is a real bug with its fix.

---

Provenance: distilled from building real 3D-printed enclosures with this
library; see `examples/` for complete parametric case scripts. MIT-licensed,
same as the rest of the repo.
