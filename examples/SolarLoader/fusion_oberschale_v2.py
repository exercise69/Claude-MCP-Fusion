"""
fusion_oberschale_v2.py — Oberschale mit vollständiger Fusion-Parametrisierung.

Alle Design-Parameter sind als Fusion User Parameters registriert
und in Modify → Change Parameters sichtbar und änderbar.
Hardware-Konstanten (PCB-BB, PCB-Bauhöhe) bleiben Python-Variablen.

Gemeinsame Parameter (wall, clearance, fillet_r, split_z, lip_h, lip_gap,
clip_w, clip_h, clip_p) werden beim Start neu registriert — existieren sie
bereits (weil fusion_unterschale_v3 vorher lief), werden sie nur bestätigt
(kein Fehler, kein Überschreiben abweichender Werte).

Oberschale-spezifische Parameter:
  os_clear    Luft über höchstem Bauteil (default 10 mm)
  rs485_y0/y1 RS485-Kabelausgang Y-Bereich
  rs485_z0/z1 RS485-Kabelausgang Z-Bereich
  mount_d     M4-Montageloch-Durchmesser
  mount_x0/x1 X-Positionen der zwei Montagelöcher

Änderungen gegenüber v1 (fusion_oberschale.py):
  - Alle Design-Knöpfe als Fusion User Parameters
  - Gemeinsame Parameter konsistent mit Unterschale_v3
  - Alte Oberschale wird versteckt (nicht gelöscht)
  - Idempotent: Oberschale_v2 wird bei Wiederholung gelöscht und neu erstellt
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

    # ── 1. FUSION USER PARAMETERS REGISTRIEREN ──────────────────────────
    # Sichtbar in: Modify → Change Parameters
    # Werte in mm — f.set_param konvertiert intern nach cm.

    # --- Gemeinsame Gehäuse-Parameter (gleich wie Unterschale_v3) ---
    f.set_param(des, 'wall',      2.5,   'Wandstaerke mm')
    f.set_param(des, 'clearance', 0.6,   'Luft um PCB-Stack mm')
    f.set_param(des, 'fillet_r',  2.0,   'Verrundungsradius Kanten mm')
    f.set_param(des, 'split_z',   22.0,  'Trennlinie Unter-/Oberschale mm')

    # --- Schnapp-Clips (gemeinsam — Fenster müssen zu Unterschale-Clips passen) ---
    f.set_param(des, 'lip_h',    4.0,   'Hoehe Steckzunge mm')
    f.set_param(des, 'lip_gap',  0.25,  'Toleranzspiel Steckzunge mm')
    f.set_param(des, 'clip_w',   6.0,   'Clip-Breite mm')
    f.set_param(des, 'clip_h',   2.0,   'Clip-Rasthoehe mm')
    f.set_param(des, 'clip_p',   0.5,   'Clip-Ueberstand ueber Steckzunge mm')

    # --- Oberschale-spezifisch ---
    f.set_param(des, 'os_clear',   10.0,  'Luft ueber hoeherem Bauteil mm')

    # --- RS485-Kabelausgang (rechte Wand, X+ Seite) ---
    f.set_param(des, 'rs485_y0',   5.0,   'RS485-Ausgang Y-Unterkante mm')
    f.set_param(des, 'rs485_y1',  18.0,   'RS485-Ausgang Y-Oberkante mm')
    f.set_param(des, 'rs485_z0',  23.0,   'RS485-Ausgang Z-Unterkante mm')
    f.set_param(des, 'rs485_z1',  32.0,   'RS485-Ausgang Z-Oberkante mm')

    # --- Montage-Löcher M4 (durch Deckel) ---
    f.set_param(des, 'mount_d',   4.2,   'M4-Montageloch Durchmesser mm')
    f.set_param(des, 'mount_x0',  5.4,   'Montageloch X-Position links mm')
    f.set_param(des, 'mount_x1', 44.2,   'Montageloch X-Position rechts mm')

    # ── 2. PARAMETER EINLESEN (alle in cm für Fusion-API) ───────────────
    wall      = f.get_param_cm(des, 'wall')
    clearance = f.get_param_cm(des, 'clearance')
    fillet_r  = f.get_param_cm(des, 'fillet_r')
    split_z   = f.get_param_cm(des, 'split_z')

    lip_h    = f.get_param_cm(des, 'lip_h')
    lip_gap  = f.get_param_cm(des, 'lip_gap')
    clip_w   = f.get_param_cm(des, 'clip_w')
    clip_h   = f.get_param_cm(des, 'clip_h')
    clip_p   = f.get_param_cm(des, 'clip_p')

    os_clear  = f.get_param_cm(des, 'os_clear')

    rs485_y0 = f.get_param_cm(des, 'rs485_y0')
    rs485_y1 = f.get_param_cm(des, 'rs485_y1')
    rs485_z0 = f.get_param_cm(des, 'rs485_z0')
    rs485_z1 = f.get_param_cm(des, 'rs485_z1')

    mount_d  = f.get_param_cm(des, 'mount_d')
    mount_x0 = f.get_param_cm(des, 'mount_x0')
    mount_x1 = f.get_param_cm(des, 'mount_x1')

    # ── 3. HARDWARE-KONSTANTEN ───────────────────────────────────────────
    # Durch die Hardware bestimmt — ändern sich nur bei anderem PCB-Stack.

    # PCB-Stack Bounding Box (Adafruit Feather-Stack)
    asm_x0, asm_x1 = f.cm(-1.24), f.cm(50.83)
    asm_y0, asm_y1 = f.cm(-0.04), f.cm(22.90)

    # Oberkante PCB-Stack inkl. RS485-Wing + Schraubklemmen
    pcb_top_z = f.cm(34.0)

    # PCB-Mitte Y (für Montageloch-Zentrierung)
    pcb_cy = (asm_y0 + asm_y1) / 2

    # ── 4. ABGELEITETE GEOMETRIE ─────────────────────────────────────────
    ix0, ix1 = asm_x0 - clearance, asm_x1 + clearance
    iy0, iy1 = asm_y0 - clearance, asm_y1 + clearance

    iz1 = pcb_top_z + os_clear   # Innendecke (34 + 10 = 44 mm)

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz1 = iz1 + wall             # Außendecke (44 + 2.5 = 46.5 mm)

    # Schnapp-Fenster-Geometrie (muss zu Unterschale-Clips passen)
    clip_z1 = split_z + lip_h          # Clip-Oberkante   = 22 + 4 = 26 mm
    clip_z0 = clip_z1 - clip_h         # Clip-Unterkante  = 26 - 2 = 24 mm
    pw      = clip_w + f.cm(0.4)       # Fensterbreite + Montagespiel
    ph      = clip_h + f.cm(0.5)       # Fensterhöhe   + Montagespiel
    pd      = clip_p + lip_gap + f.cm(0.1)  # Fenstertiefe in Wand

    cx_lip  = (ix0 + ix1) / 2
    pz0     = clip_z0 - f.cm(0.1)     # Fenster etwas tiefer starten
    pz1     = pz0 + ph

    # ── 5. MODELL ERSTELLEN ──────────────────────────────────────────────
    # v1 verstecken (nicht löschen)
    occ_v1 = f.find_occurrence(root, 'Oberschale')
    if occ_v1:
        occ_v1.isLightBulbOn = False
        print('Oberschale (v1) versteckt')

    # Alte v2 entfernen (Idempotenz)
    f.delete_component(root, 'Oberschale_v2')

    print('Erstelle Oberschale_v2 ...')
    os_occ = f.new_component(root, 'Oberschale_v2')
    oc = os_occ.component

    # 1. Außenhülle + Verrundung
    shell = f.box(oc, ox0, oy0, split_z, ox1, oy1, oz1)
    shell.name = 'Oberschale_v2'
    f.fillet_z_edges(oc, shell, fillet_r)
    print('  Außenhülle + Verrundung')

    # 2. Innenraum aushöhlen (nimmt Steckzunge der Unterschale auf)
    f.cut(oc, shell, f.box(oc, ix0, iy0, split_z - f.cm(0.1),
                                ix1, iy1, iz1 + f.cm(0.1)))
    print('  Innenraum ausgehöhlt')

    # 3. RS485-Kabelausgang (rechte Wand, X+ Seite)
    f.cut(oc, shell, f.box(oc,
        ix1 - f.cm(0.1), rs485_y0, rs485_z0,
        ix1 + wall + f.cm(0.1), rs485_y1, rs485_z1))
    print('  RS485-Kabelausgang  (Y=' + str(round((rs485_y1 - rs485_y0)*10, 1))
          + 'mm × Z=' + str(round((rs485_z1 - rs485_z0)*10, 1)) + 'mm)')

    # 4. Schnapp-Fenster in Innenwände (vorne + hinten, passend zu Unterschale-Clips)
    f.cut(oc, shell, f.box(oc,
        cx_lip - pw/2, iy0 - pd,        pz0,
        cx_lip + pw/2, iy0 + f.cm(0.1), pz1))
    f.cut(oc, shell, f.box(oc,
        cx_lip - pw/2, iy1 - f.cm(0.1), pz0,
        cx_lip + pw/2, iy1 + pd,        pz1))
    print('  Schnapp-Fenster (vorne + hinten)')

    # 5. Montage-Löcher M4 durch Deckel
    for mx in [mount_x0, mount_x1]:
        f.cut(oc, shell, f.cylinder(oc,
            mx, pcb_cy, iz1 - f.cm(0.1), oz1 + f.cm(0.1), mount_d))
    print('  Montagelöcher M4  (Ø' + str(round(mount_d*10, 1)) + 'mm × 2)')

    print('✓ Oberschale_v2 fertig!  ' + f.bbox_str(shell))
    print('  Parameter sichtbar unter: Modify → Change Parameters')
