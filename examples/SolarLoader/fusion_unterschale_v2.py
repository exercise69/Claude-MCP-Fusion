"""
fusion_unterschale_v2.py — Unterschale mit vertiefter Display-Mulde (Adafruit-Stil).

Neu gegenüber v1:
  - Vorderfläche (oz0-Seite) im Display-/Tasterbereich auf 1mm ausgedünnt
    (Mulde: X=4..45mm, Y=1..22mm, Tiefe=1.5mm → 1mm Restwand)
  - Nur der TFT-Bereich (25.5×15.4mm) wird komplett durchbrochen
  - Taster-Stiftlöcher gehen durch die dünne 1mm Wand der Mulde
  - USB-C-Schlitz korrigiert: Z=0..4.5mm (statt -0.5..5.8mm)

Alle anderen Merkmale identisch mit v1:
  Standoffs, Board-Schrauben, USB-C, SD-Schlitz, Steckzunge, 2 Schnapp-Clips.
"""
import sys
sys.path.append('/Users/upi/Documents/Eigene Programme/Programs/Fusion360Scripts')
import f360_helpers as f

import adsk.core, adsk.fusion

def run(_context):
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # Bestehende Unterschale (v1) verstecken — nicht löschen
    occ_v1 = f.find_occurrence(root, "Unterschale")
    if occ_v1:
        occ_v1.isLightBulbOn = False
        print("  Unterschale v1 versteckt")

    # Alte v2 entfernen falls vorhanden (Idempotenz)
    f.delete_component(root, "Unterschale_v2")

    # ── Parameter (identisch mit v1) ────────────────────────────────────
    wall      = f.cm(2.5)
    fillet_r  = f.cm(2.0)
    split_z   = f.cm(22.0)
    clearance = f.cm(0.6)

    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)
    iz0 = f.cm(-1.94) - f.cm(0.6)        # = -2.54mm
    top_z = f.cm(34.0)

    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance
    iz1 = top_z + f.cm(1.0)

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0 = iz0 - wall        # = -5.04mm  (Außenseite / Vorderseite / Displayseite)

    pcb_cy = (asm_y0 + asm_y1) / 2  # ≈ 11.43mm

    # TFT aktive Fläche
    disp_w, disp_h = f.cm(25.5), f.cm(15.4)
    disp_cx, disp_cy = f.cm(26.26), f.cm(11.35)

    # USB-C-Schlitz (linke Wand) — korrigiert Z=0..4.5mm
    usbc_y0, usbc_y1 = pcb_cy - f.cm(5.0), pcb_cy + f.cm(5.0)
    usbc_z0, usbc_z1 = f.cm(0.0), f.cm(4.5)

    # Taster-Stiftlöcher Ø2.5mm
    btn_hole_d = f.cm(2.5)
    btn_hole_x = f.cm(7.6)
    btn_ys     = [f.cm(4.4), f.cm(11.4), f.cm(18.4)]
    rst_hole_x = f.cm(44.5)
    rst_hole_y = f.cm(11.5)

    # SD-Karten-Schlitz (rechte Wand)
    sd_y0, sd_y1 = f.cm(3.0),  f.cm(17.5)
    sd_z0, sd_z1 = f.cm(9.3),  f.cm(14.0)

    # Standoffs Ø5mm, h=2.5mm
    so_pos = [(f.cm(2.54), f.cm(2.54)),  (f.cm(2.54), f.cm(20.32)),
              (f.cm(48.26), f.cm(1.84)), (f.cm(48.26), f.cm(20.96))]
    so_od, so_h = f.cm(5.0), f.cm(2.5)

    # Board-Schrauben M2 Senkkopf
    screw_d = f.cm(2.2)
    csk_d   = f.cm(4.0)
    csk_dep = f.cm(1.5)

    # Steckzunge
    # lip_wall=1.6mm = 4 Perimeter bei 0.4mm Nozzle (war 1.5mm = 3.75 → unrund)
    lip_h, lip_wall, lip_gap = f.cm(4.0), f.cm(1.6), f.cm(0.25)

    # ── Display-Mulde ───────────────────────────────────────────────────
    # Maße: deckt Display-Modul-BB (X≈12..40mm, Y≈2.5..20mm),
    #        D0/D1/D2-Taster (X=7.6mm) und Reset (X=44.5mm) ab.
    # wall=2.5mm → recess_depth=1.3mm → Restwand=1.2mm = 3 Perimeter bei 0.4mm Nozzle
    # (war 1.5mm Tiefe → 1.0mm Restwand = 2.5 Perimeter, nicht sauber teilbar)
    recess_depth = f.cm(1.3)
    recess_x0    = f.cm(4.0)
    recess_x1    = f.cm(45.0)
    recess_y0    = f.cm(1.0)
    recess_y1    = f.cm(22.0)

    # ── UNTERSCHALE v2 ERSTELLEN ─────────────────────────────────────────
    print("Erstelle Unterschale_v2 ...")
    us_occ = f.new_component(root, "Unterschale_v2")
    us = us_occ.component

    # 1. Außenhülle
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z)
    shell.name = "Unterschale_v2"

    # 2. Vertikale Kanten verrunden (R=2mm)
    f.fillet_z_edges(us, shell, fillet_r)
    print("  Außenhülle + Verrundung fertig")

    # 3. Innenraum aushöhlen
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z + f.cm(0.1)))
    print("  Innenraum ausgehöhlt")

    # 4. Standoffs joinen
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print("  Standoffs hinzugefügt")

    # 5. Steckzunge als Rahmen + 2 Schnapp-Clips (vorne + hinten)
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap
    lip = f.box(us, lx0, ly0, split_z, lx1, ly1, split_z + lip_h)
    f.cut(us, lip, f.box(us, lx0 + lip_wall, ly0 + lip_wall,
                          split_z - f.cm(0.1),
                          lx1 - lip_wall, ly1 - lip_wall,
                          split_z + lip_h + f.cm(0.1)))

    clip_w    = f.cm(6.0)
    clip_h    = f.cm(2.0)
    clip_ramp = f.cm(1.0)
    clip_p    = f.cm(0.5)
    clip_ov   = f.cm(0.15)
    clip_z1   = split_z + lip_h          # 26mm
    clip_z0   = clip_z1 - clip_h         # 24mm
    clip_zr   = clip_z0 - clip_ramp      # 23mm
    cx_lip    = (lx0 + lx1) / 2

    def add_clip(x0, y0, z0_ramp, x1, y1, z1_lock, ramp_axis, ramp_sign):
        tab = f.box(us, x0, y0, z0_ramp, x1, y1, z1_lock)
        if ramp_axis == 'y' and ramp_sign < 0:
            f.cut(us, tab, f.box(us, x0 - f.cm(0.1), y0, z0_ramp - f.cm(0.1),
                                      x1 + f.cm(0.1), y0 + clip_p * 0.6, clip_z0 + f.cm(0.1)))
        elif ramp_axis == 'y' and ramp_sign > 0:
            f.cut(us, tab, f.box(us, x0 - f.cm(0.1), y1 - clip_p * 0.6, z0_ramp - f.cm(0.1),
                                      x1 + f.cm(0.1), y1 + f.cm(0.1), clip_z0 + f.cm(0.1)))
        f.join(us, lip, tab)

    # Vordere Wand (Überstand in -Y)
    add_clip(cx_lip - clip_w/2, ly0 - clip_p,  clip_zr,
             cx_lip + clip_w/2, ly0 + clip_ov, clip_z1, 'y', -1)
    # Hintere Wand (Überstand in +Y)
    add_clip(cx_lip - clip_w/2, ly1 - clip_ov, clip_zr,
             cx_lip + clip_w/2, ly1 + clip_p,  clip_z1, 'y', +1)

    f.join(us, shell, lip)
    print("  Steckzunge + 2 Schnapp-Clips fertig")

    # 6. Display-Mulde: 1.5mm tief von INNEN (iz0-Seite) einsenken
    #    → Außenfläche bleibt glatt; Tasche nur von innen sichtbar (Adafruit-Stil)
    #    Restwand außen: wall - recess_depth = 2.5 - 1.5 = 1mm
    f.cut(us, shell, f.box(us,
        recess_x0, recess_y0, iz0 - recess_depth - f.cm(0.1),
        recess_x1, recess_y1, iz0 + f.cm(0.1)))
    print("  Display-Mulde eingesenkt  (von innen, 1mm Restwand außen)")

    # 7. TFT-Fenster: komplett durchbrochen (durch volle 2.5mm Wand)
    f.cut(us, shell, f.box(us,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - f.cm(0.1),
        disp_cx + disp_w/2, disp_cy + disp_h/2, oz0 + wall + f.cm(0.1)))
    print("  TFT-Fenster ausgeschnitten  (25.5 × 15.4mm)")

    # 8. USB-C-Schlitz (linke Wand, Z=0..4.5mm)
    f.cut(us, shell, f.box(us,
        ox0 - f.cm(0.1), usbc_y0, usbc_z0,
        ix0 + f.cm(4.0), usbc_y1,  usbc_z1))
    print("  USB-C-Schlitz fertig")

    # 9. Taster-Stiftlöcher Ø2.5mm durch Vorderwand
    #    (in der Mulde: durch 1mm Restwand; außerhalb: durch volle 2.5mm)
    for by in btn_ys:
        f.cut(us, shell, f.cylinder(us,
            btn_hole_x, by, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_hole_d))
    f.cut(us, shell, f.cylinder(us,
        rst_hole_x, rst_hole_y, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_hole_d))
    print("  Stiftlöcher fertig  (D0/D1/D2 + Reset)")

    # 10. SD-Karten-Schlitz (rechte Wand)
    f.cut(us, shell, f.box(us,
        ix1 - f.cm(0.1), sd_y0, sd_z0,
        ix1 + wall + f.cm(0.1), sd_y1, sd_z1))
    print("  SD-Schlitz fertig")

    # 11. Board-Schrauben M2: Senkung + Durchgangsloch
    #     Alle 4 Positionen liegen AUSSERHALB der Mulde → volle Wandstärke vorhanden
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), oz0 + csk_dep + f.cm(0.1), csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), iz0 + so_h + f.cm(0.1), screw_d))
    print("  Board-Schrauben fertig")

    print(f"✓ Unterschale_v2 fertig!  {f.bbox_str(shell)}")
