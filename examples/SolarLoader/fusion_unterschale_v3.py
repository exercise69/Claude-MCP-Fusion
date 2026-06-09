"""
fusion_unterschale_v3.py — Unterschale mit vollständiger Fusion-Parametrisierung.

Alle Design-Parameter sind als Fusion User Parameters registriert
und in Modify → Change Parameters sichtbar und änderbar.
Hardware-Konstanten (PCB-BB, Display-Position, Taster-XY) bleiben
Python-Variablen, da sie durch die Hardware vorgegeben sind.

Änderungen gegenüber v2:
  - Alle Parameter als Fusion User Parameters
  - lipo_h vorbereitet (0mm = kein LiPo, >0 = Höhenzuschlag)
  - Strukturiert nach Gruppen
"""
import sys
sys.path.append('/path/to/Fusion360Scripts')
import f360_helpers as f
import adsk.core, adsk.fusion

def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. FUSION USER PARAMETERS REGISTRIEREN ──────────────────────
    # Sichtbar in: Modify → Change Parameters
    # Werte in mm — f.set_param konvertiert intern nach cm.

    # --- Gehäuse ---
    f.set_param(des, 'wall',      2.5,   'Wandstaerke mm')
    f.set_param(des, 'clearance', 0.6,   'Luft um PCB-Stack mm')
    f.set_param(des, 'fillet_r',  2.0,   'Verrundungsradius Kanten mm')
    f.set_param(des, 'split_z',   22.0,  'Trennlinie Unter-/Oberschale mm')
    f.set_param(des, 'lipo_h',    0.0,   'LiPo-Hoehenaufschlag mm (0 = kein LiPo)')

    # --- Steckzunge ---
    f.set_param(des, 'lip_h',    4.0,   'Hoehe Steckzunge mm')
    f.set_param(des, 'lip_wall', 1.6,   'Wandstaerke Steckzunge mm (4 Perimeter bei 0.4mm Nozzle)')
    f.set_param(des, 'lip_gap',  0.25,  'Toleranzspiel Steckzunge mm')

    # --- Schnapp-Clips ---
    f.set_param(des, 'clip_w',    6.0,  'Clip-Breite mm')
    f.set_param(des, 'clip_h',    2.0,  'Clip-Rasthöhe mm')
    f.set_param(des, 'clip_ramp', 1.0,  'Clip-Einführschraege Höhe mm')
    f.set_param(des, 'clip_p',    0.5,  'Clip-Überstand über Steckzunge mm')

    # --- Display-Mulde ---
    f.set_param(des, 'recess_d',  1.3,  'Tiefe Display-Mulde von innen mm (Restwand = wall - recess_d)')

    # --- USB-C Schlitz (linke Wand) ---
    f.set_param(des, 'usbc_half', 5.0,  'USB-C Schlitz Halbbreite mm (±Y von PCB-Mitte)')
    f.set_param(des, 'usbc_z1',   4.5,  'USB-C Schlitz Z-Oberkante mm')

    # --- Taster ---
    f.set_param(des, 'btn_d',    2.5,   'Taster-Stiftloch Durchmesser mm')

    # --- SD-Karten-Schlitz (rechte Wand) ---
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

    # ── 2. PARAMETER EINLESEN (alle in cm für Fusion-API) ───────────
    wall      = f.get_param_cm(des, 'wall')
    clearance = f.get_param_cm(des, 'clearance')
    fillet_r  = f.get_param_cm(des, 'fillet_r')
    split_z   = f.get_param_cm(des, 'split_z')
    lipo_h    = f.get_param_cm(des, 'lipo_h')

    lip_h    = f.get_param_cm(des, 'lip_h')
    lip_wall = f.get_param_cm(des, 'lip_wall')
    lip_gap  = f.get_param_cm(des, 'lip_gap')

    clip_w    = f.get_param_cm(des, 'clip_w')
    clip_h    = f.get_param_cm(des, 'clip_h')
    clip_ramp = f.get_param_cm(des, 'clip_ramp')
    clip_p    = f.get_param_cm(des, 'clip_p')

    recess_d  = f.get_param_cm(des, 'recess_d')

    usbc_half = f.get_param_cm(des, 'usbc_half')
    usbc_z1   = f.get_param_cm(des, 'usbc_z1')

    btn_d = f.get_param_cm(des, 'btn_d')

    sd_y0 = f.get_param_cm(des, 'sd_y0')
    sd_y1 = f.get_param_cm(des, 'sd_y1')
    sd_z0 = f.get_param_cm(des, 'sd_z0')
    sd_z1 = f.get_param_cm(des, 'sd_z1')

    so_od   = f.get_param_cm(des, 'so_od')
    so_h    = f.get_param_cm(des, 'so_h')
    screw_d = f.get_param_cm(des, 'screw_d')
    csk_d   = f.get_param_cm(des, 'csk_d')
    csk_dep = f.get_param_cm(des, 'csk_dep')

    # ── 3. HARDWARE-KONSTANTEN ───────────────────────────────────────
    # Durch die Hardware bestimmt — ändern sich nur bei anderem PCB-Stack.

    # PCB-Stack Bounding Box (Adafruit Feather-Stack)
    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)
    pcb_z0  = f.cm(-1.94)   # Unterseite Stack (Display-Seite)

    # PCB-Mitte Y (für USB-C Schlitz-Zentrierung)
    pcb_cy = (asm_y0 + asm_y1) / 2

    # Display TFT (aktive Fläche + Modul-Mitte)
    disp_w  = f.cm(25.5);  disp_h  = f.cm(15.4)
    disp_cx = f.cm(26.26); disp_cy = f.cm(11.35)

    # Display-Mulde Footprint (deckt Modul-BB + D0/D1/D2 + Reset ab)
    recess_x0 = f.cm(4.0);  recess_x1 = f.cm(45.0)
    recess_y0 = f.cm(1.0);  recess_y1 = f.cm(22.0)

    # Taster D0/D1/D2 + Reset
    btn_x  = f.cm(7.6)
    btn_ys = [f.cm(4.4), f.cm(11.4), f.cm(18.4)]
    rst_x  = f.cm(44.5);  rst_y = f.cm(11.5)

    # Standoff-Positionen (M2-Montagelöcher im PCB)
    so_pos = [(f.cm(2.54), f.cm(2.54)),  (f.cm(2.54), f.cm(20.32)),
              (f.cm(48.26), f.cm(1.84)), (f.cm(48.26), f.cm(20.96))]

    # ── 4. ABGELEITETE GEOMETRIE ─────────────────────────────────────
    iz0 = pcb_z0 - f.cm(0.6)       # Innenraum-Unterkante (+0.6mm Puffer unter Display)

    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0 = iz0 - wall                # Außenfläche Vorderseite/Display (-5.04mm)

    usbc_y0 = pcb_cy - usbc_half
    usbc_y1 = pcb_cy + usbc_half

    # ── 5. MODELL ERSTELLEN ──────────────────────────────────────────
    # v2 verstecken (nicht löschen)
    occ_v2 = f.find_occurrence(root, 'Unterschale_v2')
    if occ_v2:
        occ_v2.isLightBulbOn = False
        print('Unterschale_v2 versteckt')
    occ_v1 = f.find_occurrence(root, 'Unterschale')
    if occ_v1:
        occ_v1.isLightBulbOn = False

    # Alte v3 entfernen (Idempotenz)
    f.delete_component(root, 'Unterschale_v3')

    print('Erstelle Unterschale_v3 ...')
    us_occ = f.new_component(root, 'Unterschale_v3')
    us = us_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z)
    shell.name = 'Unterschale_v3'
    f.fillet_z_edges(us, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z + f.cm(0.1)))
    print('  Innenraum ausgehöhlt')

    # 3. Standoffs
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print('  Standoffs')

    # 4. Steckzunge + 2 Schnapp-Clips (vorne + hinten)
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap
    lip = f.box(us, lx0, ly0, split_z, lx1, ly1, split_z + lip_h)
    f.cut(us, lip, f.box(us, lx0 + lip_wall, ly0 + lip_wall,
                              split_z - f.cm(0.1),
                              lx1 - lip_wall, ly1 - lip_wall,
                              split_z + lip_h + f.cm(0.1)))

    clip_z1 = split_z + lip_h
    clip_z0 = clip_z1 - clip_h
    clip_zr = clip_z0 - clip_ramp
    cx_lip  = (lx0 + lx1) / 2
    clip_ov = f.cm(0.15)   # Überlappung für Join

    def add_clip(x0, y0, z0r, x1, y1, z1l, ramp_sign):
        tab = f.box(us, x0, y0, z0r, x1, y1, z1l)
        if ramp_sign < 0:
            f.cut(us, tab, f.box(us, x0-f.cm(0.1), y0, z0r-f.cm(0.1),
                                      x1+f.cm(0.1), y0+clip_p*0.6, clip_z0+f.cm(0.1)))
        else:
            f.cut(us, tab, f.box(us, x0-f.cm(0.1), y1-clip_p*0.6, z0r-f.cm(0.1),
                                      x1+f.cm(0.1), y1+f.cm(0.1), clip_z0+f.cm(0.1)))
        f.join(us, lip, tab)

    add_clip(cx_lip-clip_w/2, ly0-clip_p,  clip_zr,
             cx_lip+clip_w/2, ly0+clip_ov, clip_z1, -1)
    add_clip(cx_lip-clip_w/2, ly1-clip_ov, clip_zr,
             cx_lip+clip_w/2, ly1+clip_p,  clip_z1, +1)
    f.join(us, shell, lip)
    print('  Steckzunge + 2 Schnapp-Clips')

    # 5. Display-Mulde von INNEN (Außenfläche bleibt glatt)
    f.cut(us, shell, f.box(us,
        recess_x0, recess_y0, iz0 - recess_d - f.cm(0.1),
        recess_x1, recess_y1, iz0 + f.cm(0.1)))
    print('  Display-Mulde (von innen, Restwand=' + str(round((wall - recess_d)*10, 1)) + 'mm)')

    # 6. TFT-Fenster (komplett durchbrochen)
    f.cut(us, shell, f.box(us,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - f.cm(0.1),
        disp_cx + disp_w/2, disp_cy + disp_h/2, oz0 + wall + f.cm(0.1)))
    print('  TFT-Fenster')

    # 7. USB-C-Schlitz (linke Wand, Z=0..usbc_z1)
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

    # 9. SD-Karten-Schlitz (rechte Wand)
    f.cut(us, shell, f.box(us,
        ix1 - f.cm(0.1), sd_y0, sd_z0,
        ix1 + wall + f.cm(0.1), sd_y1, sd_z1))
    print('  SD-Karten-Schlitz')

    # 10. Board-Schrauben M2: Senkung + Durchgangsloch
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), oz0 + csk_dep + f.cm(0.1), csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), iz0 + so_h + f.cm(0.1), screw_d))
    print('  Board-Schrauben (M2)')

    print('✓ Unterschale_v3 fertig!  ' + f.bbox_str(shell))
    print('  Parameter sichtbar unter: Modify → Change Parameters')
