# Fusion 360 Python API — gotchas & fixes

Every entry below is a real bug that produced a silent failure or a confusing
error. Skim before debugging a misbehaving script.

## 1. Internal unit is centimeters, not millimeters
The UI shows mm; the API expects cm. The most common bug, and it's silent (a
10× scale error that still "works"). Wrap every mm value: `f.cm(2.5)` → `0.25`.

## 2. `Line3D` has no `.direction`
`g.direction` → AttributeError. Compute it from endpoints:
```python
sp, ep = g.startPoint, g.endPoint
dx, dy, dz = ep.x-sp.x, ep.y-sp.y, ep.z-sp.z
length = (dx*dx+dy*dy+dz*dz) ** 0.5
if length > 1e-8 and abs(dz/length) > 0.99: ...
```

## 3. `occ.isVisible` is read-only — use `isLightBulbOn`
`occ.isVisible = False` → "no setter". Use `occ.isLightBulbOn = True/False`
(the lightbulb in the browser tree).

## 4. `body.deleteMe()` isn't permanent in a parametric design
Fusion regenerates the body from its features on the next timeline update.
Instead delete the **features** (combine, fillet, extrude, sketches,
constructionPlanes — reverse order) or the whole **component**
(`occ.deleteMe()`).

## 5. `join()` fails silently when bodies don't overlap
`combineFeatures` with Join raises no error but does nothing if the bodies only
touch (coincident face) or have a gap. Make them **overlap** by a small epsilon
(~0.1 mm) before joining. Symptom: a tab/lip/rib stays a separate body and your
STL is missing it — catch it with a body-count check.

## 6. Don't `cut()` with a body from another component
Using an external/assembly body as the cut tool fails. Always make a fresh
helper body (`box`/`cylinder`) in the **same** component as the target and use
that as the tool.

## 7. `CameraTypes` lives in `adsk.core`, not `adsk.fusion`
`adsk.fusion.CameraTypes` → AttributeError. Use
`adsk.core.CameraTypes.OrthographicCameraType`.

## 8. Assembly bodies are deeply nested
Imported components (e.g. a dev board) can be 2–3 occurrence levels deep, not in
`root.bRepBodies`. Recurse through `occ.childOccurrences`.

## 9. World coordinates need the occurrence transform chain
A body's coords are local to its component. For world coords, multiply up the
`assemblyContext` transform chain (or `point.transformBy(occ.transform)` for a
direct child).

## 10. At z≈0, use the standard XY plane
`constructionPlanes.createInput().setByOffset(xy, 0.0)` can misbehave. At z≈0
return `comp.xYConstructionPlane` directly; only build an offset plane for z≠0.

## 11. STL export path must NOT include `.stl`
`createSTLExportOptions(body, path)` appends `.stl`. Passing `foo.stl` yields
`foo.stl.stl`. Pass the path without extension.

## 12. Scripts need `def run(_context):`
Every script executed via the MCP bridge must define `run(_context)` as the
entry point. Fetch `app/des/root/vp` at the top. **Don't** catch exceptions
inside `run` — the uncaught traceback is what tells you where/why it failed.
