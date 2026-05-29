"""
fusion_oberschale.py — Erstellt die Oberschale des SolarLoader-Gehäuses in Fusion 360.
Verwendet f360_helpers für alle Basis-Operationen.
"""
import sys
sys.path.append('/path/to/Fusion360Scripts')
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

    # 5. Montage-Löcher M4 durch Deckel
    for mx in mount_xs:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - f.cm(0.1), oz1 + f.cm(0.1), mount_d))
    print("  Montage-Löcher fertig")

    print(f"✓ Oberschale fertig!  {f.bbox_str(shell)}")
