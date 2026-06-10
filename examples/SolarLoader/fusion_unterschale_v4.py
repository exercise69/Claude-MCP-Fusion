"""
fusion_unterschale_v4.py — Unterschale mit Spiess-Stil Lip (dreieckiger Querschnitt).

Passend zu fusion_oberschale_v4.py.

Gemeinsame Hardware-Konstanten und geteilte Parameter kommen aus
solarloader_common (define_common_params) — kein Doppelt-Definieren mehr.

Parameter-Philosophie: create-if-missing (overwrite=False). Werte, die du in
Fusion unter Modify → Change Parameters änderst, überleben einen Rebuild.
Zum Zurücksetzen auf die Code-Defaults: define_common_params(des, overwrite=True)
bzw. die set_param(..., overwrite=True)-Aufrufe.

Änderungen gegenüber v3_1:
  - Eck-Protrusions (Würfel) ersetzt durch durchgehende Lip-Leiste
  - Lip läuft auf beiden langen Y-Seiten fast über volle X-Länge
  - Dreieckiger Querschnitt via f.triangle_prism_x() (Spiess-Stil)
  - Lip_front/Lip_back als separate Bodies (male part, rastet in Notch der Oberschale)
  - RS485-Aussparung in der rechten Steckzungen-Wand

Konstruktions-Strategie:
  Shell und Lip werden als EIN KÖRPER gebaut (kein separate Join-Operation nötig):
  1. Hoher Quader von oz0 bis split_z + lip_h
  2. Innenraum aushöhlen (bis split_z+0.1)
  3. Oberhalb split_z: Material außerhalb des Lip-Footprints entfernen (4 Schnitte)
  4. Lip innen aushöhlen + RS485-Aussparung
  5. Spiess-Lips als separate Bodies erzeugen (kein Join)
"""
import sys

_PATHS = ('/path/to/Fusion360Scripts',
          '/path/to/Fusion360Scripts/examples/SolarLoader')
for _p in _PATHS:
    if _p not in sys.path:
        sys.path.append(_p)
for _m in ('f360_helpers', 'solarloader_common'):
    if _m in sys.modules:
        del sys.modules[_m]
import f360_helpers as f
import solarloader_common as sl
import adsk.core, adsk.fusion


def run(_context):
    try:
        _build()
    except Exception:
        import traceback
        print('!!! FEHLER in fusion_unterschale_v4:\n' + traceback.format_exc())
        raise


def _build():
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. USER-PARAMETER ────────────────────────────────────────────────
    sl.define_common_params(des)          # geteilte Params (create-if-missing)

    ow = False                            # overwrite=False für alle Specifics
    f.set_param(des, 'lipo_h',      0.0,  'LiPo-Hoehenaufschlag mm',          ow)
    f.set_param(des, 'lip_wall',    1.6,  'Wandstaerke Steckzunge mm',        ow)
    f.set_param(des, 'recess_d',    1.3,  'Tiefe Display-Mulde von innen mm', ow)
    f.set_param(des, 'usbc_half',   5.0,  'USB-C Schlitz Halbbreite mm',      ow)
    f.set_param(des, 'usbc_z0',     1.2,  'USB-C Schlitz Z-Unterkante mm',    ow)
    f.set_param(des, 'usbc_z1',     5.2,  'USB-C Schlitz Z-Oberkante mm',     ow)
    f.set_param(des, 'btn_d',       2.5,  'Taster-Stiftloch Durchmesser mm',  ow)
    f.set_param(des, 'sd_y0',       3.0,  'SD-Schlitz Y-Unterkante mm',       ow)
    f.set_param(des, 'sd_y1',      17.5,  'SD-Schlitz Y-Oberkante mm',        ow)
    f.set_param(des, 'sd_z0',       9.3,  'SD-Schlitz Z-Unterkante mm',       ow)
    f.set_param(des, 'sd_z1',      14.0,  'SD-Schlitz Z-Oberkante mm',        ow)
    f.set_param(des, 'so_od',       5.0,  'Standoff Aussendurchmesser mm',    ow)
    f.set_param(des, 'so_h',        2.5,  'Standoff Hoehe mm',                ow)
    f.set_param(des, 'screw_d',     2.2,  'M2-Durchgangsloch mm',             ow)
    f.set_param(des, 'csk_d',       4.0,  'M2-Senkkopf Durchmesser mm',       ow)
    f.set_param(des, 'csk_dep',     1.5,  'M2-Senkkopf Tiefe mm',             ow)
    # Flex-Taster (Living-Hinge) D0/D1/D2
    f.set_param(des, 'fb_pad',      5.0,  'Flex-Taster Pad-Kantenlaenge mm',  ow)
    f.set_param(des, 'fb_slot',     0.6,  'Flex-Taster Schlitzbreite mm',     ow)
    f.set_param(des, 'fb_hinge',    0.6,  'Flex-Taster Scharnier-Restwand mm', ow)
    f.set_param(des, 'fb_hinge_w',  1.5,  'Flex-Taster Scharnier-Nutbreite mm', ow)
    f.set_param(des, 'fb_nub_d',    2.0,  'Flex-Taster Drucknocken Durchm. mm', ow)
    f.set_param(des, 'fb_nub_gap',  0.15, 'Flex-Taster Ruheluft zum Taster mm', ow)

    # ── 2. PARAMETER EINLESEN ────────────────────────────────────────────
    wall        = f.get_param_cm(des, 'wall')
    clearance   = f.get_param_cm(des, 'clearance')
    fillet_r    = f.get_param_cm(des, 'fillet_r')
    split_z     = f.get_param_cm(des, 'split_z')
    lipo_h      = f.get_param_cm(des, 'lipo_h')

    lip_h       = f.get_param_cm(des, 'lip_h')
    lip_wall    = f.get_param_cm(des, 'lip_wall')
    lip_gap     = f.get_param_cm(des, 'lip_gap')

    snap_d      = f.get_param_cm(des, 'snap_d')
    snap_h      = f.get_param_cm(des, 'snap_h')
    snap_margin = f.get_param_cm(des, 'snap_margin')
    snap_top    = f.get_param_cm(des, 'snap_top')

    recess_d    = f.get_param_cm(des, 'recess_d')
    usbc_half   = f.get_param_cm(des, 'usbc_half')
    usbc_z0     = f.get_param_cm(des, 'usbc_z0')
    usbc_z1     = f.get_param_cm(des, 'usbc_z1')
    btn_d       = f.get_param_cm(des, 'btn_d')
    sd_y0       = f.get_param_cm(des, 'sd_y0')
    sd_y1       = f.get_param_cm(des, 'sd_y1')
    sd_z0       = f.get_param_cm(des, 'sd_z0')
    sd_z1       = f.get_param_cm(des, 'sd_z1')
    so_od       = f.get_param_cm(des, 'so_od')
    so_h        = f.get_param_cm(des, 'so_h')
    screw_d     = f.get_param_cm(des, 'screw_d')
    csk_d       = f.get_param_cm(des, 'csk_d')
    csk_dep     = f.get_param_cm(des, 'csk_dep')
    fb_pad      = f.get_param_cm(des, 'fb_pad')
    fb_slot     = f.get_param_cm(des, 'fb_slot')
    fb_hinge    = f.get_param_cm(des, 'fb_hinge')
    fb_hinge_w  = f.get_param_cm(des, 'fb_hinge_w')
    fb_nub_d    = f.get_param_cm(des, 'fb_nub_d')
    fb_nub_gap  = f.get_param_cm(des, 'fb_nub_gap')
    rs485_y0    = f.get_param_cm(des, 'rs485_y0')
    rs485_y1    = f.get_param_cm(des, 'rs485_y1')

    # ── 3. HARDWARE-KONSTANTEN (aus solarloader_common) ──────────────────
    asm_x0, asm_x1 = sl.ASM_X0, sl.ASM_X1
    asm_y0, asm_y1 = sl.ASM_Y0, sl.ASM_Y1
    pcb_z0  = sl.PCB_Z0
    pcb_cy  = sl.pcb_cy()

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

    # Lip-Maße (passend in Oberschale-Innenraum, lip_gap Luft)
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap

    # Lip-Geometrie
    snap_z1 = split_z + lip_h - snap_top   # Lip-Oberkante (Rampe oben endet hier)
    snap_z0 = snap_z1 - snap_h             # Lip-Unterkante (flache Rastfläche)
    lip_x0  = lx0 + snap_margin            # X-Beginn der Lip-Leiste
    lip_x1  = lx1 - snap_margin            # X-Ende der Lip-Leiste

    e = f.cm(0.1)   # kleines Übermaß für saubere Schnitte

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    for name in ('Unterschale', 'Unterschale_v2', 'Unterschale_v3',
                 'Unterschale_v3_1'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Unterschale_v4')

    print('Erstelle Unterschale_v4 ...')
    us_occ = f.new_component(root, 'Unterschale_v4')
    us = us_occ.component

    # 1. Hoher Quader: Shell + Lip als EIN Körper
    #    Höhe geht bis split_z + lip_h (statt nur split_z)
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z + lip_h)
    shell.name = 'Unterschale_v4'
    f.fillet_z_edges(us, shell, fillet_r)
    print('  Außenhülle + Verrundung (oz0 → split_z+lip_h)')

    # 2. Innenraum aushöhlen (Shell-Kavität bis split_z)
    #    split_z - e: lässt 0.1mm Verbindungsscheibe stehen → Lip-Säule bleibt mit Shell verbunden
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z - e))
    print('  Innenraum ausgehöhlt')

    # 3. Standoffs
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print('  Standoffs')

    # 4. Oberhalb split_z: Lip-Form herausschneiden
    #    Alles außerhalb des Lip-Footprints (lx0..lx1, ly0..ly1) entfernen
    #    → Shell + Lip bleiben als ein einziger zusammenhängender Körper

    # Links (X < lx0)
    f.cut(us, shell, f.box(us, ox0-e, oy0-e, split_z,
                                lx0, oy1+e, split_z+lip_h+e))
    # Rechts (X > lx1)
    f.cut(us, shell, f.box(us, lx1, oy0-e, split_z,
                                ox1+e, oy1+e, split_z+lip_h+e))
    # Vorne (Y < ly0, im X-Bereich des Lips)
    f.cut(us, shell, f.box(us, lx0, oy0-e, split_z,
                                lx1, ly0, split_z+lip_h+e))
    # Hinten (Y > ly1, im X-Bereich des Lips)
    f.cut(us, shell, f.box(us, lx0, ly1, split_z,
                                lx1, oy1+e, split_z+lip_h+e))
    print('  Lip-Außenform geschnitten (Shell+Lip = 1 Körper)')

    # 5. Lip innen aushöhlen
    f.cut(us, shell, f.box(us,
        lx0 + lip_wall, ly0 + lip_wall, split_z - e,
        lx1 - lip_wall, ly1 - lip_wall, split_z + lip_h + e))
    print('  Lip innen ausgehöhlt')

    # 5b. RS485-Aussparung: rechte Steckzungen-Wand über der Klemme unterbrechen
    #     Sonst säße der umlaufende Oberschalen-Rand in der RS485-Klemme.
    #     Y = rs485_y0..rs485_y1 (gleiche Breite wie das RS485-Kabelfenster)
    f.cut(us, shell, f.box(us,
        lx1 - lip_wall - e, rs485_y0, split_z - e,
        lx1 + e,           rs485_y1, split_z + lip_h + e))
    print('  RS485-Aussparung in Steckzunge (rechte Wand unterbrochen)')

    # 6. Spiess-Lip — dreieckige Leiste auf beiden langen Y-Seiten (male part)
    #    Separate Bodies → in Fusion ggf. nachpositionieren,
    #    dann mit Modify → Combine joinen.
    #
    #  Dreieck (vordere Seite, Überstand -Y von ly0):
    #    Ecke 1: (ly0,         snap_z1)  Wandfläche oben
    #    Ecke 2: (ly0,         snap_z0)  Wandfläche unten
    #    Ecke 3: (ly0-snap_d,  snap_z0)  Außenspitze unten → flache Rastfläche unten
    #    → Schräge OBEN (Lead-in beim Aufstecken), flache Rastfläche UNTEN (Verriegelung)

    # Vordere Seite (ly0, Überstand -Y)
    lip_front = f.triangle_prism_x(us,
        lip_x0, lip_x1,
        ly0,          snap_z1,
        ly0,          snap_z0,
        ly0 - snap_d, snap_z0)
    lip_front.name = 'Lip_front'

    # Hintere Seite (ly1, Überstand +Y)
    lip_back = f.triangle_prism_x(us,
        lip_x0, lip_x1,
        ly1,          snap_z1,
        ly1,          snap_z0,
        ly1 + snap_d, snap_z0)
    lip_back.name = 'Lip_back'

    print('  Spiess-Lip (2× Δ-Querschnitt, separat, '
          + str(round((lip_x1 - lip_x0) * 10, 1)) + ' mm lang)')

    # 7. Display-Mulde von innen
    f.cut(us, shell, f.box(us,
        recess_x0, recess_y0, iz0 - recess_d - e,
        recess_x1, recess_y1, iz0 + e))
    print('  Display-Mulde  (Restwand='
          + str(round((wall - recess_d) * 10, 1)) + ' mm)')

    # 8. TFT-Fenster
    f.cut(us, shell, f.box(us,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - e,
        disp_cx + disp_w/2, disp_cy + disp_h/2, oz0 + wall + e))
    print('  TFT-Fenster')

    # 9. USB-C-Schlitz  (Z auf echte Stecker-Öffnung 3.17mm zentriert, ~0.4mm Luft rundum)
    f.cut(us, shell, f.box(us,
        ox0 - e, usbc_y0, usbc_z0,
        ix0 + f.cm(4.0), usbc_y1, usbc_z1))
    print('  USB-C-Schlitz')

    # 10. Flex-Taster D0/D1/D2 (Living-Hinge) + Reset als Pinhole
    #     Pad in der Display-Mulden-Restwand, 3-seitig durch die Wand
    #     freigeschnitten; Scharnier-Steg bleibt auf der -X-Seite stehen und
    #     wird von innen auf fb_hinge ausgedünnt (Außenfläche bleibt glatt).
    #     Der Innen-Nocken überbrückt den ~1.94mm-Luftspalt bis kurz vor die
    #     gemessene Taster-Oberkante (-1.90mm), fb_nub_gap Ruheluft.
    recess_inner = iz0 - recess_d          # Pad-Innenfläche (Restwand innen)
    btn_top_z    = f.cm(-1.90)             # gemessene Taster-Oberkante (display-seitig)
    nub_tip_z    = btn_top_z - fb_nub_gap  # Nocken-Spitze
    hp = fb_pad / 2.0
    for by in btn_ys:
        sz0, sz1 = oz0 - e, recess_inner + e
        # U-Schlitz, rechte Seite (+X)
        f.cut(us, shell, f.box(us,
            btn_x + hp,           by - hp - fb_slot, sz0,
            btn_x + hp + fb_slot, by + hp + fb_slot, sz1))
        # oben (+Y)
        f.cut(us, shell, f.box(us,
            btn_x - hp, by + hp,           sz0,
            btn_x + hp, by + hp + fb_slot, sz1))
        # unten (−Y)
        f.cut(us, shell, f.box(us,
            btn_x - hp, by - hp - fb_slot, sz0,
            btn_x + hp, by - hp,           sz1))
        # Scharnier-Nut: Verbindungssteg (-X) von innen auf fb_hinge ausdünnen
        f.cut(us, shell, f.box(us,
            btn_x - hp - fb_hinge_w/2.0, by - hp, oz0 + fb_hinge,
            btn_x - hp + fb_hinge_w/2.0, by + hp, recess_inner + e))
        # Druck-Nocken auf der Pad-Innenseite
        f.join(us, shell, f.cylinder(us,
            btn_x, by, recess_inner - e, nub_tip_z, fb_nub_d))
    # Reset bleibt Pinhole (Ø btn_d)
    f.cut(us, shell, f.cylinder(us,
        rst_x, rst_y, oz0 - e, oz0 + wall + e, btn_d))
    print('  Flex-Taster D0/D1/D2 (Living-Hinge) + Reset-Pinhole')

    # 11. SD-Karten-Schlitz
    f.cut(us, shell, f.box(us,
        ix1 - e, sd_y0, sd_z0,
        ix1 + wall + e, sd_y1, sd_z1))
    print('  SD-Karten-Schlitz')

    # 12. Board-Schrauben M2
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - e, oz0 + csk_dep + e, csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - e, iz0 + so_h + e, screw_d))
    print('  Board-Schrauben (M2)')

    print('✓ Unterschale_v4 fertig!  ' + f.bbox_str(shell))
    print('  Lip: Spiess-Stil Δ, snap_d=' + str(round(snap_d*10,1))
          + ' mm, snap_h=' + str(round(snap_h*10,1)) + ' mm'
          + ', snap_top=' + str(round(snap_top*10,1)) + ' mm')
    print('  Parameter: Modify → Change Parameters')
