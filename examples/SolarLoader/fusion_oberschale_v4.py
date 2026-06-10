"""
fusion_oberschale_v4.py — Oberschale mit Spiess-Stil Notch-Nuten (female part).

Passend zu fusion_unterschale_v4.py.

Gemeinsame Hardware-Konstanten und geteilte Parameter kommen aus
solarloader_common (define_common_params) — kein Doppelt-Definieren mehr.

Parameter-Philosophie: create-if-missing (overwrite=False). Werte, die du in
Fusion unter Modify → Change Parameters änderst, überleben einen Rebuild.

Änderungen gegenüber v3:
  - 4 Eck-Nuten ersetzt durch 2 durchgehende Notch-Nuten auf den langen Y-Seiten
  - Notch nimmt die dreieckige Lip-Leiste der Unterschale_v4 auf
  - Rechteckige Tasche: flache Rastfläche der Lip (snap_z1) fängt sich unter der Decke
  - Fit-Toleranzen als eigene Parameter (notch_extra_d / notch_play /
    notch_z_play / notch_x_play) statt vergrabener Magic Numbers

Geometrie der Notch-Tasche:
  nd = snap_d - lip_gap + notch_extra_d → Tiefe in die Wand (nimmt Lip-Spitze auf)
  ni = lip_gap + notch_play             → Tiefe in den Hohlraum (Spiel)
  nz1 = split_z + lip_h - snap_top      → Notch-Oberkante (Rast-Ledge darüber)
  nz0 = nz1 - snap_h - notch_z_play     → Notch-Unterkante
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
        print('!!! FEHLER in fusion_oberschale_v4:\n' + traceback.format_exc())
        raise


def _build():
    app  = adsk.core.Application.get()
    des  = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent

    # ── 1. USER-PARAMETER ────────────────────────────────────────────────
    sl.define_common_params(des)          # geteilte Params (create-if-missing)

    ow = False                            # overwrite=False für alle Specifics
    # Oberschale-spezifisch
    f.set_param(des, 'os_clear',  10.0,  'Luft ueber hoeherem Bauteil mm',     ow)
    f.set_param(des, 'rs485_z0',  23.0,  'RS485-Ausgang Z-Unterkante mm',      ow)
    f.set_param(des, 'rs485_z1',  32.0,  'RS485-Ausgang Z-Oberkante mm',       ow)
    f.set_param(des, 'mount_d',    4.2,  'M4-Montageloch Durchmesser mm',      ow)
    f.set_param(des, 'mount_x0',   5.4,  'Montageloch X-Position links mm',    ow)
    f.set_param(des, 'mount_x1', 44.2,   'Montageloch X-Position rechts mm',   ow)
    # Notch-Fit-Toleranzen (vorher Magic Numbers im Code)
    f.set_param(des, 'notch_extra_d', 0.15, 'Notch Mehrtiefe in Wand mm',      ow)
    f.set_param(des, 'notch_play',    0.10, 'Notch Spiel in Hohlraum mm',      ow)
    f.set_param(des, 'notch_z_play',  0.10, 'Notch Hoehen-Spiel mm',           ow)
    f.set_param(des, 'notch_x_play',  0.30, 'Notch X-Spiel je Ende mm',        ow)

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

    # ── 3. HARDWARE-KONSTANTEN (aus solarloader_common) ──────────────────
    asm_x0, asm_x1 = sl.ASM_X0, sl.ASM_X1
    asm_y0, asm_y1 = sl.ASM_Y0, sl.ASM_Y1
    pcb_top_z = sl.PCB_TOP_Z
    pcb_cy    = sl.pcb_cy()

    e = f.cm(0.1)   # kleines Übermaß für saubere Schnitte

    # ── 4. ABGELEITETE GEOMETRIE ──────────────────────────────────────────
    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance

    iz1 = pcb_top_z + os_clear

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz1 = iz1 + wall

    # Notch-Geometrie (passend zur Lip der Unterschale_v4)
    nd  = snap_d - lip_gap + notch_extra_d   # Tiefe in die Wand (nimmt Lip-Spitze auf)
    ni  = lip_gap + notch_play               # Tiefe in den Hohlraum (Spiel)
    nz1 = split_z + lip_h - snap_top         # Notch-Oberkante (Rast-Ledge), = snap_z1
    nz0 = nz1 - snap_h - notch_z_play        # Notch-Unterkante

    # Lip-X-Bereich (identisch zur Unterschale) + notch_x_play Spiel je Ende
    lx0, lx1 = ix0 + lip_gap, ix1 - lip_gap
    nx0 = lx0 + snap_margin - notch_x_play
    nx1 = lx1 - snap_margin + notch_x_play

    # ── 5. MODELL ERSTELLEN ───────────────────────────────────────────────
    for name in ('Oberschale', 'Oberschale_v2', 'Oberschale_v3'):
        occ = f.find_occurrence(root, name)
        if occ:
            occ.isLightBulbOn = False
    f.delete_component(root, 'Oberschale_v4')

    print('Erstelle Oberschale_v4 ...')
    os_occ = f.new_component(root, 'Oberschale_v4')
    oc = os_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(oc, ox0, oy0, split_z, ox1, oy1, oz1)
    shell.name = 'Oberschale_v4'
    f.fillet_z_edges(oc, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen (nimmt Steckzunge auf)
    f.cut(oc, shell, f.box(oc, ix0, iy0, split_z - e,
                                ix1, iy1, iz1 + e))
    print('  Innenraum ausgehöhlt')

    # 3. RS485-Kabelausgang (rechte Wand)
    f.cut(oc, shell, f.box(oc,
        ix1 - e, rs485_y0, rs485_z0,
        ix1 + wall + e, rs485_y1, rs485_z1))
    print('  RS485-Kabelausgang  ('
          + str(round((rs485_y1-rs485_y0)*10,1)) + 'mm × '
          + str(round((rs485_z1-rs485_z0)*10,1)) + 'mm)')

    # 4. Notch-Nuten (2 lange Y-Seiten, passend zur Lip der Unterschale_v4)
    #
    #  Rechteckige Tasche in der Innenwand. Die flache Rastfläche der Lip
    #  (Oberkante bei nz1) fängt sich unter der Decke der Tasche (Ledge ab nz1).
    #
    #  Front (iy0): Tasche reicht von iy0-nd (in die Wand) bis iy0+ni (in den Hohlraum)
    f.cut(oc, shell, f.box(oc, nx0, iy0 - nd, nz0, nx1, iy0 + ni, nz1))
    #  Hinten (iy1): Tasche reicht von iy1-ni (Hohlraum) bis iy1+nd (in die Wand)
    f.cut(oc, shell, f.box(oc, nx0, iy1 - ni, nz0, nx1, iy1 + nd, nz1))
    print('  Notch-Nuten (2× lange Y-Seite, '
          + str(round((nx1 - nx0) * 10, 1)) + ' mm lang)')

    # 5. Montagelöcher M4 durch Deckel
    for mx in [mount_x0, mount_x1]:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - e, oz1 + e, mount_d))
    print('  Montagelöcher M4  (Ø' + str(round(mount_d*10, 1)) + 'mm × 2)')

    print('✓ Oberschale_v4 fertig!  ' + f.bbox_str(shell))
    print('  Notch: Spiess-Stil, snap_d=' + str(round(snap_d*10,1))
          + ' mm, snap_h=' + str(round(snap_h*10,1)) + ' mm'
          + ', nd=' + str(round(nd*10,2)) + ' mm')
    print('  Parameter: Modify → Change Parameters')
