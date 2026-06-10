"""
fusion_oberschale.py — Erstellt die Oberschale des SolarLoader-Gehäuses in Fusion 360.
Verwendet f360_helpers für alle Basis-Operationen.
"""
import os, sys

def _f360_root():
    """Wurzel des Fusion360Scripts-Repos finden (kein hardwired Pfad)."""
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

import adsk.core, adsk.fusion

def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── Parameter ───────────────────────────────────────────────────────
    wall      = f.cm(2.5)
    fillet_r  = f.cm(2.0)
    split_z   = f.cm(22.0)
    clearance = f.cm(0.6)

    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)
    top_z = f.cm(34.0)

    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance
    iz1 = top_z + f.cm(10.0)           # = 44.0mm  (10mm Luft über Bauteilen)

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz1 = iz1 + wall                   # = 46.5mm

    pcb_cy = (asm_y0 + asm_y1) / 2

    # RS485-Kabelausgang (rechte Wand)
    rs485_y0, rs485_y1 = f.cm(5.0),  f.cm(18.0)
    rs485_z0, rs485_z1 = f.cm(23.0), f.cm(32.0)

    # Montage-Löcher im Deckel (M4) — symmetrisch, je 9.7mm vom Rand
    mount_xs = [f.cm(5.4), f.cm(44.2)]
    mount_d  = f.cm(4.2)

    # ── OBERSCHALE ERSTELLEN ─────────────────────────────────────────────
    print("Erstelle Oberschale ...")
    os_occ = f.new_component(root, "Oberschale")
    oc = os_occ.component

    # 1. Außenhülle (split_z bis oz1)
    shell = f.box(oc, ox0, oy0, split_z, ox1, oy1, oz1)
    shell.name = "Oberschale"
    print("  Außenhülle erstellt")

    # 2. Vertikale Kanten verrunden (R=2mm)
    f.fillet_z_edges(oc, shell, fillet_r)
    print("  Verrundung fertig")

    # 3. Innenraum aushöhlen (nimmt Steckzunge der Unterschale auf)
    f.cut(oc, shell, f.box(oc, ix0, iy0, split_z - f.cm(0.1),
                                ix1, iy1, iz1 + f.cm(0.1)))
    print("  Innenraum ausgehöhlt")

    # 4. RS485-Kabelausgang (rechte Wand)
    f.cut(oc, shell, f.box(oc,
        ix1 - f.cm(0.1), rs485_y0, rs485_z0,
        ix1 + wall + f.cm(0.1), rs485_y1, rs485_z1))
    print("  RS485-Ausgang fertig")

    # 5. Schnapp-Fenster in Innenwände (passend zu Clips der Unterschale)
    # Maße müssen zu Clips passen: clip_p=0.5mm, clip_w=6mm, clip_h=2mm
    # Fenster: Breite+0.4mm Spiel, Höhe+0.5mm Spiel, Tiefe = clip_p+lip_gap+0.1mm
    clip_p    = f.cm(0.5)
    lip_gap   = f.cm(0.25)
    clip_w    = f.cm(6.0)
    clip_h    = f.cm(2.0)
    clip_z1   = f.cm(22.0) + f.cm(4.0)          # split_z + lip_h = 26mm
    clip_z0   = clip_z1 - clip_h                 # = 24mm
    pw        = clip_w + f.cm(0.4)               # Fensterbreite mit Spiel
    ph        = clip_h + f.cm(0.5)               # Fensterhöhe mit Spiel
    pd        = clip_p + lip_gap + f.cm(0.1)     # Tiefe = 0.85mm

    cx_lip = (ix0 + ix1) / 2
    cy_lip = (iy0 + iy1) / 2
    pz0 = clip_z0 - f.cm(0.1)   # Fenster etwas tiefer starten (Montagespiel)
    pz1 = pz0 + ph

    # Nur die langen Seiten (vorne + hinten, Y-Richtung)
    # Vordere Innenwand
    f.cut(oc, shell, f.box(oc,
        cx_lip - pw/2, iy0 - pd,        pz0,
        cx_lip + pw/2, iy0 + f.cm(0.1), pz1))
    # Hintere Innenwand
    f.cut(oc, shell, f.box(oc,
        cx_lip - pw/2, iy1 - f.cm(0.1), pz0,
        cx_lip + pw/2, iy1 + pd,        pz1))
    print("  Schnapp-Fenster fertig")

    # 6. Montage-Löcher M4 durch Deckel
    for mx in mount_xs:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - f.cm(0.1), oz1 + f.cm(0.1), mount_d))
    print("  Montage-Löcher fertig")

    print(f"✓ Oberschale fertig!  {f.bbox_str(shell)}")
