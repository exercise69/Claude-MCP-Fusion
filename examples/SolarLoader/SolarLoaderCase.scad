// ============================================================
// SolarLoader Gehäuse — parametrisch
// Importiert das echte Adafruit-Assembly-STL aus Fusion 360
// ============================================================

// --- PARAMETER (hier anpassen) ---
wall        = 2.5;    // Wandstärke mm
clearance   = 0.6;    // Luft um den Stack mm
split_z     = 22.0;   // Trennlinie Unter-/Oberschale mm
fillet      = 2.0;    // Verrundungsradius (aktuell nur optisch)
show_boards = true;   // Stack einblenden (zum Überprüfen)
show_lower  = true;   // Unterschale zeigen
show_upper  = true;   // Oberschale zeigen
explode     = 8;      // mm Abstand für Explosionsdarstellung (0 = zusammen)

// --- ABGELEITETE GRÖßEN (aus Assembly Bounding Box) ---
// Assembly X=-1.24..50.83, Y=-0.04..22.90, Z=-1.94..31.71
asm_x0=-1.24; asm_x1=50.83;
asm_y0=-0.04; asm_y1=22.90;
asm_z0=-1.94; asm_z1=31.71;  // Stack-Höhe (ohne Schraubklemme oben)
top_z  = 34.0;  // bis hier gehen Bauteile der RS485 + Klemme

// Innenraum
ix0 = asm_x0 - clearance;   // -1.84
ix1 = asm_x1 + clearance;   // 51.43
iy0 = asm_y0 - clearance;   // -0.64
iy1 = asm_y1 + clearance;   // 23.50
iz0 = asm_z0 - 0.6;         // -2.54  (Puffer unter Display)
iz1 = top_z  + 10.0;        // 44.0   (10mm Luft über Klemme)

// Außenmaße
ox0 = ix0 - wall;  // -4.34
ox1 = ix1 + wall;  //  53.93
oy0 = iy0 - wall;  // -3.14
oy1 = iy1 + wall;  //  26.00
oz0 = iz0 - wall;  // -5.04  (Boden = Vorderseite mit Display)
oz1 = iz1 + wall;  //  37.5  (Deckel)

// --- DISPLAY-FENSTER ---
disp_w  = 25.5;   // Öffnung Breite (Display aktiv 24.9mm + Toleranz)
disp_h  = 15.4;   // Öffnung Höhe  (Display aktiv 14.8mm + Toleranz)
// Display-Glas-Mitte aus STL-Analyse (Z≈-1.5mm Schicht):
// Modul-BB X=12.41..40.10 → Mitte 26.26mm  (PCB-Mitte wäre nur 24.8mm → zu weit links)
// Modul-BB Y=2.56..20.11  → Mitte 11.34mm
disp_cx = 26.26;  // Display-Mitte X (aus STL-Analyse)
disp_cy = 11.35;  // Display-Mitte Y (aus STL-Analyse)
pcb_cx  = (asm_x0+asm_x1)/2;  // PCB-Mitte X ≈ 24.8mm (für USB-C / Montage)
pcb_cy  = (asm_y0+asm_y1)/2;  // PCB-Mitte Y ≈ 11.4mm

// --- USB-C SCHLITZ ---
usbc_y0 = pcb_cy - 5.0;  usbc_y1 = pcb_cy + 5.0;   // 10mm breit
usbc_z0 = -0.5;           usbc_z1 =  5.8;            //  6.3mm hoch, zentriert auf Connector (0.57..4.77mm)

// --- TASTER-KANÄLE D0/D1/D2 ---
btn_ys   = [4.4, 11.4, 18.4];  // Y-Positionen
btn_size = 3.5;                  // Kanalbreite/-höhe
btn_z_c  = 2.5;                  // Z-Mitte (ESP32 Komponentenseite)
btn_x1   = 8.5;                  // bis hierher einschneiden (Taster bei X=7.6)

// --- RS485-KABELAUSGANG ---
rs485_y0 = 5.0;  rs485_y1 = 18.0;   // 13mm breit
rs485_z0 = 23.0; rs485_z1 = 32.0;   //  9mm hoch

// --- MONTAGE-LÖCHER im Deckel ---
mount_xs = [5.4, 44.2];   // X-Positionen M4 Ø4.2mm — symmetrisch, je 9.7mm vom Rand
mount_y  = pcb_cy;
mount_d  = 4.2;

// --- STANDOFFS ---
so_pos = [[2.54,2.54],[2.54,20.32],[48.26,1.84],[48.26,20.96]];
so_od  = 5.0;  so_h = 2.5;  so_hole_d = 2.2;

// --- BOARD-SCHRAUBEN (M2 Senkkopf von Display-Seite) ---
// M2×8mm Senkkopfschraube durch oz0-Fläche → Standoff → PCB-Montageloch
// Standoff-Loch (Ø2.2mm) ist bereits im Standoff; diese Löcher verbinden
// es mit der Außenseite des Gehäusebodens.
screw_d   = 2.2;   // Durchgangsloch-Ø (M2-Schaft passt durch)
csk_d     = 4.0;   // Senkung-Ø (M2-Senkkopf Ø3.8mm + 0.2mm Spiel)
csk_depth = 1.5;   // Senkungstiefe mm

// --- TASTER-STIFTLÖCHER (Vorderseite, links neben Display-Fenster) ---
// Ø2.5mm Löcher durch den Gehäuseboden → Taster mit Kugelschreiber bedienen
// Positionen (PCB-/Fusion-Koordinaten):
btn_hole_d = 2.5;   // Loch-Ø mm
btn_hole_x  = 7.6;  // X der D0/D1/D2-Taster (PCB-Koordinate ≈ Fusion-Koordinate)
rst_hole_x  = 44.5; // X des Reset-Tasters (Display-Seite, rechts vom Display — aus STL-Analyse)
rst_hole_y  = 11.5; // Y des Reset-Tasters (Display-Seite, mittig — aus STL-Analyse)

// --- SD-KARTEN-SCHLITZ (rechte Wand der Unterschale) ---
// Aus STL-Analyse: SD-Halter-Öffnung an X=50.8mm: Y=3.6..16.8mm, Z=10.0..13.4mm
// (Adalogger FeatherWing, SD-Schacht auf Komponentenseite)
sd_y0 = 3.0;    // Y-Start mit 0.6mm Toleranz
sd_y1 = 17.5;   // Y-Ende  mit 0.7mm Toleranz
sd_z0 = 9.3;    // Z-Unterkante mit 0.7mm Puffer
sd_z1 = 14.0;   // Z-Oberkante  mit 0.6mm Puffer

// --- VERBINDUNG OBER-/UNTERSCHALE: Steckzunge ---
// Die Unterschale hat oben einen umlaufenden Rahmen (Zunge), der in die Oberschale
// gleitet. Die Oberschale braucht kein extra Feature — die Zunge passt in den
// vorhandenen Innenraum.
// Beim Zusammenbau: Unterschale von unten in Oberschale schieben (Z-Richtung).
lip_h    = 4.0;   // Höhe der Zunge (überragt split_z in Richtung Oberschale)
lip_wall = 1.5;   // Wandstärke der Zunge mm
lip_gap  = 0.25;  // Toleranzspiel Zunge ↔ Oberschale-Innenraum (für 3D-Druck)

// ============================================================
// MODULE
// ============================================================

// ----------------------------------------------------------
// Abgerundete Außenschale: linear_extrude eines Minkowski-
// Rounded-Rectangle → rundet die 4 vertikalen Kanten mit
// Radius `fillet`. Deckel, Boden und Trennlinie bleiben FLACH.
// ----------------------------------------------------------
module rounded_shell(x0, y0, x1, y1, z0, z1) {
    translate([x0 + fillet, y0 + fillet, z0])
        linear_extrude(height = z1 - z0)
            minkowski() {
                square([x1 - x0 - 2*fillet, y1 - y0 - 2*fillet]);
                circle(r = fillet, $fn = 32);
            }
}

module display_window() {
    translate([disp_cx - disp_w/2, disp_cy - disp_h/2, oz0 - 0.1])
        cube([disp_w, disp_h, wall + 0.2]);
}

module usbc_slot() {
    translate([ox0 - 0.1, usbc_y0, usbc_z0])
        cube([wall + 4.0, usbc_y1 - usbc_y0, usbc_z1 - usbc_z0]);
}

module button_channels() {
    for (by = btn_ys)
        translate([ox0 - 0.1, by - btn_size/2, btn_z_c - btn_size/2])
            cube([btn_x1 - ox0 + 0.1, btn_size, btn_size]);
}

module rs485_hole() {
    translate([ix1 - 0.1, rs485_y0, rs485_z0])
        cube([wall + 1.0, rs485_y1 - rs485_y0, rs485_z1 - rs485_z0]);
}

module button_pinholes() {
    // D0, D1, D2 — durch den Gehäuseboden (oz0-Fläche)
    for (by = btn_ys)
        translate([btn_hole_x, by, oz0 - 0.1])
            cylinder(d=btn_hole_d, h=wall + 0.2, $fn=16);
    // Reset
    translate([rst_hole_x, rst_hole_y, oz0 - 0.1])
        cylinder(d=btn_hole_d, h=wall + 0.2, $fn=16);
}

module sd_slot() {
    // Schlitz durch die rechte Wand der Unterschale für microSD-Zugang
    translate([ix1 - 0.1, sd_y0, sd_z0])
        cube([wall + 0.2, sd_y1 - sd_y0, sd_z1 - sd_z0]);
}

module mount_holes() {
    for (mx = mount_xs)
        translate([mx, mount_y, iz1 - 0.1])
            cylinder(d=mount_d, h=wall + 0.2, $fn=24);
}

module standoffs() {
    for (p = so_pos)
        translate([p[0], p[1], iz0])
            difference() {
                cylinder(d=so_od, h=so_h, $fn=24);
                cylinder(d=so_hole_d, h=so_h + 0.1, $fn=16);
            }
}

// ----------------------------------------------------------
// Board-Schraubenlöcher: M2-Senkkopfschraube von außen (oz0)
// durch Gehäusewand bis in den Standoff.
// Schraube: M2×8mm Senkkopf (DIN 7991 / ISO 10642)
// ----------------------------------------------------------
module board_screw_holes() {
    for (p = so_pos)
        translate([p[0], p[1], oz0 - 0.1]) {
            // Konische Senkung für Senkkopf (90°)
            cylinder(d1=csk_d, d2=screw_d, h=csk_depth + 0.1, $fn=24);
            // Zylindrisches Durchgangsloch durch die Gehäusewand
            cylinder(d=screw_d, h=iz0 - oz0 + 0.3, $fn=16);
        }
}

// ----------------------------------------------------------
// Steckzunge: umlaufender Rahmen an der Oberkante der Unterschale.
// Außenmaß = Innenraum (ix/iy) minus lip_gap → gleitet satt in Oberschale.
// Wandstärke lip_wall, Höhe lip_h.
// ----------------------------------------------------------
module connection_lip() {
    lx0 = ix0 + lip_gap;
    lx1 = ix1 - lip_gap;
    ly0 = iy0 + lip_gap;
    ly1 = iy1 - lip_gap;
    translate([lx0, ly0, split_z])
        difference() {
            cube([lx1 - lx0, ly1 - ly0, lip_h]);
            translate([lip_wall, lip_wall, -0.1])
                cube([lx1-lx0 - 2*lip_wall, ly1-ly0 - 2*lip_wall, lip_h + 0.2]);
        }
}

// ============================================================
// UNTERSCHALE
// ============================================================
module unterschale() {
    difference() {
        rounded_shell(ox0, oy0, ox1, oy1, oz0, split_z);
        translate([ix0, iy0, iz0])
            cube([ix1-ix0, iy1-iy0, split_z - iz0 + 0.1]);
        display_window();
        usbc_slot();
        button_pinholes();
        sd_slot();
        board_screw_holes();
    }
    standoffs();
    connection_lip();
}

// ============================================================
// OBERSCHALE
// ============================================================
module oberschale() {
    difference() {
        rounded_shell(ox0, oy0, ox1, oy1, split_z, oz1);
        // Innenraum — nimmt die Steckzunge der Unterschale auf
        translate([ix0, iy0, split_z])
            cube([ix1-ix0, iy1-iy0, iz1 - split_z + 0.1]);
        rs485_hole();
        mount_holes();
    }
}

// ============================================================
// ASSEMBLY-BOARDS (importiertes STL)
// ============================================================
module boards() {
    color("olive", 0.8)
        import("SolarLoaderAssembly.stl", convexity=10);
}

// ============================================================
// HAUPTSZENE
// ============================================================
if (show_boards)
    boards();

if (show_lower)
    color("lightgray", 0.6)
        unterschale();

if (show_upper)
    color("silver", 0.6)
        translate([0, 0, explode])
            oberschale();
