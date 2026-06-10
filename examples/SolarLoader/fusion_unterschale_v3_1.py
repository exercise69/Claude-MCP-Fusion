"""
fusion_unterschale_v3_1.py — Unterschale mit Spiess-Stil Eck-Schnapp-Clips.

Änderungen gegenüber v3:
  - Clip-Mechanismus ersetzt: statt 2 zentraler Cantilever-Tabs
    → 4 Eck-Protrusions (Spiess-Stil)
  - Clip flexiert horizontal (XY-Ebene) statt vertikal
    → Layerlinien stehen senkrecht zur Biegung = robuster
  - Neue Parameter: snap_d (Überstandstiefe), snap_h (Eingriffshöhe)
  - Entfernt: clip_w, clip_h, clip_ramp, clip_p

Geometrie-Prinzip:
  An jedem der 4 Lip-Ecken sitzt ein snap_d × snap_d × snap_h großer
  Quader-Vorsprung. Die Oberschale (v3) hat passende Eck-Nuten.
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

    # ── 1. FUSION USER PARAMETERS ────────────────────────────────────────
    # --- Gehäuse ---
    f.set_param(des, 'wall',      2.5,   'Wandstaerke mm')
    f.set_param(des, 'clearance', 0.6,   'Luft um PCB-Stack mm')
    f.set_param(des, 'fillet_r',  2.0,   'Verrundungsradius Kanten mm')
    f.set_param(des, 'split_z',   22.0,  'Trennlinie Unter-/Oberschale mm')
    f.set_param(des, 'lipo_h',    0.0,   'LiPo-Hoehenaufschlag mm (0 = kein LiPo)')

    # --- Steckzunge ---
    f.set_param(des, 'lip_h',    4.0,   'Hoehe Steckzunge mm')
    f.set_param(des, 'lip_wall', 1.6,   'Wandstaerke Steckzunge mm')
    f.set_param(des, 'lip_gap',  0.25,  'Toleranzspiel Steckzunge mm')

    # --- Eck-Schnapp-Clips (Spiess-Stil) ---
    f.set_param(des, 'snap_d',   0.6,   'Eck-Clip Ueberstand mm')
    f.set_param(des, 'snap_h',   1.5,   'Eck-Clip Eingriffshöhe mm')

    # --- Display-Mulde ---
    f.set_param(des, 'recess_d',  1.3,  'Tiefe Display-Mulde von innen mm')

    # --- USB-C Schlitz ---
    f.set_param(des, 'usbc_half', 5.0,  'USB-C Schlitz Halbbreite mm')
    f.set_param(des, 'usbc_z1',   4.5,  'USB-C Schlitz Z-Oberkante mm')

    # --- Taster ---
    f.set_param(des, 'btn_d',    2.5,   'Taster-Stiftloch Durchmesser mm')

    # --- SD-Karte ---
    f.set_param(des, 'sd_y0',   3.0,   'SD-Schlitz Y-Unterkante mm')
    f.set_param(des, 'sd_y1',   17.5,  'SD-Schlitz Y-Oberkante mm')
    f.set_param(des, 'sd_z0',   9.3,   'SD-Schlitz Z-Unterkante mm')
    f.set_param(des, 'sd_z1',   14.0,  'SD-Schlitz Z-Oberkante mm')

    # --- Standoffs + Board-Schrauben ---
    f.set_param(des, 'so_od',   5.0,   'Standoff Aussendurchmesser mm')
    f.set_param(des, 'so_h',    2.5,   'Standoff Hoehe mm')
    f.set_param(des, 'screw_d', 2.2,   'M2-Durchgangsloch mm')
    f.set_param(des, 'csk_d',   4.0,   'M2-Senkkopf Durchmesser mm')
    f.set_param(des, 'csk_dep', 1.5,   'M2-Senkkopf Tiefe mm')

    # ── 2. PARAMETER EINLESEN ────────────────────────────────────────────
    wall      = f.get_param_cm(des, 'wall')
    clearance = f.get_param_cm(des, 'clearance')
    fillet_r  = f.get_param_cm(des, 'fillet_r')
    split_z   = f.get_param_cm(des, 'split_z')
    lipo_h    = f.get_param_cm(des, 'lipo_h')

    lip_h    = f.get_param_cm(des, 'lip_h')
    lip_wall = f.get_param_cm(des, 'lip_wall')
    lip_gap  = f.get_param_cm(des, 'lip_gap')

    snap_d   = f.get_param_cm(des, 'snap_d')
    snap_h   = f.get_param_cm(des, 'snap_h')

    recess_d  = f.get_param_cm(des, 'recess_d')
    usbc_half = f.get_param_cm(des, 'usbc_half')
    usbc_z1   = f.get_param_cm(des, 'usbc_z1')
    btn_d     = f.get_param_cm(des, 'btn_d')

    sd_y0 = f.get_param_cm(des, 'sd_y0')
    sd_y1 = f.get_param_cm(des, 'sd_y1')
    sd_z0 = f.get_param_cm(des, 'sd_z0')
    sd_z1 = f.get_param_cm(des, 'sd_z1')

    so_od   = f.get_param_cm(des, 'so_od')
    so_h    = f.get_param_cm(des, 'so_h')
    screw_d = f.get_param_cm(des, 'screw_d')
    csk_d   = f.get_param_cm(des, 'csk_d')
    csk_dep = f.get_param_cm(des, 'csk_dep')

    # ── 3. HARDWARE-KONSTANTEN ────────────────────────────────────────────
    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)
    pcb_z0  = f.cm(-1.94)
    pcb_cy  = (asm_y0 + asm_y1) / 2

    disp_w  = f.cm(25.5);  disp_h  = f.cm(15.4)
    disp_cx = f.cm(26.26); disp_cy = f.cm(11.35)

    recess_x0 = f.cm(4.0);  recess_x1 = f.cm(45.0)
    recess_y0 = f.cm(1.0);  recess_y1 = f.cm(22.0)

    btn_x  = f.cm(7.6)
    btn_ys = [f.cm(4.4), f.cm(11.4), f.cm(18.4)]
    rst_x  = f.cm(44.5);  rst_y = f.cm(11.5)

    so_pos = [(f.cm(2.54),  f.cm(2.54)),
              (f.cm(2.54),  f.cm(20.32)),
              (f.cm(48.26), f.cm(1.84)),
              (f.cm(48.26), f.cm(20.96))]

    # ── 4. ABGELEITETE GEOMETRIE ──────────────────────────────────────────
    iz0 = pcb_z0 - f.cm(0.6)

    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0 = iz0 - wall

    usbc_y0 = pcb_cy - usbc_half
    usbc_y1 = pcb_cy + usbc_half

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    # Vorgänger verstecken
    for name in ('Unterschale', 'Unterschale_v2', 'Unterschale_v3'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Unterschale_v3_1')

    print('Erstelle Unterschale_v3_1 ...')
    us_occ = f.new_component(root, 'Unterschale_v3_1')
    us = us_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z)
    shell.name = 'Unterschale_v3_1'
    f.fillet_z_edges(us, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z + f.cm(0.1)))
    print('  Innenraum ausgehöhlt')

    # 3. Standoffs
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print('  Standoffs')

    # 4. Steckzunge + 4 Eck-Schnapp-Clips (Spiess-Stil)
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap

    # Hohler Lip-Rahmen
    lip = f.box(us, lx0, ly0, split_z, lx1, ly1, split_z + lip_h)
    f.cut(us, lip, f.box(us, lx0 + lip_wall, ly0 + lip_wall,
                              split_z - f.cm(0.1),
                              lx1 - lip_wall, ly1 - lip_wall,
                              split_z + lip_h + f.cm(0.1)))

    # Eck-Protrusions: snap_d × snap_d × snap_h an den 4 Ecken
    # (sx, sy) = Überstand-Richtung: -1 = nach außen in negativer Achse
    snap_z0 = split_z + lip_h - snap_h
    snap_z1 = split_z + lip_h
    for cx, cy, sx, sy in [(lx0, ly0, -1, -1),
                            (lx1, ly0, +1, -1),
                            (lx0, ly1, -1, +1),
                            (lx1, ly1, +1, +1)]:
        bx0 = (cx - snap_d) if sx < 0 else (cx - lip_wall)
        bx1 = (cx + lip_wall) if sx < 0 else (cx + snap_d)
        by0 = (cy - snap_d) if sy < 0 else (cy - lip_wall)
        by1 = (cy + lip_wall) if sy < 0 else (cy + snap_d)
        f.join(us, lip, f.box(us, bx0, by0, snap_z0, bx1, by1, snap_z1))

    f.join(us, shell, lip)
    print('  Steckzunge + 4 Eck-Schnapp-Clips  (snap_d='
          + str(round(snap_d*10, 2)) + 'mm, snap_h='
          + str(round(snap_h*10, 2)) + 'mm)')

    # 5. Display-Mulde von innen
    f.cut(us, shell, f.box(us,
        recess_x0, recess_y0, iz0 - recess_d - f.cm(0.1),
        recess_x1, recess_y1, iz0 + f.cm(0.1)))
    print('  Display-Mulde (Restwand='
          + str(round((wall - recess_d)*10, 1)) + 'mm)')

    # 6. TFT-Fenster
    f.cut(us, shell, f.box(us,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - f.cm(0.1),
        disp_cx + disp_w/2, disp_cy + disp_h/2, oz0 + wall + f.cm(0.1)))
    print('  TFT-Fenster')

    # 7. USB-C-Schlitz
    f.cut(us, shell, f.box(us,
        ox0 - f.cm(0.1), usbc_y0, f.cm(0.0),
        ix0 + f.cm(4.0),  usbc_y1, usbc_z1))
    print('  USB-C-Schlitz')

    # 8. Taster-Stiftlöcher D0/D1/D2 + Reset
    for by in btn_ys:
        f.cut(us, shell, f.cylinder(us,
            btn_x, by, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_d))
    f.cut(us, shell, f.cylinder(us,
        rst_x, rst_y, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_d))
    print('  Taster-Stiftlöcher (D0/D1/D2 + Reset)')

    # 9. SD-Karten-Schlitz
    f.cut(us, shell, f.box(us,
        ix1 - f.cm(0.1), sd_y0, sd_z0,
        ix1 + wall + f.cm(0.1), sd_y1, sd_z1))
    print('  SD-Karten-Schlitz')

    # 10. Board-Schrauben M2
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), oz0 + csk_dep + f.cm(0.1), csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), iz0 + so_h + f.cm(0.1), screw_d))
    print('  Board-Schrauben (M2)')

    print('✓ Unterschale_v3_1 fertig!  ' + f.bbox_str(shell))
    print('  Snap-Clips: 4 Ecken, Spiess-Stil')
    print('  Parameter: Modify → Change Parameters')
