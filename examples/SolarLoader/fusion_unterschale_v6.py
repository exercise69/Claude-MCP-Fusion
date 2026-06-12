"""
fusion_unterschale_v6.py — Unterschale V6 (Druck-Optimierung) mit Akkufach.

Druck-optimierte Bodenschale (Merkmale u.a. nach Druckerei-Hinweisen):
  - INNEN-RADIEN an den Ausschnitten (TFT-Fenster, Display-Mulde, USB-C, SD)
    über abgerundete Schnitt-Werkzeuge — scharfe Innenecken sind Sollbruch-
    stellen. Radius = Parameter 'inner_r'.
  - DICKERE DISPLAY-FRONT: Parameter 'front_extra' verschiebt die Außen-Front
    um diesen Betrag nach außen (-Z). Die dünne Bezel-Restwand unter dem
    Display wächst damit (1,2 → ~1,7 mm), OHNE die Display-Einbautiefe zu
    ändern (Mulde bleibt relativ zu iz0). Das Glas sitzt nur 'front_extra'
    geschützt versenkt.

Akku-Geometrie & Schalen-Mating kommen aus solarloader_battery
(cavity_xy / batt_extents), geteilt mit fusion_oberschale_v6.py.
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
for _m in ('f360_helpers', 'solarloader_common', 'solarloader_battery'):
    if _m in sys.modules:
        del sys.modules[_m]
import f360_helpers as f
import solarloader_common as sl
import solarloader_battery as slb
import adsk.core, adsk.fusion


def _fillet_axis_edges(comp, body, r, axis):
    """Verrundet die 4 zur 'axis' (x|y|z) parallelen Kanten eines Quaders."""
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        a = e.startVertex.geometry
        b = e.endVertex.geometry
        dx, dy, dz = abs(b.x - a.x), abs(b.y - a.y), abs(b.z - a.z)
        if axis == 'z' and dz >= dx and dz >= dy and dz > 1e-6:
            edges.add(e)
        elif axis == 'x' and dx >= dy and dx >= dz and dx > 1e-6:
            edges.add(e)
        elif axis == 'y' and dy >= dx and dy >= dz and dy > 1e-6:
            edges.add(e)
    if edges.count:
        fi = comp.features.filletFeatures.createInput()
        fi.addConstantRadiusEdgeSet(
            edges, adsk.core.ValueInput.createByReal(r), True)
        comp.features.filletFeatures.add(fi)


def _rcut(comp, target, x0, y0, z0, x1, y1, z1, r, axis):
    """Wie f.cut, aber das Schnitt-Werkzeug bekommt vorher Innen-Radien r
    an den zur 'axis' parallelen Kanten -> abgerundete Ausschnitt-Ecken."""
    tool = f.box(comp, x0, y0, z0, x1, y1, z1)
    if r > 1e-6:
        _fillet_axis_edges(comp, tool, r, axis)
    f.cut(comp, target, tool)


def run(_context):
    try:
        _build()
    except Exception:
        import traceback
        print('!!! FEHLER in fusion_unterschale_v6:\n' + traceback.format_exc())
        raise


def _build():
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. USER-PARAMETER ────────────────────────────────────────────────
    sl.define_common_params(des)          # geteilte Params (create-if-missing)
    slb.define_batt_params(des)           # Akku-Params (create-if-missing)

    ow = False                            # overwrite=False für alle Specifics
    f.set_param(des, 'lipo_h',      0.0,  'LiPo-Hoehenaufschlag mm',          ow)
    f.set_param(des, 'lip_wall',    1.6,  'Wandstaerke Steckzunge mm',        ow)
    f.set_param(des, 'lip_foot',    1.2,  'Schulterhoehe Zungenbasis mm',     ow)
    f.set_param(des, 'inner_r',     1.0,  'Innen-Radius Ausschnitt-Ecken mm', ow)
    f.set_param(des, 'front_extra', 0.5,  'Display-Front Mehrdicke mm',       ow)
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
    lip_foot    = f.get_param_cm(des, 'lip_foot')
    lip_gap     = f.get_param_cm(des, 'lip_gap')
    inner_r     = f.get_param_cm(des, 'inner_r')
    front_extra = f.get_param_cm(des, 'front_extra')

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

    # ── 3. HARDWARE-KONSTANTEN ───────────────────────────────────────────
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

    # ── 4. ABGELEITETE GEOMETRIE (V5: verbreitert + Akkufach) ────────────
    iz0 = pcb_z0 - f.cm(0.6)

    # XY-Innenraum jetzt aus solarloader_battery (geteilt mit Oberschale)
    ix0, ix1, iy0, iy1 = slb.cavity_xy(des)

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0 = iz0 - wall - front_extra      # Front dicker: Bezel-Restwand waechst

    usbc_y0 = pcb_cy - usbc_half
    usbc_y1 = pcb_cy + usbc_half

    # Lip-Maße
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    ly0, ly1 = iy0 + lip_gap, iy1 - lip_gap

    snap_z1 = split_z + lip_h - snap_top
    snap_z0 = snap_z1 - snap_h
    lip_x0  = lx0 + snap_margin
    lip_x1  = lx1 - snap_margin

    e = f.cm(0.1)

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    for name in ('Unterschale', 'Unterschale_v2', 'Unterschale_v3',
                 'Unterschale_v3_1', 'Unterschale_v4', 'Unterschale_v4 (1)',
                 'Unterschale_v5'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Unterschale_v6')

    print('Erstelle Unterschale_v6 ...')
    us_occ = f.new_component(root, 'Unterschale_v6')
    us = us_occ.component

    # 1. Hoher Quader: Shell + Lip als EIN Körper
    shell = f.box(us, ox0, oy0, oz0, ox1, oy1, split_z + lip_h)
    shell.name = 'Unterschale_v6'
    f.fillet_z_edges(us, shell, fillet_r)
    print('  Außenhülle + Verrundung (oz0 → split_z+lip_h)')

    # 2. Innenraum aushöhlen — Kavität endet lip_foot unter split_z, damit
    #    unter dem Zungen-Ring eine MASSIVE Schulter stehen bleibt, die die
    #    Zunge solide mit der Gehäusewand verbindet (kein 0.1-mm-Steg mehr).
    f.cut(us, shell, f.box(us, ix0, iy0, iz0, ix1, iy1, split_z - lip_foot))
    print('  Innenraum + Akkufach ausgehöhlt (Schulter %.1f mm bleibt)'
          % (lip_foot * 10))

    # 3. Standoffs (PCB-Ecken, im oberen Y-Bereich)
    for px, py in so_pos:
        f.join(us, shell, f.cylinder(us, px, py, iz0, iz0 + so_h, so_od))
    print('  Standoffs')

    # 4. Oberhalb split_z: Lip-Form herausschneiden
    f.cut(us, shell, f.box(us, ox0-e, oy0-e, split_z, lx0, oy1+e, split_z+lip_h+e))
    f.cut(us, shell, f.box(us, lx1, oy0-e, split_z, ox1+e, oy1+e, split_z+lip_h+e))
    f.cut(us, shell, f.box(us, lx0, oy0-e, split_z, lx1, ly0, split_z+lip_h+e))
    f.cut(us, shell, f.box(us, lx0, ly1, split_z, lx1, oy1+e, split_z+lip_h+e))
    print('  Lip-Außenform geschnitten (Shell+Lip = 1 Körper)')

    # 5. Lip innen aushöhlen — bis unter die Schulter (split_z - lip_foot),
    #    damit der Innenraum offen bleibt und die Schulter nur als RING
    #    (Wand-Innenfläche → Zungen-Innenfläche) stehen bleibt.
    f.cut(us, shell, f.box(us,
        lx0 + lip_wall, ly0 + lip_wall, split_z - lip_foot - e,
        lx1 - lip_wall, ly1 - lip_wall, split_z + lip_h + e))
    print('  Lip innen ausgehöhlt (Schulter bleibt als Ring)')

    # 5b. RS485-Aussparung (rechte Steckzungen-Wand) — bis unter die Schulter,
    #     damit der Kabelkanal nicht von der neuen Schulter blockiert wird.
    f.cut(us, shell, f.box(us,
        lx1 - lip_wall - e, rs485_y0, split_z - lip_foot - e,
        lx1 + e,           rs485_y1, split_z + lip_h + e))
    print('  RS485-Aussparung in Steckzunge')

    # 6. Spiess-Lip (dreieckige Leiste auf beiden langen Y-Seiten).
    #    Basis ragt um e in die Lip-Wand (Ueberlappung), damit join() sicher
    #    greift -> Schnappnocken werden TEIL der Schale (eine Body, druckbar).
    lip_front = f.triangle_prism_x(us,
        lip_x0, lip_x1,
        ly0 + e,      snap_z1,
        ly0 + e,      snap_z0,
        ly0 - snap_d, snap_z0)
    f.join(us, shell, lip_front)

    lip_back = f.triangle_prism_x(us,
        lip_x0, lip_x1,
        ly1 - e,      snap_z1,
        ly1 - e,      snap_z0,
        ly1 + snap_d, snap_z0)
    f.join(us, shell, lip_back)
    print('  Spiess-Lip (2× Δ, %s mm) — mit Schale verbunden'
          % str(round((lip_x1 - lip_x0) * 10, 1)))

    # 7. Display-Mulde von innen (Ecken verrundet)
    _rcut(us, shell,
        recess_x0, recess_y0, iz0 - recess_d - e,
        recess_x1, recess_y1, iz0 + e, inner_r, 'z')
    print('  Display-Mulde (Ecken R%.1f)' % (inner_r * 10))

    # 8. TFT-Fenster (Ecken verrundet) — durch die ganze (dickere) Front bis iz0
    _rcut(us, shell,
        disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - e,
        disp_cx + disp_w/2, disp_cy + disp_h/2, iz0 + e, inner_r, 'z')
    print('  TFT-Fenster (Ecken R%.1f)' % (inner_r * 10))

    # 9. USB-C-Schlitz (Ecken verrundet; Durchbruch in -X-Wand -> Achse x)
    _rcut(us, shell,
        ox0 - e, usbc_y0, usbc_z0,
        ix0 + f.cm(4.0), usbc_y1, usbc_z1, inner_r, 'x')
    print('  USB-C-Schlitz (Ecken R%.1f)' % (inner_r * 10))

    # 10. Flex-Taster D0/D1/D2 + Reset-Pinhole
    recess_inner = iz0 - recess_d
    btn_top_z    = f.cm(-1.90)
    nub_tip_z    = btn_top_z - fb_nub_gap
    hp = fb_pad / 2.0
    for by in btn_ys:
        sz0, sz1 = oz0 - e, recess_inner + e
        f.cut(us, shell, f.box(us,
            btn_x + hp,           by - hp - fb_slot, sz0,
            btn_x + hp + fb_slot, by + hp + fb_slot, sz1))
        f.cut(us, shell, f.box(us,
            btn_x - hp, by + hp,           sz0,
            btn_x + hp, by + hp + fb_slot, sz1))
        f.cut(us, shell, f.box(us,
            btn_x - hp, by - hp - fb_slot, sz0,
            btn_x + hp, by - hp,           sz1))
        f.cut(us, shell, f.box(us,
            btn_x - hp - fb_hinge_w/2.0, by - hp, oz0 + fb_hinge,
            btn_x - hp + fb_hinge_w/2.0, by + hp, recess_inner + e))
        f.join(us, shell, f.cylinder(us,
            btn_x, by, recess_inner - e, nub_tip_z, fb_nub_d))
    f.cut(us, shell, f.cylinder(us,
        rst_x, rst_y, oz0 - e, iz0 + e, btn_d))
    print('  Flex-Taster D0/D1/D2 + Reset-Pinhole')

    # 11. SD-Karten-Schlitz (innen bis Board-Kante verankert; Ecken verrundet,
    #     Durchbruch in +X-Wand -> Achse x)
    _rcut(us, shell,
        f.cm(53.0), sd_y0, sd_z0,
        ix1 + wall + e, sd_y1, sd_z1, inner_r, 'x')
    print('  SD-Karten-Schlitz (Ecken R%.1f)' % (inner_r * 10))

    # 12. Board-Schrauben M2
    for px, py in so_pos:
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - e, oz0 + csk_dep + e, csk_d))
        f.cut(us, shell, f.cylinder(us, px, py,
            oz0 - e, iz0 + so_h + e, screw_d))
    print('  Board-Schrauben (M2)')

    print('✓ Unterschale_v6 fertig!  ' + f.bbox_str(shell))
    print('  Innen X=%.1f..%.1f (%.1f)  Y=%.1f..%.1f (%.1f)'
          % (ix0*10, ix1*10, (ix1-ix0)*10, iy0*10, iy1*10, (iy1-iy0)*10))
    print('  Front-Bezel jetzt %.1f mm (Wand %.1f + front_extra %.1f - Mulde %.1f)'
          % ((wall + front_extra - recess_d)*10, wall*10, front_extra*10, recess_d*10))
