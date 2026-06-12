# f360_helpers.py — API reference

A reusable helper library that wraps the most tedious parts of the Fusion 360
Python API. It ships in this repo (`f360_helpers.py` at the root). Import via the
bootstrap in SKILL.md, then call as `f.<name>(...)`. **All coordinates/lengths
are in cm** — wrap mm with `f.cm()`.

If this library isn't present, every function below maps to a short block of raw
`adsk.core` / `adsk.fusion` code — the helper just saves the boilerplate.

## Units
- `f.cm(mm)` → cm. Use on EVERY mm literal. `f.cm(2.5)` = 0.25.
- `f.mm(cm)` → mm. For reading values back.

## Construction planes
- `f.zplane(comp, z_cm)` — XY-parallel plane at z (returns std XY plane at z≈0).
- `f.xplane(comp, x_cm)` — YZ-parallel plane at x.

## Primitives (return a BRepBody)
- `f.box(comp, x0,y0,z0, x1,y1,z1)` — box between two corners. NOTE: internally
  sketches on the z0 plane and extrudes +Z, but the body has all 12 edges, so
  you can fillet edges parallel to any axis afterwards.
- `f.cylinder(comp, cx,cy, z0,z1, diameter)` — cylinder (center cx/cy).
- `f.triangle_prism_x(comp, x0,x1, y0,z0, y1,z1, y2,z2)` — triangular prism
  extruded along X; YZ cross-section from 3 corner points. Used for snap ridges.

## Boolean ops (tool body is consumed)
- `f.cut(comp, target, tool)` — subtract. Always make a fresh helper body as the
  tool; never use a body from another component as the tool.
- `f.join(comp, target, tool)` — unite. **Bodies must OVERLAP**, not just touch.
- `f.intersect(comp, target, tool)` — keep intersection.

## Fillets / chamfers
- `f.fillet_z_edges(comp, body, r_cm)` — round all Z-parallel (vertical) edges.
- `f.fillet_h_edges(comp, body, r_cm)` — round all XY-parallel edges.
- `f.fillet_all_edges(comp, body, r_cm)` — all edges (may fail on complex bodies).
- `f.chamfer_z_edges(comp, body, dist_cm)` — chamfer vertical edges.
- To round *internal cut corners*: build the cut tool box, fillet the 4 edges
  parallel to the cut's through-axis, then `f.cut`. (Write a tiny local helper
  that selects edges by direction; `fillet_z_edges` rounds ALL z-edges of a body
  so it's too broad for a finished part with a tongue.)

## Components & lookup
- `f.new_component(root, "Name")` → occurrence. `.component` for the component.
- `f.find_occurrence(root, "Name")` → occurrence or None (direct children only;
  matches `component.name`, including a Fusion `" (1)"` suffix if present).
- `f.delete_component(root, "Name")` → True/False. Deletes occurrence + features.

## Visibility / opacity
- `f.show(root, name)` / `f.hide(root, name)` — toggle `isLightBulbOn`.
- `f.set_opacity(root, name, 0.0..1.0)` — body transparency for x-ray renders.

## User parameters (drive everything from these)
- `f.set_param(des, 'wall', 2.5, 'comment', overwrite=True)` — value in mm.
  With `overwrite=False` it is **create-if-missing**: manual edits in Fusion
  survive a rebuild. To force code defaults onto a live doc, run once with
  `overwrite=True`.
- `f.get_param_mm(des, 'wall')` / `f.get_param_cm(des, 'wall')` — read back.

## Camera / screenshots
- `f.set_camera(vp, eye, target, up=(0,0,1))` — eye/target in cm. Only the
  view *direction* matters if you then call `fit_view` (which reframes).
- `f.fit_view(vp)` — fit all visible.
- `f.screenshot(vp, path, eye=, target=, up=, width=, height=)`.
- `f.screenshot_fit(vp, path, w, h)`.
- Prefer the connector's `fusion_mcp_read` screenshot for review images — it has
  named directions and transparent background.

## Export (artifacts — keep OUTSIDE git)
- `f.export_stl(des, body, '/path/Name', refinement='high'|'medium'|'low')`
  — path WITHOUT `.stl`. Exports one body, so weld first (single body).
- `f.export_step(des, comp, '/path/Name')` — whole component (all bodies).
- `f.export_3mf(des, comp, '/path/Name')` — component, supports colors.
- `f.export_stl_all_components(des, root, output_dir)` — one STL per component.

## Debug / measure (your verification toolkit)
- `f.bbox_str(body)` → `"X=.. Y=.. Z=.. mm"` — quick position/size check.
- `f.bbox_mm(body)` → dict (xmin..zmax, width, depth, height).
- `f.list_bodies(root)` — print all bodies (root + components).
- For proofs beyond bbox, drop to raw API:
  `comp.bRepBodies.count` (welded-single-body check) and
  `body.pointContainment(adsk.core.Point3D.create(x,y,z))` returning
  `PointInside/On/OutsidePointContainment` (transform the point by
  `occ.transform` for world coords).
