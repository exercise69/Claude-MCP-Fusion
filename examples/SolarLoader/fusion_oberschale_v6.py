"""
fusion_oberschale_v6.py — Oberschale V6 (Druck-Optimierung) mit Akkufach.

Basiert auf fusion_oberschale_v5.py. Änderung ggü. V5 (Hinweis Druckerei):
  - INNEN-RADIEN am RS485-Kabelausgang über ein abgerundetes Schnitt-Werkzeug
    (Parameter 'inner_r') — scharfe Innenecken sind Sollbruchstellen.

Akku-Geometrie, Notch-Nuten, M4-Löcher und Mating bleiben identisch zu V5.
Passt zur Unterschale_v6. V5 bleibt unverändert erhalten.
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
for _m in ('f360_helpers', 'solarloader_common', 'solarloader_v5'):
    if _m in sys.modules:
        del sys.modules[_m]
import f360_helpers as f
import solarloader_common as sl
import solarloader_v5 as sl5
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
    """Wie f.cut, aber das Schnitt-Werkzeug bekommt vorher Innen-Radien r."""
    tool = f.box(comp, x0, y0, z0, x1, y1, z1)
    if r > 1e-6:
        _fillet_axis_edges(comp, tool, r, axis)
    f.cut(comp, target, tool)


def run(_context):
    try:
        _build()
    except Exception:
        import traceback
        print('!!! FEHLER in fusion_oberschale_v6:\n' + traceback.format_exc())
        raise


def _build():
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. USER-PARAMETER ────────────────────────────────────────────────
    sl.define_common_params(des)
    sl5.define_batt_params(des)

    ow = False
    f.set_param(des, 'os_clear',  10.0,  'Luft ueber hoeherem Bauteil mm',     ow)
    f.set_param(des, 'rs485_z0',  23.0,  'RS485-Ausgang Z-Unterkante mm',      ow)
    f.set_param(des, 'rs485_z1',  32.0,  'RS485-Ausgang Z-Oberkante mm',       ow)
    f.set_param(des, 'mount_d',    4.2,  'M4-Montageloch Durchmesser mm',      ow)
    f.set_param(des, 'mount_x0',   5.4,  'Montageloch X-Position links mm',    ow)
    f.set_param(des, 'mount_x1', 44.2,   'Montageloch X-Position rechts mm',   ow)
    f.set_param(des, 'notch_extra_d', 0.15, 'Notch Mehrtiefe in Wand mm',      ow)
    f.set_param(des, 'notch_play',    0.10, 'Notch Spiel in Hohlraum mm',      ow)
    f.set_param(des, 'notch_z_play',  0.10, 'Notch Hoehen-Spiel mm',           ow)
    f.set_param(des, 'notch_x_play',  0.30, 'Notch X-Spiel je Ende mm',        ow)
    f.set_param(des, 'inner_r',       1.0,  'Innen-Radius Ausschnitt-Ecken mm', ow)

    # ── 2. PARAMETER EINLESEN ────────────────────────────────────────────
    wall      = f.get_param_cm(des, 'wall')
    clearance = f.get_param_cm(des, 'clearance')
    fillet_r  = f.get_param_cm(des, 'fillet_r')
    split_z   = f.get_param_cm(des, 'split_z')

    lip_h    = f.get_param_cm(des, 'lip_h')
    lip_gap  = f.get_param_cm(des, 'lip_gap')

    snap_d      = f.get_param_cm(des, 'snap_d')
    snap_h      = f.get_param_cm(des, 'snap_h')
    snap_margin = f.get_param_cm(des, 'snap_margin')
    snap_top    = f.get_param_cm(des, 'snap_top')

    os_clear  = f.get_param_cm(des, 'os_clear')
    rs485_y0  = f.get_param_cm(des, 'rs485_y0')
    rs485_y1  = f.get_param_cm(des, 'rs485_y1')
    rs485_z0  = f.get_param_cm(des, 'rs485_z0')
    rs485_z1  = f.get_param_cm(des, 'rs485_z1')
    mount_d   = f.get_param_cm(des, 'mount_d')
    mount_x0  = f.get_param_cm(des, 'mount_x0')
    mount_x1  = f.get_param_cm(des, 'mount_x1')

    notch_extra_d = f.get_param_cm(des, 'notch_extra_d')
    notch_play    = f.get_param_cm(des, 'notch_play')
    notch_z_play  = f.get_param_cm(des, 'notch_z_play')
    notch_x_play  = f.get_param_cm(des, 'notch_x_play')
    inner_r       = f.get_param_cm(des, 'inner_r')

    # Lasche-Params
    lasche_x0  = f.get_param_cm(des, 'lasche_x0')
    lasche_x1  = f.get_param_cm(des, 'lasche_x1')
    lasche_t   = f.get_param_cm(des, 'lasche_t')
    lasche_air = f.get_param_cm(des, 'lasche_air')
    lasche_len = f.get_param_cm(des, 'lasche_len')

    # ── 3. HARDWARE-KONSTANTEN ───────────────────────────────────────────
    pcb_cy    = sl.pcb_cy()
    e = f.cm(0.1)

    # ── 4. ABGELEITETE GEOMETRIE (V5: verbreitert + Akkufach + tiefer) ───
    ix0, ix1, iy0, iy1 = sl5.cavity_xy(des)
    iz1 = sl5.wall_iz1(des)               # Tiefe Richtung Wand (Akku-Rückseite)

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz1 = iz1 + wall

    # Akku-Extents (für Lasche)
    bx0, bx1, by0, by1, bz0, bz1 = sl5.batt_extents(des)

    # Notch-Geometrie
    nd  = snap_d - lip_gap + notch_extra_d
    ni  = lip_gap + notch_play
    nz1 = split_z + lip_h - snap_top
    nz0 = nz1 - snap_h - notch_z_play

    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    nx0 = lx0 + snap_margin - notch_x_play
    nx1 = lx1 - snap_margin + notch_x_play

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    for name in ('Oberschale', 'Oberschale_v2', 'Oberschale_v3',
                 'Oberschale_v4', 'Oberschale_v5'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Oberschale_v6')

    print('Erstelle Oberschale_v6 ...')
    os_occ = f.new_component(root, 'Oberschale_v6')
    oc = os_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(oc, ox0, oy0, split_z, ox1, oy1, oz1)
    shell.name = 'Oberschale_v6'
    f.fillet_z_edges(oc, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen (nimmt Steckzunge auf) — inkl. Akkufach (+Y)
    f.cut(oc, shell, f.box(oc, ix0, iy0, split_z - e,
                                ix1, iy1, iz1 + e))
    print('  Innenraum + Akkufach ausgehöhlt')

    # 3. Haltelasche (Wandseite kragt über Akku-Oberkante, mit Luft)
    #    Akku-Oberkante by0 (Y). Lasche-Unterkante = by0 - lasche_air.
    la_y1 = by0 - lasche_air               # näher am Akku (größeres Y unten)
    la_y0 = la_y1 - lasche_t               # zum PCB hin
    la_z1 = iz1 + wall                     # bis Aussenwand -> Ueberlappung
    la_z0 = iz1 - lasche_len               # kragt nach vorn (-Z)
    f.join(oc, shell, f.box(oc, lasche_x0, la_y0, la_z0,
                                lasche_x1, la_y1, la_z1))
    print('  Haltelasche (Wandseite, %.1f mm lang, %.1f mm Luft ueber Akku)'
          % (lasche_len*10, lasche_air*10))

    # 4. RS485-Kabelausgang (rechte Wand; Ecken verrundet -> Achse x)
    _rcut(oc, shell,
        ix1 - e, rs485_y0, rs485_z0,
        ix1 + wall + e, rs485_y1, rs485_z1, inner_r, 'x')
    print('  RS485-Kabelausgang (Ecken R%.1f)' % (inner_r * 10))

    # 5. Notch-Nuten (2 lange Y-Seiten)
    f.cut(oc, shell, f.box(oc, nx0, iy0 - nd, nz0, nx1, iy0 + ni, nz1))
    f.cut(oc, shell, f.box(oc, nx0, iy1 - ni, nz0, nx1, iy1 + nd, nz1))
    print('  Notch-Nuten (2× lange Y-Seite)')

    # 6. Montagelöcher M4 durch Deckel
    for mx in [mount_x0, mount_x1]:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - e, oz1 + e, mount_d))
    print('  Montagelöcher M4 (Ø' + str(round(mount_d*10, 1)) + 'mm × 2)')

    print('✓ Oberschale_v6 fertig!  ' + f.bbox_str(shell))
    print('  Innen X=%.1f..%.1f (%.1f)  Y=%.1f..%.1f (%.1f)  Z bis %.1f (Wand)'
          % (ix0*10, ix1*10, (ix1-ix0)*10, iy0*10, iy1*10, (iy1-iy0)*10, iz1*10))
