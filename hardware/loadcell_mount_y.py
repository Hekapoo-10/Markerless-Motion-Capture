"""
Versi Y: alas berbentuk Y (3 titik tumpu) + tatakan bulat.
Memakai parameter & fitur presisi yang sama dengan loadcell_mount.py.
"""
import sys
from manifold3d import Manifold
import loadcell_mount as L

OUT = sys.argv[1]

# ---- parameter bentuk Y ----
STEM_W = 24.0                 # lebar batang Y (cukup untuk counterbore Ø12)
STEM_X0 = -62.0               # ujung batang (lebih jauh dari tepi tatakan supaya tidak terjungkit)
JUNCTION_X = -12.0            # titik percabangan
ARM_W = 14.0                  # lebar lengan
ARM_TIP = (58.0, 50.0)        # ujung lengan (x, ±y)
DISK_D = 110.0                # diameter tatakan bulat
SEG = 96

def stadium(p0, p1, w, z0, z1):
    a = Manifold.cylinder(z1 - z0, w / 2, w / 2, SEG).translate([p0[0], p0[1], z0])
    b = Manifold.cylinder(z1 - z0, w / 2, w / 2, SEG).translate([p1[0], p1[1], z0])
    return Manifold.batch_hull([a, b])

def y_base():
    t = L.BASE_T
    stem = stadium((STEM_X0 + STEM_W / 2, 0), (JUNCTION_X, 0), STEM_W, 0, t)
    arm1 = stadium((JUNCTION_X, 0), ARM_TIP, ARM_W, 0, t)
    arm2 = stadium((JUNCTION_X, 0), (ARM_TIP[0], -ARM_TIP[1]), ARM_W, 0, t)
    p = stem + arm1 + arm2
    # boss + kantong + celah kabel + counterbore: sama dengan pelat bawah
    bx0 = L.x_left_end - L.END_WALL - L.FIT
    bx1 = L.x_left_end + L.MOUNT_ZONE
    p = p + L.box(bx0, bx1, -L.boss_y, L.boss_y, t - L.EPS, t + L.BOSS_H)
    p = p - L.box(L.x_left_end - L.FIT, bx1 + 1, -L.half_w - L.FIT, L.half_w + L.FIT,
                  t + L.BOSS_H - L.POCKET_D, t + L.BOSS_H + 1)
    p = p - L.box(bx0 - 1, L.x_left_end, -L.CABLE_NOTCH / 2, L.CABLE_NOTCH / 2,
                  t + L.BOSS_H - L.POCKET_D, t + L.BOSS_H + 1)
    for hx in L.holes_left:
        p = p - L.cyl(hx, 0, -1, t + L.BOSS_H + 1, L.CLEAR[L.THREAD_LEFT])
        p = p - L.cyl(hx, 0, -1, L.CB_DEPTH[L.THREAD_LEFT], L.CB_D[L.THREAD_LEFT])
    # 3 cekungan kaki karet (tumpuan 3 titik: tidak pernah goyang di meja yang tidak rata)
    for fx, fy in [(STEM_X0 + 8, 0), (ARM_TIP[0], ARM_TIP[1]), (ARM_TIP[0], -ARM_TIP[1])]:
        p = p - L.cyl(fx, fy, -1, L.FEET_DEPTH, L.FEET_D)
    # 2 slot cable tie di batang, untuk mengunci kabel load cell ke alas
    for sx in (-50.0,):
        for sy in (-8.0, 8.0):
            p = p - L.box(sx - 1.5, sx + 1.5, sy - 2.0, sy + 2.0, -1, t + 1)
    return p

def disk_top():
    zu, zt = L.Z_TOP_UNDER, L.Z_TOP_TOP
    p = Manifold.cylinder(L.TOP_T, DISK_D / 2, DISK_D / 2, 160).translate([0, 0, zu])
    bx0 = L.x_right_end - L.MOUNT_ZONE
    bx1 = L.x_right_end + L.END_WALL + L.FIT
    zb0 = zu - L.BOSS_H
    p = p + L.box(bx0, bx1, -L.boss_y, L.boss_y, zb0, zu + L.EPS)
    p = p - L.box(bx0 - 1, L.x_right_end + L.FIT, -L.half_w - L.FIT, L.half_w + L.FIT, zb0 - 1, zb0 + L.POCKET_D)
    p = p - L.box(L.x_right_end, bx1 + 1, -L.CABLE_NOTCH / 2, L.CABLE_NOTCH / 2, zb0 - 1, zb0 + L.POCKET_D)
    for hx in L.holes_right:
        p = p - L.cyl(hx, 0, zb0 - 1, zt + 1, L.CLEAR[L.THREAD_RIGHT])
        p = p - L.cyl(hx, 0, zt - L.CB_DEPTH[L.THREAD_RIGHT], zt + 1, L.CB_D[L.THREAD_RIGHT])
    p = p - L.box(L.x_left_end - 2, L.x_left_end + L.MOUNT_ZONE + 1, -L.boss_y, L.boss_y,
                  zu - 1, zu + L.RELIEF)
    for jx, jy in L.JIG_HOLES:
        p = p - L.cyl(jx, jy, zu - 1, zt + 1, L.CLEAR[4])
        p = p - L.hexprism(jx, jy, zu - 1, zu + L.M4_NUT_H, L.M4_NUT_AF)
    p = p - L.box(-15, 15, -0.4, 0.4, zt - 0.6, zt + 1)
    p = p - L.box(-0.4, 0.4, -15, 15, zt - 0.6, zt + 1)
    return p

if __name__ == "__main__":
    b, t, lc = y_base(), disk_top(), L.lc_dummy()
    for a, c, n in [(b, t, "alas-tatakan"), (b, lc, "alas-loadcell"), (t, lc, "tatakan-loadcell")]:
        print(f"irisan {n}: {(a ^ c).volume():.4f} mm3")
    # celah minimum lengan Y ke bawah load cell (di luar area jepit)
    tb = L.export(b, "y1_alas_Y")
    tt = L.export(t, "y2_tatakan_bulat", flip=True)
    for n, tm in [("alas Y", tb), ("tatakan bulat", tt)]:
        e = tm.bounds[1] - tm.bounds[0]
        print(f"{n}: {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm, volume {tm.volume/1000:.1f} cm3")
    for m, n in [(b, "y_asm_bottom"), (t, "y_asm_top")]:
        L.to_trimesh(m).export(f"{OUT}/{n}.stl")
