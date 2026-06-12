"""
solarloader_battery.py — geteiltes Akku-/Innenraum-Modul für SolarLoader.

Wird von fusion_unterschale_v6.py UND fusion_oberschale_v6.py importiert, damit
beide Schalen exakt dieselbe Akku- und Innenraum-Geometrie verwenden und
mating-kompatibel bleiben.

Fügt unter dem PCB-Stack ein flach liegendes Akkufach für eine Li-Ion-Zelle
(Standard 40 × 28 × 5 mm) hinzu. Das Gehäuse wächst dafür nur in +Y ("nach
unten") um das Fach; die X-Außenkontur und die Tiefe bleiben unverändert, die
Display-Front bündig.

Die Hardware-Konstanten und die geteilten Schalen-Parameter kommen weiter aus
solarloader_common (sl). Hier liegen NUR die Akku-spezifischen Parameter und
die daraus abgeleitete, von BEIDEN Schalen geteilte XY-Innenraum-Geometrie.
"""
import f360_helpers as f
import solarloader_common as sl


def define_batt_params(des, overwrite=False):
    """Akku-/Fach-Parameter anlegen (create-if-missing)."""
    ow = overwrite
    # Akku-Maße (LiPo 40 × 28 × 5 mm) — passt ohne Geh.-Verbreiterung
    f.set_param(des, 'batt_w',      40.0, 'Akku Breite X mm',            ow)
    f.set_param(des, 'batt_t',       5.0, 'Akku Dicke Y mm',             ow)
    f.set_param(des, 'batt_depth',  28.0, 'Akku Tiefe Z mm',             ow)
    f.set_param(des, 'batt_xc',     25.0, 'Akku Mitte X mm',             ow)
    f.set_param(des, 'batt_top',    31.0, 'Akku Oberkante Y mm',         ow)
    f.set_param(des, 'batt_zfront', 14.0, 'Akku Front Z (Wandseite) mm', ow)
    # Luft / Wände
    f.set_param(des, 'batt_xclear',  0.5, 'Akku Luft X je Seite mm',     ow)
    f.set_param(des, 'batt_zclear',  0.5, 'Akku Luft Z je Seite mm',     ow)
    f.set_param(des, 'batt_floor',   0.7, 'Akku Luft unten Y mm',        ow)
    # Haltelasche (von Wandseite, hält Akku)
    f.set_param(des, 'lasche_x0',   15.0, 'Lasche X-Start mm',           ow)
    f.set_param(des, 'lasche_x1',   45.0, 'Lasche X-Ende mm',            ow)
    f.set_param(des, 'lasche_t',     1.6, 'Lasche Dicke Y mm',           ow)
    f.set_param(des, 'lasche_air',   1.0, 'Lasche Luft ueber Akku mm',   ow)
    f.set_param(des, 'lasche_len',   7.5, 'Lasche Laenge -Z ab Wand mm', ow)


def batt_extents(des):
    """Akku-Boundingbox in internen Einheiten (cm)."""
    w  = f.get_param_cm(des, 'batt_w')
    t  = f.get_param_cm(des, 'batt_t')
    d  = f.get_param_cm(des, 'batt_depth')
    xc = f.get_param_cm(des, 'batt_xc')
    top = f.get_param_cm(des, 'batt_top')
    zf  = f.get_param_cm(des, 'batt_zfront')
    bx0, bx1 = xc - w / 2.0, xc + w / 2.0
    by0, by1 = top, top + t
    bz0, bz1 = zf, zf + d
    return bx0, bx1, by0, by1, bz0, bz1


def cavity_xy(des):
    """
    Erweiterte XY-Innenraum-Grenzen (cm), die BEIDE Schalen teilen.
    Verbreitert für den 60-mm-Akku und verlängert in +Y um das Fach.
    Z bleibt schalenspezifisch (Unterschale iz0, Oberschale iz1).
    """
    clearance = f.get_param_cm(des, 'clearance')
    xcl = f.get_param_cm(des, 'batt_xclear')
    flo = f.get_param_cm(des, 'batt_floor')
    bx0, bx1, by0, by1, bz0, bz1 = batt_extents(des)

    ix0 = min(sl.ASM_X0 - clearance, bx0 - xcl)
    ix1 = max(sl.ASM_X1 + clearance, bx1 + xcl)
    iy0 = sl.ASM_Y0 - clearance          # Oberkante (oben) unverändert
    iy1 = by1 + flo                      # Unterkante: Akku-Unterkante + Luft
    return ix0, ix1, iy0, iy1


def wall_iz1(des):
    """Innenraum-Z auf der Wandseite (cm): tief genug für Akku-Rückseite."""
    zcl = f.get_param_cm(des, 'batt_zclear')
    _, _, _, _, _, bz1 = batt_extents(des)
    iz1_pcb = sl.PCB_TOP_Z + f.get_param_cm(des, 'os_clear')
    return max(iz1_pcb, bz1 + zcl)
