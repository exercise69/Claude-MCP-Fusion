"""
f360_helpers.py — Wiederverwendbare Hilfsfunktionen für Fusion 360 Python-Scripts
Ablageort: /Users/upi/Documents/Eigene Programme/Programs/Fusion360Scripts/

Verwendung am Anfang jedes Scripts:
    import sys
    sys.path.append('/Users/upi/Documents/Eigene Programme/Programs/Fusion360Scripts')
    import f360_helpers as f

    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    vp   = app.activeViewport
"""

import math
import adsk.core
import adsk.fusion


# ─────────────────────────────────────────────────────────────
# EINHEITEN
# ─────────────────────────────────────────────────────────────

def cm(mm):
    """Millimeter → Centimeter (Fusion arbeitet intern in cm)."""
    return mm * 0.1

def mm(cm_val):
    """Centimeter → Millimeter."""
    return cm_val * 10.0


# ─────────────────────────────────────────────────────────────
# KONSTRUKTIONSEBENEN
# ─────────────────────────────────────────────────────────────

def zplane(comp, z_cm):
    """
    Konstruktionsebene parallel zur XY-Ebene bei Höhe z_cm (in cm).
    Bei z=0 wird die Standard-XY-Ebene zurückgegeben (kein neues Feature).
    """
    if abs(z_cm) < 1e-8:
        return comp.xYConstructionPlane
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane,
                   adsk.core.ValueInput.createByReal(z_cm))
    return comp.constructionPlanes.add(pi)


# ─────────────────────────────────────────────────────────────
# GRUNDKÖRPER (geben immer einen neuen BRepBody zurück)
# ─────────────────────────────────────────────────────────────

def box(comp, x0, y0, z0, x1, y1, z1):
    """
    Erstellt einen Quader als neuen Body in comp.
    Alle Koordinaten in cm.
    """
    sk = comp.sketches.add(zplane(comp, z0))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0, y0, 0),
        adsk.core.Point3D.create(x1, y1, 0))
    ei = comp.features.extrudeFeatures.createInput(
        sk.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False,
        adsk.core.ValueInput.createByReal(z1 - z0))
    return comp.features.extrudeFeatures.add(ei).bodies.item(0)


def cylinder(comp, cx, cy, z0, z1, diameter):
    """
    Erstellt einen Zylinder als neuen Body in comp.
    cx, cy = Mittelpunkt; z0..z1 = Höhenbereich; diameter = Durchmesser. Alles in cm.
    """
    sk = comp.sketches.add(zplane(comp, z0))
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(cx, cy, 0), diameter / 2.0)
    ei = comp.features.extrudeFeatures.createInput(
        sk.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False,
        adsk.core.ValueInput.createByReal(z1 - z0))
    return comp.features.extrudeFeatures.add(ei).bodies.item(0)


# ─────────────────────────────────────────────────────────────
# BOOLEAN-OPERATIONEN
# ─────────────────────────────────────────────────────────────

def cut(comp, target, tool):
    """
    Subtrahiert tool-Body von target-Body (CutFeatureOperation).
    tool wird danach gelöscht (isKeepToolBodies=False).
    """
    tc = adsk.core.ObjectCollection.create()
    tc.add(tool)
    ci = comp.features.combineFeatures.createInput(target, tc)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci)


def join(comp, target, tool):
    """
    Vereinigt tool-Body mit target-Body (JoinFeatureOperation).
    Funktioniert nur wenn die Körper sich berühren oder überschneiden.
    tool wird danach gelöscht.
    """
    tc = adsk.core.ObjectCollection.create()
    tc.add(tool)
    ci = comp.features.combineFeatures.createInput(target, tc)
    ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci)


def intersect(comp, target, tool):
    """
    Behält nur den gemeinsamen Bereich von target und tool (IntersectFeatureOperation).
    tool wird danach gelöscht.
    """
    tc = adsk.core.ObjectCollection.create()
    tc.add(tool)
    ci = comp.features.combineFeatures.createInput(target, tc)
    ci.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci)


# ─────────────────────────────────────────────────────────────
# KANTEN: VERRUNDUNGEN & FASEN
# ─────────────────────────────────────────────────────────────

def _collect_edges_by_direction(body, z_parallel, threshold=0.99):
    """
    Interne Hilfsfunktion: Sammelt Kanten nach Richtung.
    z_parallel=True  → nur vertikale (Z-parallele) Kanten
    z_parallel=False → nur horizontale (XY-parallele) Kanten
    """
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        g = e.geometry
        if isinstance(g, adsk.core.Line3D):
            sp, ep = g.startPoint, g.endPoint
            dx = ep.x - sp.x
            dy = ep.y - sp.y
            dz = ep.z - sp.z
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            if length < 1e-8:
                continue
            cos_z = abs(dz / length)
            if z_parallel and cos_z > threshold:
                edges.add(e)
            elif not z_parallel and cos_z < (1.0 - threshold):
                edges.add(e)
    return edges


def fillet_z_edges(comp, body, r_cm):
    """
    Verrundet alle vertikalen (Z-parallelen) Kanten eines Körpers mit Radius r_cm.
    Typischer Anwendungsfall: Außenkanten eines Gehäuses abrunden.
    Gibt die Anzahl der verrundeten Kanten zurück (0 = nichts getan).
    """
    edges = _collect_edges_by_direction(body, z_parallel=True)
    if edges.count == 0:
        return 0
    fi = comp.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(
        edges, adsk.core.ValueInput.createByReal(r_cm), True)
    comp.features.filletFeatures.add(fi)
    return edges.count


def fillet_h_edges(comp, body, r_cm):
    """
    Verrundet alle horizontalen (XY-parallelen) Kanten eines Körpers mit Radius r_cm.
    Typischer Anwendungsfall: Deckel-/Bodenkanten abrunden.
    Gibt die Anzahl der verrundeten Kanten zurück (0 = nichts getan).
    """
    edges = _collect_edges_by_direction(body, z_parallel=False)
    if edges.count == 0:
        return 0
    fi = comp.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(
        edges, adsk.core.ValueInput.createByReal(r_cm), True)
    comp.features.filletFeatures.add(fi)
    return edges.count


def fillet_all_edges(comp, body, r_cm):
    """
    Verrundet ALLE Kanten eines Körpers mit Radius r_cm.
    Vorsicht: kann bei komplexen Körpern fehlschlagen.
    """
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        edges.add(e)
    if edges.count == 0:
        return 0
    fi = comp.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(
        edges, adsk.core.ValueInput.createByReal(r_cm), True)
    comp.features.filletFeatures.add(fi)
    return edges.count


def chamfer_z_edges(comp, body, dist_cm):
    """
    Fasst alle vertikalen (Z-parallelen) Kanten eines Körpers ab.
    Alternative zu fillet_z_edges, z.B. für 3D-Druck-Druckbett-Haftung.
    Gibt die Anzahl der gefasten Kanten zurück (0 = nichts getan).
    """
    edges = _collect_edges_by_direction(body, z_parallel=True)
    if edges.count == 0:
        return 0
    ci = comp.features.chamferFeatures.createInput(edges, True)
    ci.setToEqualDistance(adsk.core.ValueInput.createByReal(dist_cm))
    comp.features.chamferFeatures.add(ci)
    return edges.count


# ─────────────────────────────────────────────────────────────
# KOMPONENTEN-VERWALTUNG
# ─────────────────────────────────────────────────────────────

def new_component(root, name):
    """
    Legt eine neue leere Komponente im root-Component an.
    Gibt das Occurrence-Objekt zurück (occurrence.component = die Komponente).
    """
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ


def find_occurrence(root, name):
    """
    Sucht eine Occurrence nach dem Komponenten-Namen (direkte Kinder von root).
    Gibt das Occurrence-Objekt zurück, oder None wenn nicht gefunden.
    """
    for occ in root.occurrences:
        if occ.component.name == name:
            return occ
    return None


def delete_component(root, name):
    """
    Löscht eine Komponente (und alle ihre Features) nach Namen.
    Gibt True zurück wenn gefunden und gelöscht, sonst False.
    """
    occ = find_occurrence(root, name)
    if occ:
        occ.deleteMe()
        return True
    return False


# ─────────────────────────────────────────────────────────────
# SICHTBARKEIT & TRANSPARENZ
# ─────────────────────────────────────────────────────────────

def set_opacity(root, name, opacity):
    """
    Setzt die Opazität aller Bodies einer Komponente (0.0 = unsichtbar, 1.0 = voll opak).
    Gibt True zurück wenn die Komponente gefunden wurde.
    """
    occ = find_occurrence(root, name)
    if occ:
        for body in occ.component.bRepBodies:
            body.opacity = opacity
        return True
    return False


def show(root, name):
    """Blendet eine Komponente ein (isLightBulbOn = True)."""
    occ = find_occurrence(root, name)
    if occ:
        occ.isLightBulbOn = True
        return True
    return False


def hide(root, name):
    """Blendet eine Komponente aus (isLightBulbOn = False)."""
    occ = find_occurrence(root, name)
    if occ:
        occ.isLightBulbOn = False
        return True
    return False


# ─────────────────────────────────────────────────────────────
# USER-PARAMETER
# ─────────────────────────────────────────────────────────────

def set_param(des, name, value_mm, comment=''):
    """
    Legt einen User-Parameter an oder aktualisiert ihn.
    value_mm: Wert in Millimeter.
    Gibt das UserParameter-Objekt zurück.

    Beispiel:
        set_param(des, 'wall', 2.5, 'Wandstärke mm')
        set_param(des, 'clearance', 0.6)
    """
    params = des.userParameters
    p = params.itemByName(name)
    val = adsk.core.ValueInput.createByString(f'{value_mm} mm')
    if p:
        p.expression = f'{value_mm} mm'
        return p
    else:
        return params.add(name, val, 'mm', comment)


def get_param_mm(des, name):
    """
    Gibt den aktuellen Wert eines User-Parameters in Millimeter zurück.
    Gibt None zurück wenn der Parameter nicht existiert.
    """
    p = des.userParameters.itemByName(name)
    if p is None:
        return None
    return p.value * 10.0  # Fusion speichert intern in cm


def get_param_cm(des, name):
    """
    Gibt den aktuellen Wert eines User-Parameters in Centimeter zurück.
    Gibt None zurück wenn der Parameter nicht existiert.
    """
    p = des.userParameters.itemByName(name)
    if p is None:
        return None
    return p.value  # Fusion speichert intern in cm


# ─────────────────────────────────────────────────────────────
# KAMERA & SCREENSHOTS
# ─────────────────────────────────────────────────────────────

def set_camera(vp, eye, target, up=(0, 0, 1)):
    """
    Setzt die Kameraposition.
    eye, target = (x, y, z) Tupel in cm.
    up = Aufwärts-Vektor, Standard: Z-Achse.
    """
    cam = vp.camera
    cam.eye    = adsk.core.Point3D.create(*eye)
    cam.target = adsk.core.Point3D.create(*target)
    cam.upVector = adsk.core.Vector3D.create(*up)
    cam.isFitView = False
    vp.camera = cam
    adsk.doEvents()
    adsk.doEvents()


def fit_view(vp):
    """Passt die Ansicht an alle sichtbaren Objekte an."""
    cam = vp.camera
    cam.isFitView = True
    vp.camera = cam
    adsk.doEvents()
    adsk.doEvents()


def screenshot(vp, filepath, eye=None, target=None, up=(0, 0, 1),
               width=1400, height=1000):
    """
    Macht einen Screenshot und speichert ihn unter filepath.
    Wenn eye/target angegeben: Kamera wird zuerst gesetzt.
    Gibt den Dateipfad zurück.
    """
    if eye is not None and target is not None:
        set_camera(vp, eye, target, up)
    vp.saveAsImageFile(filepath, width, height)
    return filepath


def screenshot_fit(vp, filepath, width=1400, height=1000):
    """Screenshot nach automatischem Fit-to-View."""
    fit_view(vp)
    vp.saveAsImageFile(filepath, width, height)
    return filepath


# ─────────────────────────────────────────────────────────────
# EXPORT (STL / STEP / 3MF)
# ─────────────────────────────────────────────────────────────

def export_stl(des, body, filepath, refinement='high'):
    """
    Exportiert einen BRepBody als STL-Datei.

    des:        adsk.fusion.Design-Objekt
    body:       BRepBody der exportiert werden soll
    filepath:   Ausgabepfad (ohne .stl — wird ggf. automatisch angehängt)
    refinement: Netzqualität — 'low' | 'medium' | 'high'  (Standard: 'high')

    Gibt den Dateipfad zurück.

    Beispiel:
        f.export_stl(des, shell, '/tmp/Unterschale')
        f.export_stl(des, shell, '/tmp/Oberschale', refinement='medium')
    """
    levels = {
        'low':    adsk.fusion.MeshRefinementSettings.MeshRefinementLow,
        'medium': adsk.fusion.MeshRefinementSettings.MeshRefinementMedium,
        'high':   adsk.fusion.MeshRefinementSettings.MeshRefinementHigh,
    }
    em = des.exportManager
    opts = em.createSTLExportOptions(body, filepath)
    opts.meshRefinement = levels.get(refinement,
                                     adsk.fusion.MeshRefinementSettings.MeshRefinementHigh)
    opts.sendToPrintUtility = False
    em.execute(opts)
    return filepath


def export_step(des, comp, filepath):
    """
    Exportiert eine Komponente als STEP-Datei (.step).

    des:      adsk.fusion.Design-Objekt
    comp:     adsk.fusion.Component der exportiert werden soll
    filepath: Ausgabepfad (ohne .step)

    Gibt den Dateipfad zurück.

    Beispiel:
        f.export_step(des, oc, '/tmp/Oberschale')
    """
    em = des.exportManager
    opts = em.createSTEPExportOptions(filepath, comp)
    em.execute(opts)
    return filepath


def export_3mf(des, comp, filepath):
    """
    Exportiert eine Komponente als 3MF-Datei (modernes 3D-Druck-Format).
    3MF unterstützt Farben, Materialien und mehrere Bodies in einer Datei.

    des:      adsk.fusion.Design-Objekt
    comp:     adsk.fusion.Component der exportiert werden soll
    filepath: Ausgabepfad (ohne .3mf)

    Gibt den Dateipfad zurück.

    Beispiel:
        f.export_3mf(des, root, '/tmp/SolarLoader_komplett')
    """
    em = des.exportManager
    opts = em.create3MFExportOptions(filepath, comp)
    em.execute(opts)
    return filepath


def export_stl_all_components(des, root, output_dir):
    """
    Exportiert alle sichtbaren Komponenten als separate STL-Dateien.
    Dateiname = Komponentenname + '.stl'.

    des:        adsk.fusion.Design-Objekt
    root:       root-Component
    output_dir: Zielordner (muss existieren)

    Gibt eine Liste der erstellten Dateipfade zurück.

    Beispiel:
        paths = f.export_stl_all_components(des, root, '/tmp/export')
    """
    import os
    exported = []
    for occ in root.occurrences:
        if not occ.isLightBulbOn:
            continue
        comp = occ.component
        # Jeden Body separat exportieren
        for body in comp.bRepBodies:
            safe_name = body.name.replace(' ', '_').replace('/', '-')
            path = os.path.join(output_dir, safe_name)
            export_stl(des, body, path)
            exported.append(path + '.stl')
            print(f"  Exportiert: {path}.stl")
    return exported


# ─────────────────────────────────────────────────────────────
# ANALYSE & DEBUGGING
# ─────────────────────────────────────────────────────────────

def bbox_mm(body):
    """
    Gibt die Bounding Box eines Körpers als Dict zurück (Werte in mm).
    Keys: xmin, xmax, ymin, ymax, zmin, zmax, width, depth, height
    """
    bb = body.boundingBox
    mi, ma = bb.minPoint, bb.maxPoint
    return {
        'xmin': mi.x * 10, 'xmax': ma.x * 10,
        'ymin': mi.y * 10, 'ymax': ma.y * 10,
        'zmin': mi.z * 10, 'zmax': ma.z * 10,
        'width':  (ma.x - mi.x) * 10,
        'depth':  (ma.y - mi.y) * 10,
        'height': (ma.z - mi.z) * 10,
    }


def bbox_str(body):
    """Gibt die Bounding Box als lesbaren String zurück (in mm)."""
    b = bbox_mm(body)
    return (f"X={b['xmin']:.1f}..{b['xmax']:.1f}  "
            f"Y={b['ymin']:.1f}..{b['ymax']:.1f}  "
            f"Z={b['zmin']:.1f}..{b['zmax']:.1f} mm")


def list_bodies(root):
    """
    Gibt eine Übersicht aller Bodies (Root + Komponenten) auf der Konsole aus.
    Nützlich zur Fehlersuche.
    """
    print(f"=== Root Bodies ({root.bRepBodies.count}) ===")
    for b in root.bRepBodies:
        print(f"  '{b.name}'  {bbox_str(b)}")

    print(f"=== Komponenten ({root.occurrences.count}) ===")
    for occ in root.occurrences:
        c = occ.component
        vis = "✓" if occ.isLightBulbOn else "–"
        print(f"  {vis} '{c.name}'  ({c.bRepBodies.count} Bodies)")
        for b in c.bRepBodies:
            print(f"      '{b.name}'  {bbox_str(b)}")
