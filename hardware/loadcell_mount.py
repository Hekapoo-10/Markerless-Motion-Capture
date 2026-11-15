"""
Dudukan load cell batang 10 kg (konfigurasi "Z") untuk eksperimen cover baterai.
Semua ukuran dalam mm. Ubah bagian PARAMETER lalu jalankan ulang untuk membuat STL baru.

Koordinat: X = sepanjang load cell, Y = lebar, Z = atas.
Ujung KIRI load cell (x negatif) dikunci ke PELAT BAWAH.
Ujung KANAN load cell (x positif) dikunci ke PELAT ATAS.
"""
import math
import sys
import numpy as np
import trimesh
from manifold3d import Manifold

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"

# ===================== PARAMETER (UKUR DARI LOAD CELL ANDA) =====================
LC_L = 80.0        # panjang batang load cell
LC_W = 12.7        # lebar (sisi horizontal)
LC_H = 12.7        # tinggi (arah tekanan)
HOLE_E1 = 5.0      # jarak ujung batang -> pusat lubang pertama   [ASUMSI, UKUR]
HOLE_S = 15.0      # jarak pusat lubang pertama -> lubang kedua    [ASUMSI, UKUR]
THREAD_LEFT = 5    # ukuran ulir lubang di ujung yang ke PELAT BAWAH (M5 atau M4)
THREAD_RIGHT = 4   # ukuran ulir lubang di ujung yang ke PELAT ATAS

# ===================== PARAMETER DESAIN =====================
FIT = 0.2          # kelonggaran per sisi untuk kantong load cell (FDM)
GAP = 4.0          # celah antara badan load cell dan pelat (di bagian tengah)
POCKET_D = 1.0     # kedalaman kantong pengunci posisi load cell
BOSS_EXTRA_Y = 3.0 # dinding samping boss di kiri-kanan load cell
END_WALL = 1.8     # dinding penahan di ujung luar (mengunci posisi X)
MOUNT_ZONE = 27.0  # panjang area jepit dari ujung batang (harus > E1 + S + ~4)
RELIEF = 3.0       # kantong lega tambahan (untuk mur, bila lubang tidak berulir)
CABLE_NOTCH = 5.0  # celah di dinding ujung, kalau kabel load cell keluar dari ujung batang

BASE_T = 6.0       # tebal pelat bawah
BASE_X, BASE_Y = 160.0, 110.0
TOP_T = 8.0        # tebal pelat atas
TOP_X, TOP_Y = 120.0, 90.0

# lubang baut: clearance & counterbore (cukup untuk baut kepala silinder ATAU kepala bulat)
CLEAR = {4: 4.6, 5: 5.6}
CB_D = {4: 10.8, 5: 12.0}   # kepala M4 yang dibeli diukur ~10 mm (penggaris) -> +0.8 mm longgar
CB_DEPTH = {4: 4.5, 5: 5.5}

# pola dudukan jig di pelat atas: 4 lubang M4 + kantong mur di bawah
JIG_HOLES = [(-30, -25), (-30, 25), (30, -25), (30, 25)]
M4_NUT_AF = 7.0 + 0.4
M4_NUT_H = 3.2 + 0.3

FEET_D, FEET_DEPTH, FEET_INSET = 10.5, 1.0, 12.0
SEG = 64
EPS = 0.01

# ===================== HELPER =====================
def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def cyl(x, y, z0, z1, d, seg=SEG):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, seg).translate([x, y, z0])

def hexprism(x, y, z0, z1, af):
    r = af / math.sqrt(3)  # jari-jari luar heksagon dari ukuran kunci (across flats)
    return Manifold.cylinder(z1 - z0, r, r, 6).rotate([0, 0, 30]).translate([x, y, z0])

half_w = LC_W / 2
x_left_end, x_right_end = -LC_L / 2, LC_L / 2
holes_left = [x_left_end + HOLE_E1, x_left_end + HOLE_E1 + HOLE_S]
holes_right = [x_right_end - HOLE_E1, x_right_end - HOLE_E1 - HOLE_S]
boss_y = half_w + BOSS_EXTRA_Y

# Tinggi (Z) susunan
Z_BASE_TOP = BASE_T
BOSS_H = GAP + POCKET_D
Z_LC_BOT = Z_BASE_TOP + BOSS_H - POCKET_D
Z_LC_TOP = Z_LC_BOT + LC_H
Z_TOP_UNDER = Z_LC_TOP + GAP
Z_TOP_TOP = Z_TOP_UNDER + TOP_T

# ===================== PELAT BAWAH =====================
def bottom_plate():
    p = box(-BASE_X / 2, BASE_X / 2, -BASE_Y / 2, BASE_Y / 2, 0, BASE_T)
    bx0 = x_left_end - END_WALL - FIT
    bx1 = x_left_end + MOUNT_ZONE
    p = p + box(bx0, bx1, -boss_y, boss_y, BASE_T - EPS, BASE_T + BOSS_H)
    # kantong pengunci posisi (terbuka ke arah tengah)
    p = p - box(x_left_end - FIT, bx1 + 1, -half_w - FIT, half_w + FIT,
                BASE_T + BOSS_H - POCKET_D, BASE_T + BOSS_H + 1)
    p = p - box(bx0 - 1, x_left_end, -CABLE_NOTCH / 2, CABLE_NOTCH / 2,
                BASE_T + BOSS_H - POCKET_D, BASE_T + BOSS_H + 1)
    # lubang baut dari bawah + counterbore
    for hx in holes_left:
        p = p - cyl(hx, 0, -1, BASE_T + BOSS_H + 1, CLEAR[THREAD_LEFT])
        p = p - cyl(hx, 0, -1, CB_DEPTH[THREAD_LEFT], CB_D[THREAD_LEFT])
    # kantong lega di bawah ujung kanan (ruang untuk mur/ujung baut)
    p = p - box(x_right_end - MOUNT_ZONE - 1, x_right_end + 2, -boss_y, boss_y,
                BASE_T - RELIEF, BASE_T + 1)
    # kantong kaki karet di bawah
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p - cyl(sx * (BASE_X / 2 - FEET_INSET), sy * (BASE_Y / 2 - FEET_INSET),
                        -1, FEET_DEPTH, FEET_D)
    return p

# ===================== PELAT ATAS (posisi terpasang) =====================
def top_plate():
    p = box(-TOP_X / 2, TOP_X / 2, -TOP_Y / 2, TOP_Y / 2, Z_TOP_UNDER, Z_TOP_TOP)
    bx0 = x_right_end - MOUNT_ZONE
    bx1 = x_right_end + END_WALL + FIT
    zb0 = Z_TOP_UNDER - BOSS_H
    p = p + box(bx0, bx1, -boss_y, boss_y, zb0, Z_TOP_UNDER + EPS)
    p = p - box(bx0 - 1, x_right_end + FIT, -half_w - FIT, half_w + FIT,
                zb0 - 1, zb0 + POCKET_D)
    p = p - box(x_right_end, bx1 + 1, -CABLE_NOTCH / 2, CABLE_NOTCH / 2,
                zb0 - 1, zb0 + POCKET_D)
    for hx in holes_right:
        p = p - cyl(hx, 0, zb0 - 1, Z_TOP_TOP + 1, CLEAR[THREAD_RIGHT])
        p = p - cyl(hx, 0, Z_TOP_TOP - CB_DEPTH[THREAD_RIGHT], Z_TOP_TOP + 1, CB_D[THREAD_RIGHT])
    # kantong lega di atas ujung kiri
    p = p - box(x_left_end - 2, x_left_end + MOUNT_ZONE + 1, -boss_y, boss_y,
                Z_TOP_UNDER - 1, Z_TOP_UNDER + RELIEF)
    # pola dudukan jig: lubang M4 + kantong mur heksagon di bawah
    for jx, jy in JIG_HOLES:
        p = p - cyl(jx, jy, Z_TOP_UNDER - 1, Z_TOP_TOP + 1, CLEAR[4])
        p = p - hexprism(jx, jy, Z_TOP_UNDER - 1, Z_TOP_UNDER + M4_NUT_H, M4_NUT_AF)
    # tanda silang di tengah permukaan atas (posisi jig/cover)
    p = p - box(-15, 15, -0.4, 0.4, Z_TOP_TOP - 0.6, Z_TOP_TOP + 1)
    p = p - box(-0.4, 0.4, -15, 15, Z_TOP_TOP - 0.6, Z_TOP_TOP + 1)
    return p

# ===================== POTONGAN UJI (cetak duluan, ~10-15 menit) =====================
def coupon(thread, side):
    """Salinan kecil boss + kantong + lubang untuk satu ujung load cell."""
    t = 4.0
    L = MOUNT_ZONE + END_WALL + FIT
    p = box(0, L, -boss_y, boss_y, 0, t + BOSS_H)
    # posisi ujung batang di x = END_WALL + FIT
    xe = END_WALL + FIT
    p = p - box(xe - FIT, L + 1, -half_w - FIT, half_w + FIT, t + BOSS_H - POCKET_D, t + BOSS_H + 1)
    p = p - box(-1, xe, -CABLE_NOTCH / 2, CABLE_NOTCH / 2, t + BOSS_H - POCKET_D, t + BOSS_H + 1)
    # tebal plastik di bawah load cell dibuat sama dengan pelat aslinya,
    # supaya panjang baut dan kepala baut ikut teruji
    floor = t + BOSS_H - POCKET_D
    real = (Z_LC_BOT - CB_DEPTH[thread]) if side == "L" else (Z_TOP_TOP - CB_DEPTH[thread] - Z_LC_TOP)
    cb_depth = floor - real
    for d in (HOLE_E1, HOLE_E1 + HOLE_S):
        p = p - cyl(xe + d, 0, -1, t + BOSS_H + 1, CLEAR[thread])
        p = p - cyl(xe + d, 0, -1, cb_depth, CB_D[thread])
    # takik penanda ukuran ulir: 1 takik = M4, 2 takik = M5
    for i in range(1 if thread == 4 else 2):
        p = p - box(L - 3 - i * 3, L - 2 - i * 3, boss_y - 1, boss_y + 1, -1, t + BOSS_H + 1)
    return p

def lc_dummy():
    d = box(x_left_end, x_right_end, -half_w, half_w, Z_LC_BOT, Z_LC_TOP)
    for hx in holes_left + holes_right:
        d = d - cyl(hx, 0, Z_LC_BOT - 1, Z_LC_TOP + 1, 4.0)
    return d

# ===================== EKSPOR =====================
def to_trimesh(m):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(vertices=v, faces=f, process=True)

def export(m, name, flip=False):
    if flip:  # cetak terbalik: permukaan atas menempel ke bed
        m = m.mirror([0, 0, 1])
    bb = m.bounding_box()
    m = m.translate([0, 0, -bb[2]])
    tm = to_trimesh(m)
    assert tm.is_watertight, name + " tidak watertight"
    path = f"{OUT}/{name}.stl"
    tm.export(path)
    return tm

if __name__ == "__main__":
    bp, tp, lc = bottom_plate(), top_plate(), lc_dummy()
    # cek tabrakan antar bagian (volume irisan harus 0)
    for a, b, n in [(bp, tp, "bawah-atas"), (bp, lc, "bawah-loadcell"), (tp, lc, "atas-loadcell")]:
        inter = (a ^ b).volume()
        print(f"irisan {n}: {inter:.4f} mm3")
    t1 = export(bp, "1_pelat_bawah")
    t2 = export(tp, "2_pelat_atas", flip=True)
    c = coupon(THREAD_LEFT, "L") + coupon(THREAD_RIGHT, "R").translate([0, 2 * boss_y + 6, 0])
    t3 = export(c, "0_potongan_uji")
    for n, t in [("pelat bawah", t1), ("pelat atas", t2), ("potongan uji", t3)]:
        ext = t.bounds[1] - t.bounds[0]
        print(f"{n}: {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm, volume {t.volume/1000:.1f} cm3")
    print("Z: base_top", Z_BASE_TOP, "lc_bot", Z_LC_BOT, "lc_top", Z_LC_TOP,
          "top_under", Z_TOP_UNDER, "top_top", Z_TOP_TOP)
    # simpan mesh terpasang untuk pratinjau
    for m, n in [(bp, "asm_bottom"), (tp, "asm_top"), (lc, "asm_lc")]:
        to_trimesh(m).export(f"{OUT}/{n}.stl")
