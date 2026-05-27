# Known Issues & API Gotchas — Fusion 360 Python API

Gesammelte Erfahrungen beim Schreiben von Fusion 360 Python Scripts via MCP-Bridge.
Alle Punkte sind durch konkrete Fehler in der Praxis aufgedeckt worden.

---

## 1. Fusion 360 arbeitet intern in Centimeter (nicht mm!)

**Problem:** Alle Koordinaten, Abstände und Radien müssen in **Centimeter** übergeben werden.
Die UI zeigt mm, die API erwartet cm — das ist die häufigste Fehlerquelle überhaupt.

**Lösung:**
```python
def cm(mm): return mm * 0.1   # 2.5mm → 0.25cm
```
Konsequent `f.cm(2.5)` statt `2.5` verwenden.

---

## 2. `adsk.core.Line3D` hat KEIN `.direction`-Attribut

**Problem:**
```python
# FALSCH — wirft AttributeError
if abs(g.direction.z) > 0.99: ...
```

**Lösung:** Richtung manuell aus Start- und Endpunkt berechnen:
```python
sp, ep = g.startPoint, g.endPoint
dx, dy, dz = ep.x - sp.x, ep.y - sp.y, ep.z - sp.z
length = math.sqrt(dx*dx + dy*dy + dz*dz)
if length > 1e-8 and abs(dz / length) > 0.99:
    edges.add(e)
```

---

## 3. `occ.isVisible` ist read-only — stattdessen `isLightBulbOn`

**Problem:**
```python
# FALSCH — wirft: property '_get_isVisible' of 'Occurrence' has no setter
occ.isVisible = False
```

**Lösung:**
```python
occ.isLightBulbOn = False   # Glühbirne im Fusion-Browser = Sichtbarkeit
occ.isLightBulbOn = True
```

---

## 4. `body.deleteMe()` ist nicht permanent bei parametrischem Design

**Problem:** Wenn man einen Body per `body.deleteMe()` löscht, regeneriert Fusion
ihn beim nächsten Timeline-Update aus seinen Features neu.

**Lösung:** Statt den Body zu löschen, die **Features** löschen (in umgekehrter Reihenfolge):
- `combineFeatures` (Boolean-Operationen)
- `filletFeatures`
- `extrudeFeatures`
- `sketches`
- `constructionPlanes`

Oder: Die gesamte **Komponente** (Occurrence) löschen mit `occ.deleteMe()`.

---

## 5. `join()` schlägt lautlos fehl wenn Bodies sich nicht berühren

**Problem:** `combineFeatures` mit `JoinFeatureOperation` erzeugt keinen Fehler, aber
es passiert nichts, wenn die Bodies keinen gemeinsamen Bereich haben (auch kein Berühren).

**Typisches Beispiel:** Eine Steckzunge (lip), die mit `lip_gap=0.25mm` Abstand zur
Gehäusewand entworfen ist — der Join schlägt fehl weil kein Overlap.

**Lösung:** 
- Bodies müssen sich überlappen (auch minimal, z.B. 0.1mm) damit `join()` funktioniert
- Alternativ: Bodies getrennt lassen (Slicer behandelt sie im gleichen Component als ein Objekt)

---

## 6. `cut()` direkt auf Außenflächen eines anderen Bodies schlägt fehl

**Problem:** Man kann nicht direkt mit `combineFeatures` in einen Body schneiden, der
zu einer anderen Komponente gehört (z.B. Assembly-Body als Tool).

**Lösung:** Immer einen neuen **Hilfs-Body** im gleichen Component erstellen (via `box()` 
oder `cylinder()`) und diesen als Tool für `cut()` verwenden. Nie externe Bodies als Tool.

---

## 7. `adsk.fusion.CameraTypes` existiert nicht

**Problem:**
```python
# FALSCH — AttributeError
cam.cameraType = adsk.fusion.CameraTypes.OrthographicCameraType
```

**Lösung:**
```python
cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
```
CameraTypes ist in `adsk.core`, nicht in `adsk.fusion`.

---

## 8. Occurrence-Baum: Assembly-Bodies sind tief verschachtelt

**Problem:** Im Assembly-STL sind Bodies nicht direkt in `root.bRepBodies`.
Sub-Komponenten können 2-3 Ebenen tief verschachtelt sein (z.B. ESP32 Feather hat 52 Sub-Occurrences).

**Lösung:** Rekursiv durch den Occurrence-Baum traversieren:
```python
def find_body_recursive(occ, name):
    for body in occ.component.bRepBodies:
        if name in body.name:
            return body, occ
    for sub in occ.childOccurrences:
        result = find_body_recursive(sub, name)
        if result:
            return result
    return None
```

---

## 9. World-Koordinaten von Occurrences via Transform

**Problem:** Die Koordinaten eines Bodies in einer Sub-Occurrence sind lokal zur Komponente,
nicht im Welt-Koordinatensystem.

**Lösung:** Über die Occurrence-Transform-Kette multiplizieren:
```python
def get_world_transform(occ):
    t = occ.transform
    parent = occ.assemblyContext
    while parent is not None:
        t2 = parent.transform
        t2.transformBy(t)
        t = t2
        parent = parent.assemblyContext
    return t
```

---

## 10. `sketches.add()` auf einer Konstruktionsebene bei z=0 → Standard-XY-Ebene verwenden

**Problem:** `constructionPlanes.createInput().setByOffset(..., 0.0)` kann Probleme machen.

**Lösung:** Bei z=0 direkt `comp.xYConstructionPlane` verwenden statt einer Offset-Ebene:
```python
def zplane(comp, z_cm):
    if abs(z_cm) < 1e-8:
        return comp.xYConstructionPlane
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane,
                   adsk.core.ValueInput.createByReal(z_cm))
    return comp.constructionPlanes.add(pi)
```

---

## 11. Export: STL-Dateipfad ohne `.stl`-Endung angeben

**Problem:** `exportManager.createSTLExportOptions(body, filepath)` fügt `.stl` automatisch
an. Wenn man den Pfad bereits mit `.stl` übergibt, entsteht `datei.stl.stl`.

**Lösung:** Pfad ohne Endung übergeben:
```python
# RICHTIG
em.createSTLExportOptions(body, '/tmp/Unterschale')    # → Unterschale.stl
# FALSCH
em.createSTLExportOptions(body, '/tmp/Unterschale.stl') # → Unterschale.stl.stl
```

---

## 12. MCP-Script-Ausführung: `run(_context)` als Einstiegspunkt

Alle Scripts die über den MCP-Server ausgeführt werden, müssen eine `run(_context)`
Funktion als Einstiegspunkt haben:

```python
def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    vp   = app.activeViewport
    # ... Script-Logik hier
```

---

*Letzte Aktualisierung: 2026-05-28*
