"""
solarloader_common.py — Gemeinsame Konstanten & Parameter für SolarLoader v4.

Wird von fusion_unterschale_v4.py UND fusion_oberschale_v4.py importiert, damit
Hardware-Maße und geteilte User-Parameter nur an EINER Stelle stehen
(kein Doppelt-Definieren, kein "wer zuletzt läuft, gewinnt").

Ablage: examples/SolarLoader/ — liegt via sys.path-Eintrag im Import-Pfad.
"""
import f360_helpers as f


# ── HARDWARE-KONSTANTEN (Adafruit-Feather-Stack, fest) ───────────────
# PCB-Footprint und Stack-Höhen, Maße in mm (→ cm via f.cm()).
ASM_X0, ASM_X1 = f.cm(-1.24), f.cm(50.83)
ASM_Y0, ASM_Y1 = f.cm(-0.04), f.cm(22.90)
PCB_Z0    = f.cm(-1.94)   # Unterkante Stack            (Bezug Unterschale)
PCB_TOP_Z = f.cm(34.0)    # Oberkante höchstes Bauteil  (Bezug Oberschale)


def pcb_cy():
    """Y-Mitte des PCB-Stacks (cm)."""
    return (ASM_Y0 + ASM_Y1) / 2.0


# ── GEMEINSAME USER-PARAMETER ────────────────────────────────────────
def define_common_params(des, overwrite=False):
    """
    Legt die von BEIDEN Schalen geteilten User-Parameter an.

    overwrite=False (Default): create-if-missing — vorhandene Werte bleiben
        unangetastet, damit manuelle Änderungen in Fusion einen Rebuild
        überleben.
    overwrite=True: Werte auf die hier hinterlegten Code-Defaults zurücksetzen.
    """
    # Gehäuse
    f.set_param(des, 'wall',        2.5,  'Wandstaerke mm',                     overwrite)
    f.set_param(des, 'clearance',   0.6,  'Luft um PCB-Stack mm',               overwrite)
    f.set_param(des, 'fillet_r',    2.0,  'Verrundungsradius Kanten mm',        overwrite)
    f.set_param(des, 'split_z',    22.0,  'Trennlinie Unter-/Oberschale mm',    overwrite)
    # Steckzunge
    f.set_param(des, 'lip_h',       4.0,  'Hoehe Steckzunge mm',                overwrite)
    f.set_param(des, 'lip_gap',     0.25, 'Toleranzspiel Steckzunge mm',        overwrite)
    # Spiess-Lip / Notch (Geometrie)
    f.set_param(des, 'snap_d',      0.8,  'Lip Ueberstand mm',                  overwrite)
    f.set_param(des, 'snap_h',      1.2,  'Lip Hoehe mm',                       overwrite)
    f.set_param(des, 'snap_margin', 3.0,  'Lip Randabstand mm',                 overwrite)
    f.set_param(des, 'snap_top',    2.0,  'Lip-Ueberstand ueber Rastleiste mm', overwrite)
    # RS485-Fenster (Y, von beiden Schalen genutzt)
    f.set_param(des, 'rs485_y0',    5.0,  'RS485 Y-Unterkante mm',              overwrite)
    f.set_param(des, 'rs485_y1',   18.0,  'RS485 Y-Oberkante mm',               overwrite)
