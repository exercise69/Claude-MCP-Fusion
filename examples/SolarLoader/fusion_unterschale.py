"""
fusion_unterschale.py — Erstellt die Unterschale des SolarLoader-Gehäuses in Fusion 360.
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

    # ── Parameter (identisch mit OpenSCAD) ──────────────────────────────
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
    oz0 = iz0 - wall        # = -5.04mm  (Außenseite Display/Vorderseite)

    pcb_cy = (asm_y0 + asm_y1) / 2  # ≈ 1.143cm

    # Display-Fenster
    disp_w, disp_h = f.cm(25.5), f.cm(15.4)
    disp_cx, disp_cy = f.cm(26.26), f.cm(11.35)

    # USB-C-Schlitz — zentriert auf Connector Z=0.57..4.77mm (Welt-Koordinaten)
    usbc_y0, usbc_y1 = pcb_cy - f.cm(5.0), pcb_cy + f.cm(5.0)
    usbc_z0, usbc_z1 = f.cm(-0.5), f.cm(5.8)

    # Taster-Stiftlöcher
    btn_hole_d  = f.cm(2.5)
    btn_hole_x  = f.cm(7.6)
    btn_ys      = [f.cm(4.4), f.cm(11.4), f.cm(18.4)]
    rst_hole_x  = f.cm(44.5)   # Reset: rechts vom Display
    rst_hole_y  = f.cm(11.5)

    # SD-Karten-Schlitz
    sd_y0, sd_y1 = f.cm(3.0),  f.cm(17.5)
    sd_z0, sd_z1 = f.cm(9.3),  f.cm(14.0)

    # Standoffs
    so_pos = [(f.cm(2.54), f.cm(2.54)),  (f.cm(2.54), f.cm(20.32)),
              (f.cm(48.26), f.cm(1.84)), (f.cm(48.26), f.cm(20.96))]
    so_od, so_h = f.cm(5.0), f.cm(2.5)

    # Board-Schrauben (M2 Senkkopf)
    screw_d = f.cm(2.2)
    csk_d   = f.cm(4.0)
    csk_dep = f.cm(1.5)

    # Steckzunge
    lip_h, lip_wall, lip_gap = f.cm(4.0), f.cm(1.5), f.cm(0.25)

    # ── UNTERSCHALE ERSTELLEN ────────────────────────────────────────────
    print("Erstelle Unterschale ...")
    us_occ = f.new_component(root, "Unterschale")
    us = us_occ.component

    # 1. Außenhülle
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z)
    shell.name = "Unterschale"
    print("  Außenhülle erstellt")

    # 2. Vertikale Kanten verrunden (R=2mm)
    f.fillet_z_edges(us, shell, fillet_r)
    print("  Verrundung fertig")

    # 3. Innenraum aushöhlen
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z + f.cm(0.1)))
    print("  Innenraum ausgehöhlt")

    # 4. Standoffs (Ø5mm, h=2.5mm) joinen
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print("  Standoffs hinzugefügt")

    # 5. Steckzunge als Rahmen joinen
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap
    lip = f.box(us, lx0, ly0, split_z, lx1, ly1, split_z + lip_h)
    f.cut(us, lip, f.box(us, lx0 + lip_wall, ly0 + lip_wall,
                          split_z - f.cm(0.1),
                          lx1 - lip_wall, ly1 - lip_wall,
                          split_z + lip_h + f.cm(0.1)))
    # Schnapp-Clips: 4 Cantilever-Tabs auf der Steckzunge (je eine pro Wand)
    # Tab-Geometrie: 6mm breit, 2mm Rasthöhe + 1mm Rampe, 0.5mm Überstand
    clip_w   = f.cm(6.0)   # Breite entlang der Wand
    clip_h   = f.cm(2.0)   # Höhe des Rastbereichs
    clip_ramp= f.cm(1.0)   # Höhe der Einführschräge (unterhalb Rastbereich)
    clip_p   = f.cm(0.5)   # Überstand über Steckzungenaußenfläche
    clip_ov  = f.cm(0.15)  # Überlappung in Steckzunge für Join
    clip_z1  = split_z + lip_h                    # = 26mm (Oberkante Tab = Oberkante Zunge)
    clip_z0  = clip_z1 - clip_h                   # = 24mm (Unterkante Rastbereich)
    clip_zr  = clip_z0 - clip_ramp                # = 23mm (Unterkante Rampe)

    cx_lip = (lx0 + lx1) / 2   # X-Mitte Steckzunge
    cy_lip = (ly0 + ly1) / 2   # Y-Mitte Steckzunge

    # Hilfsfunktion: Tab + Rampe erstellen und an lip joinen
    def add_clip(x0, y0, z0_ramp, x1, y1, z1_lock, ramp_axis, ramp_sign):
        """Erstellt einen Clip-Tab mit Einführrampe und joiniert ihn an lip."""
        # Vollquader (Rampe + Rastbereich zusammen)
        tab = f.box(us, x0, y0, z0_ramp, x1, y1, z1_lock)
        # Rampe durch Keil-Cut: untere Hälfte der Protrusion wegschneiden
        ramp_h = clip_ramp
        if ramp_axis == 'x' and ramp_sign < 0:   # linke Wand, Überstand in -X
            f.cut(us, tab, f.box(us, x0, y0 - f.cm(0.1), z0_ramp - f.cm(0.1),
                                      x0 + clip_p * 0.6, y1 + f.cm(0.1), clip_z0 + f.cm(0.1)))
        elif ramp_axis == 'x' and ramp_sign > 0:  # rechte Wand, Überstand in +X
            f.cut(us, tab, f.box(us, x1 - clip_p * 0.6, y0 - f.cm(0.1), z0_ramp - f.cm(0.1),
                                      x1 + f.cm(0.1), y1 + f.cm(0.1), clip_z0 + f.cm(0.1)))
        elif ramp_axis == 'y' and ramp_sign < 0:  # vordere Wand, Überstand in -Y
            f.cut(us, tab, f.box(us, x0 - f.cm(0.1), y0, z0_ramp - f.cm(0.1),
                                      x1 + f.cm(0.1), y0 + clip_p * 0.6, clip_z0 + f.cm(0.1)))
        elif ramp_axis == 'y' and ramp_sign > 0:  # hintere Wand, Überstand in +Y
            f.cut(us, tab, f.box(us, x0 - f.cm(0.1), y1 - clip_p * 0.6, z0_ramp - f.cm(0.1),
                                      x1 + f.cm(0.1), y1 + f.cm(0.1), clip_z0 + f.cm(0.1)))
        f.join(us, lip, tab)

    # Linke Wand (Überstand in -X)
    add_clip(lx0 - clip_p,  cy_lip - clip_w/2, clip_zr,
             lx0 + clip_ov, cy_lip + clip_w/2, clip_z1, 'x', -1)
    # Rechte Wand (Überstand in +X)
    add_clip(lx1 - clip_ov, cy_lip - clip_w/2, clip_zr,
             lx1 + clip_p,  cy_lip + clip_w/2, clip_z1, 'x', +1)
    # Vordere Wand (Überstand in -Y)
    add_clip(cx_lip - clip_w/2, ly0 - clip_p,  clip_zr,
             cx_lip + clip_w/2, ly0 + clip_ov, clip_z1, 'y', -1)
    # Hintere Wand (Überstand in +Y)
    add_clip(cx_lip - clip_w/2, ly1 - clip_ov, clip_zr,
             cx_lip + clip_w/2, ly1 + clip_p,  clip_z1, 'y', +1)

    f.join(us, shell, lip)
    print("  Steckzunge + 4 Schnapp-Clips hinzugefügt")

    # 6. Display-Fenster
    f.cut(us, shell, f.box(us,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - f.cm(0.1),
        disp_cx + disp_w/2, disp_cy + disp_h/2, oz0 + wall + f.cm(0.1)))
    print("  Display-Fenster ausgeschnitten")

    # 7. USB-C-Schlitz (linke Wand)
    f.cut(us, shell, f.box(us,
        ox0 - f.cm(0.1), usbc_y0, usbc_z0,
        ix0 + f.cm(4.0), usbc_y1,  usbc_z1))
    print("  USB-C-Schlitz fertig")

    # 8. Taster-Stiftlöcher D0/D1/D2 + Reset (durch Displayboden)
    for by in btn_ys:
        f.cut(us, shell, f.cylinder(us,
            btn_hole_x, by, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_hole_d))
    f.cut(us, shell, f.cylinder(us,
        rst_hole_x, rst_hole_y, oz0 - f.cm(0.1), oz0 + wall + f.cm(0.1), btn_hole_d))
    print("  Stiftlöcher fertig")

    # 9. SD-Karten-Schlitz (rechte Wand)
    f.cut(us, shell, f.box(us,
        ix1 - f.cm(0.1), sd_y0, sd_z0,
        ix1 + wall + f.cm(0.1), sd_y1, sd_z1))
    print("  SD-Schlitz fertig")

    # 10. Board-Schrauben (M2): Senkung + Durchgangsloch
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), oz0 + csk_dep + f.cm(0.1), csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - f.cm(0.1), iz0 + so_h + f.cm(0.1), screw_d))
    print("  Board-Schrauben fertig")

    print(f"✓ Unterschale fertig!  {f.bbox_str(shell)}")
