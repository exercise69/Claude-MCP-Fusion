"""
fusion_oberschale_v3.py — Oberschale mit Spiess-Stil Eck-Schnapp-Aufnahmen.

Passend zu fusion_unterschale_v3_1.py.

Änderungen gegenüber v2:
  - Snap-Fenster (clip windows) ersetzt durch 4 Eck-Nuten
  - Eck-Nuten empfangen die Eck-Protrusions der Unterschale
  - Einführschräge (lead-in) an jedem Eckeintritt
  - Entfernt: clip_w, clip_h, clip_p
  - Neu: snap_d, snap_h (gemeinsam mit Unterschale_v3_1)

Geometrie der Eck-Nut:
  nd = snap_d - lip_gap + 0.15mm  → Tiefe in die Wand
  ni = lip_gap + 0.10mm           → Tiefe in den Hohlraum
  lead-in: 0.4mm breitere Öffnung am Eingang (Z = lip_tip)
"""
import sys
sys.path.append('/path/to/Fusion360Scripts')
import f360_helpers as f
import adsk.core, adsk.fusion


def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. FUSION USER PARAMETERS ────────────────────────────────────────
    # --- Gemeinsame Gehäuse-Parameter ---
    f.set_param(des, 'wall',      2.5,   'Wandstaerke mm')
    f.set_param(des, 'clearance', 0.6,   'Luft um PCB-Stack mm')
    f.set_param(des, 'fillet_r',  2.0,   'Verrundungsradius Kanten mm')
    f.set_param(des, 'split_z',   22.0,  'Trennlinie Unter-/Oberschale mm')

    # --- Steckzunge (gemeinsam) ---
    f.set_param(des, 'lip_h',    4.0,   'Hoehe Steckzunge mm')
    f.set_param(des, 'lip_gap',  0.25,  'Toleranzspiel Steckzunge mm')

    # --- Eck-Schnapp-Clips (gemeinsam mit Unterschale_v3_1) ---
    f.set_param(des, 'snap_d',   0.6,   'Eck-Clip Ueberstand mm')
    f.set_param(des, 'snap_h',   1.5,   'Eck-Clip Eingriffshöhe mm')

    # --- Oberschale-spezifisch ---
    f.set_param(des, 'os_clear',  10.0,  'Luft ueber hoeherem Bauteil mm')
    f.set_param(des, 'rs485_y0',   5.0,  'RS485-Ausgang Y-Unterkante mm')
    f.set_param(des, 'rs485_y1',  18.0,  'RS485-Ausgang Y-Oberkante mm')
    f.set_param(des, 'rs485_z0',  23.0,  'RS485-Ausgang Z-Unterkante mm')
    f.set_param(des, 'rs485_z1',  32.0,  'RS485-Ausgang Z-Oberkante mm')
    f.set_param(des, 'mount_d',   4.2,   'M4-Montageloch Durchmesser mm')
    f.set_param(des, 'mount_x0',  5.4,   'Montageloch X-Position links mm')
    f.set_param(des, 'mount_x1', 44.2,   'Montageloch X-Position rechts mm')

    # ── 2. PARAMETER EINLESEN ────────────────────────────────────────────
    wall      = f.get_param_cm(des, 'wall')
    clearance = f.get_param_cm(des, 'clearance')
    fillet_r  = f.get_param_cm(des, 'fillet_r')
    split_z   = f.get_param_cm(des, 'split_z')

    lip_h    = f.get_param_cm(des, 'lip_h')
    lip_gap  = f.get_param_cm(des, 'lip_gap')

    snap_d   = f.get_param_cm(des, 'snap_d')
    snap_h   = f.get_param_cm(des, 'snap_h')

    os_clear  = f.get_param_cm(des, 'os_clear')
    rs485_y0  = f.get_param_cm(des, 'rs485_y0')
    rs485_y1  = f.get_param_cm(des, 'rs485_y1')
    rs485_z0  = f.get_param_cm(des, 'rs485_z0')
    rs485_z1  = f.get_param_cm(des, 'rs485_z1')
    mount_d   = f.get_param_cm(des, 'mount_d')
    mount_x0  = f.get_param_cm(des, 'mount_x0')
    mount_x1  = f.get_param_cm(des, 'mount_x1')

    # ── 3. HARDWARE-KONSTANTEN ────────────────────────────────────────────
    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)
    pcb_top_z = f.cm(34.0)
    pcb_cy    = (asm_y0 + asm_y1) / 2

    # ── 4. ABGELEITETE GEOMETRIE ──────────────────────────────────────────
    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance

    iz1 = pcb_top_z + os_clear

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz1 = iz1 + wall

    # Eck-Nut-Geometrie (passend zu Unterschale_v3_1 Protrusions)
    # nd: wie weit die Nut in die Wand geht (nach außen von ix0/ix1/iy0/iy1)
    # ni: wie weit die Nut in den Hohlraum geht (nach innen)
    nd    = snap_d - lip_gap + f.cm(0.15)   # 0.6 - 0.25 + 0.15 = 0.5mm
    ni    = lip_gap + f.cm(0.10)            # 0.25 + 0.10 = 0.35mm
    li    = f.cm(0.40)                      # Lead-in Übermaß

    nz0   = split_z + lip_h - snap_h - f.cm(0.1)   # Nut-Unterkante
    nz1   = split_z + lip_h + f.cm(0.1)             # Nut-Oberkante (Lip-Spitze)
    li_z0 = split_z + lip_h - f.cm(0.35)            # Lead-in nur am Eingang

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    for name in ('Oberschale', 'Oberschale_v2'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Oberschale_v3')

    print('Erstelle Oberschale_v3 ...')
    os_occ = f.new_component(root, 'Oberschale_v3')
    oc = os_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(oc, ox0, oy0, split_z, ox1, oy1, oz1)
    shell.name = 'Oberschale_v3'
    f.fillet_z_edges(oc, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen (nimmt Steckzunge auf)
    f.cut(oc, shell, f.box(oc, ix0, iy0, split_z - f.cm(0.1),
                                ix1, iy1, iz1 + f.cm(0.1)))
    print('  Innenraum ausgehöhlt')

    # 3. RS485-Kabelausgang (rechte Wand)
    f.cut(oc, shell, f.box(oc,
        ix1 - f.cm(0.1), rs485_y0, rs485_z0,
        ix1 + wall + f.cm(0.1), rs485_y1, rs485_z1))
    print('  RS485-Kabelausgang  ('
          + str(round((rs485_y1-rs485_y0)*10,1)) + 'mm × '
          + str(round((rs485_z1-rs485_z0)*10,1)) + 'mm)')

    # 4. Eck-Schnapp-Nuten (4 Ecken, passend zu Unterschale_v3_1)
    #
    #  Jede Ecke besteht aus 2 Schnitten:
    #    a) Haupt-Nut: exakte Passform für die Protrusion
    #    b) Lead-in:   am Eingang (Z ≈ lip_h) etwas breiter → leichtere Montage
    #
    #  (sx, sy): +1 = Nut geht in positive Richtung (außen), -1 = negative
    #
    corners = [
        (ix0, iy0, -1, -1),   # Front-links
        (ix1, iy0, +1, -1),   # Front-rechts
        (ix0, iy1, -1, +1),   # Hinten-links
        (ix1, iy1, +1, +1),   # Hinten-rechts
    ]
    for cx, cy, sx, sy in corners:
        # Haupt-Nut
        nx0 = (cx - nd) if sx < 0 else (cx - ni)
        nx1 = (cx + ni) if sx < 0 else (cx + nd)
        ny0 = (cy - nd) if sy < 0 else (cy - ni)
        ny1 = (cy + ni) if sy < 0 else (cy + nd)
        f.cut(oc, shell, f.box(oc, nx0, ny0, nz0, nx1, ny1, nz1))

        # Lead-in: am Eingang (Lip-Spitze) nach außen erweitern
        li_nx0 = (cx - nd - li) if sx < 0 else nx0
        li_nx1 = nx1 if sx < 0 else (cx + nd + li)
        li_ny0 = (cy - nd - li) if sy < 0 else ny0
        li_ny1 = ny1 if sy < 0 else (cy + nd + li)
        f.cut(oc, shell, f.box(oc, li_nx0, li_ny0, li_z0, li_nx1, li_ny1, nz1))

    print('  Eck-Schnapp-Nuten (4×)  + Lead-in')

    # 5. Montagelöcher M4 durch Deckel
    for mx in [mount_x0, mount_x1]:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - f.cm(0.1), oz1 + f.cm(0.1), mount_d))
    print('  Montagelöcher M4  (Ø' + str(round(mount_d*10, 1)) + 'mm × 2)')

    print('✓ Oberschale_v3 fertig!  ' + f.bbox_str(shell))
    print('  Snap-Clips: 4 Ecken, Spiess-Stil')
    print('  Parameter: Modify → Change Parameters')
