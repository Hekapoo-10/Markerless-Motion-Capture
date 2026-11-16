# STAGES: Tahap Kerja, Kode, dan Tes

Versi 14 Nov 2026 (revisi malam: load cell di perangkat terpisah, gaya diketik satu angka per gerakan di formulir pendataan Tahap 5, gerakan generik `move_1`, `move_2`, …; FmaxM ditetapkan). Aturan: **satu tahap, satu tes**. Tahap berikutnya baru dimulai setelah tes tahap ini lulus, dicatat di `docs/progress-log.md`, dan di-commit dengan tag `stage-XX-pass`.

Kode di dokumen ini adalah **kerangka awal**. Claude Code boleh meringkas (ponytail), tapi tidak boleh mengubah aturan atau kriteria lulus tanpa izin. Bagian bertanda **(cek)** belum diuji di perangkat kita.

Setiap tahap memakai format yang sama: **Tujuan · Siapkan · Langkah · Kode inti · Tes (lulus jika) · Catat**.

### Uji dini vs uji final (keputusan pengguna 15 Nov)

**Uji dini** = dikerjakan sekarang dengan setup apa adanya, hasilnya dicatat sebagai info, cukup untuk lanjut. **Uji final** = kriteria "Lulus jika" di tiap tahap, dikerjakan setelah setup fisik dibekukan, berurutan dari Tahap 1.

**Setup dibekukan** bila: rig 3D print terpasang dan kamera terkunci; kabel dirapikan dan diikat; setiap kabel, port hub, dan port PC berlabel; hub terpasang tetap ke port PC; lampu final. Setelah itu: jalankan ulang `tools/identify_cameras.py` + `check` (port bisa berubah saat kabel dirapikan), lalu mulai uji final.

| Tahap | Uji dini (sekarang) | Uji final (setelah setup beku) |
|---|---|---|
| 0 | Semua (sudah lulus) | — |
| 1 | Label + tes + uji tutup lensa | Ulang setelah reboot dan cabut-colok |
| 2 | fps, jeda, format, urutan setting | Nilai exposure (tergantung lampu final), cek tajam |
| 3 | 6 kamera 5 menit, DSHOW vs MSMF (peringatan dini bandwidth hub) | Ulang dengan kabel final |
| 4 | Semua (perangkat terpisah) | — |
| 5 | Tes formulir; rekaman 5 menit | Ulang dengan exposure final |
| 6 | — (butuh pose 2D Tahap 8) | Semua kriteria, sesudah Tahap 8 |
| 7–10 | Kode saja (dengan rekaman uji) | **Dimulai setelah setup beku**; semua kriteria |
| 11 | Semua (software) | — |
| 12–13 | Kode + data buatan | Uji jawaban-diketahui dengan rekaman nyata |
| 14 | — | Semua |

---

## Tahap 0: Lingkungan, repo, dan deklarasi PC

**Tujuan:** semua alat terpasang dengan versi terkunci, dan spesifikasi PC tercatat sebelum kode lain ditulis.

**Siapkan:** Windows dengan akses admin, Git, VS Code, Claude Code desktop, Anaconda, driver NVIDIA terbaru (kalau ada GPU NVIDIA), Arduino IDE hanya untuk perangkat load cell terpisah. FFmpeg terpisah tidak wajib (cadangan Tahap 5). File lama dari Project (`hardware/*.ino`, `hardware/loadcell_mount*.py`) disalin ke folder `hardware/` di repo sebagai arsip perangkat load cell terpisah.

**Langkah:**
1. Buat repo di folder proyek: `git init -b main`. File yang dibuat: `.gitignore` (`data/` dan file video tidak masuk Git), `requirements.txt`, `.pre-commit-config.yaml` (hook ruff lokal dari env, tanpa unduhan).
2. Buat env conda dan pasang paket (lihat `CLAUDE.md` §5). Pilih onnxruntime sesuai versi CUDA di header `nvidia-smi` (driver baru menulis `CUDA UMD Version`).
3. Jalankan `python tools/env_report.py`, lalu periksa `configs/environment.yaml` bersama pengguna.
4. Di Claude Code (dua prompt terpisah): `/plugin marketplace add DietrichGebert/ponytail` lalu `/plugin install ponytail@ponytail`. Ponytail hanya berupa prompt (SKILL.md), tidak butuh Node/Python. Pakai `/ponytail full` saat menulis kode dan `/ponytail-review` sebelum commit tiap tahap. Jangan memakai salinan ponytail yang berisi `.exe`/`.dll`.
5. `pre-commit install`. Repo GitHub: https://github.com/Hekapoo-10/Markerless-Motion-Capture (**public**, keputusan pengguna 15 Nov; rencana awal private). Login lewat Git Credential Manager (browser).

**Kode inti:** `tools/env_report.py` (CPU, RAM, disk per drive, GPU, versi CUDA driver, USB host controller, kamera → `configs/environment.yaml`).

**Tes:** `tests/test_stage00_env.py`: hanya satu paket OpenCV; `cv2.aruco.CharucoDetector` ada; onnxruntime benar-benar menjalankan model contoh (`sigmoid.onnx`) di `CUDAExecutionProvider` (daftar provider saja tidak cukup, karena sesi bisa diam-diam jatuh ke CPU); `aniposelib` dan `rtmlib` bisa di-import. Set `KIMCAM_CPU=1` untuk melewati tes CUDA di PC tanpa GPU NVIDIA.

**Lulus jika:** keempat tes lulus dan `environment.yaml` terisi. GPU, driver CUDA, jumlah USB host controller, dan ruang disk sudah dibaca bersama pengguna.

**Catat:** isi `environment.yaml` dan keputusan versi onnxruntime (1.30.x atau 1.26.0).

---

## Tahap 1: Inventaris dan label kamera

**Tujuan:** setiap kamera fisik (`front_left`, `front`, `front_right`, `top`, `wing_left`, `wing_right`; kiri/kanan = sisi peserta) selalu dikenali dengan benar, walaupun Windows memberi nama yang sama ("USB Camera").

**Temuan 14 Nov:** keenam kamera berseri sama (`SN0001`). Windows memberi ID berbasis seri ke satu kamera saja, sedangkan sisanya diberi ID berbasis port, dan kamera "pemilik" seri bisa berganti setelah reboot. Urutan index DSHOW dan MSMF juga berbeda. **Keputusan pengguna:** seri tidak diganti; kamera dikenali dari **alamat fisik port USB** (`DEVPKEY_Device_LocationPaths` perangkat induk, misalnya `PCIROOT(0)#PCI(0801)#PCI(0003)#USBROOT(0)#USB(1)#USB(2)`). **[Bersumber: dibaca dari Windows]**

**Siapkan:** stiker label untuk badan kamera, kedua ujung kabel, dan port hub; foto susunan kamera dan hub.

**Langkah:**
1. Tempel label fisik. Foto setiap kamera dan foto posisi seluruh setup (termasuk hub dan colokannya).
2. `python tools/support/list_cameras.py`: semua kamera per backend (index, nama, VID/PID, path).
3. `python tools/identify_cameras.py`: jendela menampilkan satu kamera; tekan 1–6 sesuai posisinya → `usb_port` di `configs/cameras.yaml` terisi.
4. `python tools/identify_cameras.py check`: uji tutup lensa per label (tekan `y` bila gambar gelap).
5. Reboot → `pytest tests/test_stage01_cameras.py` + `check`. Cabut semua kabel, colok lagi ke port yang sama → ulangi.

**Kode inti:** `src/kimcam/cameras.py` (`camera_ports()` memetakan port → index OpenCV untuk backend yang dipakai; `open_camera(label)` mencari ulang index tiap kali dibuka), `tools/identify_cameras.py`, `configs/cameras.yaml` (`backend` diputuskan di Tahap 3, `exposure` di Tahap 2).

**Tes:** `tests/test_stage01_cameras.py`: label di `cameras.yaml` tepat enam dan port-nya unik; untuk DSHOW dan MSMF, setiap label menemukan kamera dan semua index berbeda. Uji tutup lensa dikerjakan manual.

**Lulus jika:** tes lulus dan uji tutup lensa benar untuk keenam label, setelah (a) reboot dan (b) semua kabel dicabut lalu dicolok ke port yang sama.

**Catat:** foto setup, isi `cameras.yaml`, hasil reboot dan cabut-colok.

---

## Tahap 2: Tes satu kamera (format, exposure, timestamp)

**Tujuan:** memastikan satu kamera memberi 1280×800 MJPG 30 fps stabil dengan exposure manual.

**Temuan 15 Nov (uji dini, kamera `top`, DSHOW):** **[Bersumber: diukur]**
- Urutan setting: **FOURCC harus terakhir.** Bila FOURCC di-set sebelum ukuran, DSHOW kembali ke YUY2.
- **`grab()` DSHOW tidak menunggu frame baru** (±2,8 juta panggilan/detik); `read()` menunggu. Timestamp diambil **setelah `read()`** (jeda decode kira-kira tetap per kamera; diukur di Tahap 6 dari gerakan tangan).
- Exposure DSHOW: `AUTO_EXPOSURE 0.25` + `EXPOSURE` bekerja (−7 terbaca −7; −6 lebih terang, −8 lebih gelap). Kamera **mengingat** exposure terakhir sampai dicabut, jadi `exposure: null` tidak sama dengan auto → untuk rekaman nilai exposure **wajib** diisi.
- MSMF (5 detik): 29,2–29,4 frame baru/detik (ada frame dobel), jeda sampai 80 ms, dan exposure −8 terbaca −6. DSHOW: 30,2 fps tanpa dobel. Pilihan final di Tahap 3.

**Langkah:**
1. `python tools/support/test_one_camera.py top 60` (auto) dan `python tools/support/test_one_camera.py top 60 -7` (manual).
2. Uji final (setelah lampu final): pilih exposure sependek mungkin yang masih terang (tanpa blur saat menekan), isi `exposure` di `cameras.yaml`, ulangi langkah 1 dengan tangan menekan di bawah kamera.

**Kode inti:** `tools/support/test_one_camera.py` (label, detik, exposure opsional → fps, jeda maks, jeda > 67 ms, frame dobel, format/exposure terbaca, contoh `data/interim/stage02_<label>.png`).

**Lulus jika:** fps rata-rata ≥ 29,5; tidak ada jeda > 67 ms (2 periode frame); tidak ada frame dobel; format dan exposure yang dibaca balik sama dengan yang di-set; gambar tajam saat tangan menekan (cek visual 1 frame).

**Catat:** urutan setting yang berhasil, nilai exposure → `cameras.yaml`.

---

## Tahap 3: Tes enam kamera bersamaan (DSHOW vs MSMF)

**Tujuan:** keenam kamera jalan bersamaan tanpa frame hilang, dan backend dipilih berdasarkan data.

**Langkah:**
1. Satu thread per kamera, masing-masing menjalankan loop `read()` Tahap 2 selama 5 menit.
2. Jalankan dengan `backend: dshow`, lalu `backend: msmf`.
3. Bila ada kamera gagal: pindahkan ke USB host controller lain (maksimal 2–3 kamera per controller). Bila controller kurang, gunakan kartu PCIe USB dengan controller terpisah per port.

**Kode inti:** `tools/support/test_six_cameras.py`
```python
import threading, time
import numpy as np
from kimcam.cameras import load_cfg, open_camera

cfg, DUR, ts = load_cfg(), 300, {}

def worker(label):
    cap, t_end, out = open_camera(label, cfg), time.perf_counter() + DUR, []
    while time.perf_counter() < t_end:
        if cap.read()[0]:                # bukan grab(): di DSHOW grab() tidak menunggu frame baru
            out.append(time.perf_counter_ns())
    ts[label] = out

threads = [threading.Thread(target=worker, args=(c,)) for c in cfg["cameras"]]
for t in threads: t.start()
for t in threads: t.join()
for label, t in sorted(ts.items()):
    g = np.diff(t) / 1e6
    print(f"{label}: fps={1000 / g.mean():.2f} jeda_maks={g.max():.1f} ms jeda>67ms={int((g > 67).sum())}")
```

**Lulus jika:** keenam kamera memenuhi kriteria Tahap 2 selama 5 menit dengan satu backend yang sama, **kecuali frame dobel**: boleh ≤ 0,1% frame per kamera (`dup_max_fraction` di `cameras.yaml`) dan tidak boleh berturut-turut (2 dobel berurutan = kamera mulai beku). Jeda > 67 ms tetap 0.

**Keputusan 16 Nov (pengguna; berlawanan dengan saran Claude untuk juga memindah hub C):** uji final menunjukkan front_left (hub C) memberi frame dobel identik penuh yang langka (5 lalu 1 per 5 menit, 0 saat sendirian). Hub C berbagi controller chipset dengan keyboard/mouse, LED RGB, dan Bluetooth (Asumsi penyebab). Dobel langka **ditoleransi**: ditandai `dup=1` di `<label>_ts.csv` dan dibuang per kamera saat analisis (Tahap 8). Bila muncul jeda > 67 ms atau kamera beku lagi, pemindahan hub C dibahas ulang.

**Temuan 16 Nov (malam):** sesudahnya kamera hub C gagal dibuka / hilang sesaat. Penyebab: **satu controller USB hanya muat 2 kamera ini** (kamera ke-3 di satu controller selalu gagal dibuka), dan di controller chipset sisa jatah dipakai perangkat lain. Hub C dipindah ke controller AMD USB 2.0 `PCI(0803)` yang kosong → 6 kamera 5 menit tanpa dobel dan tanpa jeda. Aturan: 3 controller CPU × 2 kamera; controller chipset tidak dipakai untuk kamera. **[Bersumber: diukur]**

**Catat:** hasil DSHOW vs MSMF, backend terpilih, peta kamera → controller.

---

## Tahap 4: Load cell di perangkat terpisah (akurasi gaya)

**Tujuan:** memastikan angka gaya yang nanti diketik ke formulir pendataan (Tahap 5) akurat, dan menetapkan cara mendapat **satu angka per gerakan**.

**Keputusan 14 Nov (revisi malam, dari pengguna):** load cell dibuat di **perangkat terpisah** dan tidak tersambung ke PC kamera. Untuk setiap peserta, gaya setiap gerakan diukur di perangkat itu **sebelum rekaman**, lalu dicatat sebagai **satu angka (N) per gerakan** dan diketik di formulir pendataan. Tidak ada ukur ulang sesudah rekaman, tidak ada sinkron, dan tidak ada kode load cell di repo ini. Dasarnya: KIM memakai gaya khas/rata-rata per sub-aktivitas (formulir hlm. 4). **[Bersumber (dasar) / Disetujui pengguna (cara)]**

Konsekuensi yang diterima: perubahan gaya selama 15 menit (lelah/belajar) tidak terdeteksi, dan P4 tidak bisa mengacak sebaran gaya per orang.

**Kondisi sekarang (progress-log 7 Nov):** kabel sudah jalan (DT → D3, SCK → D2, VCC → 5V, GND → GND; load cell merah/hitam/putih/hijau → E+/E−/A−/A+), bacaan OK tetapi **±10 sampel/detik** (RATE masih 10 SPS). Sketsa lama `hardware/tes_realtime.ino` dan `hardware/tes2_gaya_newton.ino` menjadi titik awal perangkat ini.

**Langkah:**
1. Bersama pengguna, tentukan bentuk perangkat (misalnya Nano + HX711 + layar, atau Nano ke laptop lain). **Jangan menebak; minta foto.**
2. Bila puncak gerakan singkat (misalnya snap-fit), naikkan HX711 ke 80 SPS: cari jalur pin RATE (pin 15) di foto papan **sebelum** memotong apa pun. Di 10 SPS puncak bisa tercatat terlalu kecil (Asumsi).
3. Kalibrasi dengan beban acuan yang sudah ditimbang (misalnya 0,5 kg, 1 kg, 2 kg).
4. Tetapkan cara mendapat satu angka per gerakan. Usulan: peserta melakukan gerakan itu 5 kali di alat, lalu dipakai **nilai tengah puncaknya**.

**Lulus jika:** galat ≤ 0,3 N pada semua beban acuan; cara mendapat satu angka per gerakan tertulis di `progress-log.md`.

**Catat:** foto perangkat, faktor kalibrasi, cara menghitung angka gaya, gaya tiap gerakan dari 10 kali percobaan peneliti sendiri (cover, dan gear bila dipakai).

---

## Tahap 5: Pendataan peserta + program rekam 6 kamera

**Tujuan:** satu program yang (1) mencatat data peserta dan gaya tiap gerakan, lalu (2) merekam 6 kamera dengan jam PC yang sama, dari satu tombol mulai/berhenti.

**Langkah:**
1. `configs/session.yaml`: `scenario_hours` (belum diputuskan) dan `moves: [move_1, move_2, move_3, move_4]` (nama sementara; setelah rapat dosen cukup ganti baris ini).
2. `python tools/record_session.py --participant P001 --session S01 [--minutes 15] [--exposure -7]`. Program menolak bila exposure belum diisi, folder sesi sudah ada, atau disk data < 40 GB. Lalu formulir di terminal: nama, gender, tangan dominan, pengalaman, **gaya (N) tiap gerakan**; input salah ditanya ulang; ringkasan harus dikonfirmasi `y`.
3. Nama **hanya** ditulis ke `data/participants_private.csv` (id, name). ID yang sudah ada boleh dipakai lagi **bila namanya sama** (sesi berikutnya orang yang sama); nama berbeda ditolak.
4. Rekam: satu thread per kamera, `read()` → timestamp (bukan `grab()`, lihat Tahap 2) → abu-abu → `VideoWriter` MJPG 1 kanal (diterima di Windows, dicek 15 Nov) + `<label>_ts.csv` (frame, t_ns, dup). Berhenti saat durasi habis atau Enter. Status tiap 5 detik.
5. **Peringatan langsung** bila satu kamera memberi frame dobel (berturut-turut = kamera beku) atau jeda > 67 ms (dari data Tahap 3), supaya rekaman bisa dihentikan dan diulang.
6. Setelah berhenti: `meta.yaml` (peserta tanpa nama + gaya per gerakan, mulai, durasi, backend, format, exposure, port kamera, `calibration_id` (Tahap 7), skenario jam, daftar gerakan, commit Git, statistik per kamera), lalu SHA-256 setiap file ke `data/manifest.csv`.
7. Bila CPU > 80% atau frame hilang: ganti penulis video ke FFmpeg tanpa encode ulang (cadangan; CPU Tahap 3 hanya 3–5%).

Data: `data/` di repo adalah junction ke `D:\kimcam-data` (keputusan pengguna 15 Nov; C: tidak cukup).

**Kode inti:** `src/kimcam/intake.py` (formulir), `tools/record_session.py` (rekam), `configs/session.yaml`. Rekaman uji tanpa peserta: `--skip-intake` (folder `data/raw/TEST/`).

**Tes:** `tests/test_stage05_intake.py` (input diganti `monkeypatch`): kosong/huruf/negatif/`nan` ditanya ulang; `30,5` dibaca 30.5; nama tidak ada di hasil `intake()`; nama ada di file privat; ID sama + nama sama diterima tanpa baris baru; ID sama + nama lain ditolak; jawaban `n` tidak menyimpan apa pun.

**Lulus jika:** tes formulir lulus; rekaman 5 menit dengan: fps tiap kamera ±0,5% dari fps terukur Tahap 3 (`format.fps_measured` = 30,2); jumlah frame **di jendela waktu bersama** sama di keenam kamera ±2 (kamera tidak mulai tepat bersamaan, jadi total frame bisa beda tanpa ada yang hilang); tidak ada jeda > 67 ms; frame dobel ≤ 0,1% per kamera dan tidak berturut-turut (16 Nov, lihat Tahap 3); semua video bisa dibuka; manifest tertulis. (Kriteria lama "±0,5% dari 9.000" diganti 15 Nov atas izin pengguna; dihitung oleh `record_session.py`, baris "CEK REKAMAN".)

**Catat:** pemakaian CPU/disk, ukuran file per menit.


---

## Tahap 6: Sinkron antar kamera dari gerakan tangan (dikerjakan sesudah Tahap 8)

**Tujuan:** mengukur selisih waktu **antar kamera** (keterlambatan PC per kamera: timestamp `_ts.csv` = waktu frame tiba di PC, bukan waktu dipotret). Tetap wajib karena triangulasi 3D butuh frame dari saat yang sama. Sinkron kamera ↔ load cell **tidak** diperlukan (keputusan 14 Nov).

**Keputusan 15 Nov (pengguna):** tanpa LED/Arduino. Selisih dicari dari **gerakan tangan** yang sama di keenam kamera (cara modul sinkronisasi Pose2Sim, yang mengkorelasikan kecepatan titik tubuh antar kamera). **[Sebagian: cek dokumentasi Pose2Sim]** Karena butuh titik 2D, tahap ini dikerjakan **setelah Tahap 8** dan sebelum triangulasi Tahap 9. Tahap 7 dan 8 tidak bergantung padanya.

Selisih yang tidak bisa dihilangkan cara ini: kamera tidak memotret di saat yang sama (jalan sendiri-sendiri), paling buruk setengah frame (±16,5 ms). Frame selalu dipasangkan **berdasarkan timestamp**, bukan nomor urut, karena fps tiap kamera sedikit berbeda (30,205–30,210 → ±4–5 frame selisih dalam 15 menit; data Tahap 5).

**Langkah:**
1. Ambil titik pergelangan (dan ujung jari) dari pose 2D tiap kamera (Tahap 8), skor rendah → NaN.
2. Hitung kecepatan 2D titik itu per kamera, lalu sampel ulang ke grid waktu bersama 1 ms memakai `<label>_ts.csv`.
3. Untuk tiap kamera, cari geser waktu (±150 ms) yang membuat kurva kecepatannya paling berkorelasi dengan kamera `top` (acuan).
4. Ulangi per potongan 1 menit sepanjang rekaman untuk melihat apakah geser waktunya stabil. Simpan offset ke `configs/sync.yaml`.
5. Bila offset semua kamera < ±5 ms dan stabil: koreksi tidak dipakai (cukup dicatat).

**Lulus jika (disetujui pengguna 15 Nov):** offset tiap kamera dari potongan-potongan 1 menit berbeda SD < 5 ms (stabil); galat reproyeksi triangulasi dengan offset ≤ tanpa offset. Bila offset tidak stabil atau korelasi lemah → diskusikan cadangan: kedip senter HP sekali, atau FSIN (kabel pemicu kamera dari Arduino).

**Catat:** offset per kamera, kestabilannya, keputusan dipakai/tidak.

---

## Tahap 7: Kalibrasi kamera

**Tujuan:** posisi dan lensa keenam kamera diketahui, supaya titik 2D bisa diubah menjadi 3D.

**Siapkan:** papan ChArUco dicetak A3 di kertas tebal atau ditempel ke papan rata (misalnya 7 × 10 kotak, DICT_4X4_50). Buat gambar papan dengan `board.draw()` dari aniposelib yang sama, bukan dari situs generator lain: sejak OpenCV 4.6 susunan ChArUco untuk jumlah baris genap berubah, jadi papan dari alat lain bisa tidak terbaca (Sebagian). **Ukur sisi kotak hasil cetak dengan jangka sorong** dan pakai angka ukuran itu.

**Langkah:**
1. Rekam papan bergerak 60–90 detik. Papan harus melewati tepi gambar (penting untuk fisheye) dan terlihat oleh ≥ 2 kamera sekaligus.
2. Kalibrasi dengan aniposelib (`fisheye=True`). Ulangi 3 kali dari rekaman yang sama, lalu bandingkan.
3. Opsional: cek visual dengan caliscope.
4. Simpan ke `data/calib/<tanggal>/calibration.toml`. Ulangi kalibrasi setiap hari pengambilan data, atau bila kamera tersenggol.

**Kode inti:** `src/kimcam/calib.py`
```python
from aniposelib.boards import CharucoBoard
from aniposelib.cameras import CameraGroup

from kimcam.cameras import LABELS

def calibrate(day, square_mm, marker_mm):
    board = CharucoBoard(7, 10, square_length=square_mm, marker_length=marker_mm,
                         marker_bits=4, dict_size=50)
    videos = [[f"data/calib/{day}/{c}.avi"] for c in LABELS]
    cgroup = CameraGroup.from_names(LABELS, fisheye=True)
    error, _ = cgroup.calibrate_videos(videos, board)   # (cek) bentuk nilai kembalian
    cgroup.dump(f"data/calib/{day}/calibration.toml")
    return error, cgroup
```

**Lulus jika:** galat reproyeksi < 0,5 px; posisi tiap kamera antar-ulangan berbeda < 5 mm (`cgroup.get_translations()`); jarak yang diukur di papan (misalnya 10 kotak) sesuai ukuran nyata ±1 mm.

**Catat:** galat per ulangan, file kalibrasi, foto papan.

---

## Tahap 8: Pose 2D (RTMW)

**Tujuan:** titik tubuh dan tangan terdeteksi di setiap kamera, terutama `top`.

**Langkah:**
1. Rekam 30 detik tugas + 10 detik tangan diam di atas jig.
2. Jalankan RTMW di setiap video. Ubah frame abu-abu ke 3 kanal. Frame dengan `dup=1` di `<label>_ts.csv` diberi NaN untuk kamera itu (gambar lama; dibuang dari triangulasi Tahap 9; keputusan 16 Nov, Tahap 3).
3. Gambar titik di atas video (overlay) dan periksa bersama pengguna.
4. Cek urutan titik tangan (91–132) dari metadata rtmlib.
5. Ukur kecepatan model (frame/detik) untuk memperkirakan lama proses per orang.

Catatan (dicek di kode rtmlib 0.0.16): `mode="performance"` memakai detektor YOLOX-m dan pose `rtmw-dw-x-l` 384×288. Model diunduh otomatis dari download.openmmlab.com saat pertama dipakai, jadi butuh internet sekali. **Skor titik RTMW bukan probabilitas 0–1** (nilai maksimum SimCC mentah), sehingga ambang 0,3/0,5 di bawah hanya mengikuti kebiasaan rtmlib dan disetel ulang dari data Tahap 8 (Asumsi).

**Kode inti:** `src/kimcam/pose2d.py`
```python
import cv2, numpy as np
from rtmlib import Wholebody

def run_pose(video_path, out_path, device="cuda"):
    model = Wholebody(mode="performance", backend="onnxruntime", device=device, to_openpose=False)
    cap, kps, scs = cv2.VideoCapture(video_path), [], []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        k, s = model(frame)                    # k: (orang, 133, 2), s: (orang, 133)
        i = int(np.argmax(s.mean(axis=1))) if len(s) else None
        kps.append(k[i] if i is not None else np.full((133, 2), np.nan))
        scs.append(s[i] if i is not None else np.zeros(133))
    np.savez_compressed(out_path, kps=np.array(kps), scores=np.array(scs))
```

**Lulus jika:** saat menekan, tangan dominan terdeteksi (skor rata-rata titik tangan ≥ 0,5, ambang Asumsi) di ≥ 3 kamera termasuk `top`; saat tangan diam 10 detik, getaran titik pergelangan < 2 px SD (Asumsi).

**Catat:** kamera yang melihat tangan, kecepatan model, contoh overlay.

---

## Tahap 9: 3D, sudut sendi, dan uji goniometer

**Tujuan:** sudut pergelangan, lengan bawah, siku, dan bahu dalam derajat, beserta besar galatnya.

**Langkah:**
1. Triangulasi titik 2D (skor < 0,3 → NaN), isi celah ≤ 5 frame, filter Butterworth orde 4, 6 Hz.
2. Hitung sudut sesuai `PROJECT_OVERVIEW.md` §4.3, dikurangi offset posisi netral.
3. **Uji goniometer:** pengguna menahan pergelangan pada sudut yang diukur goniometer, masing-masing 3 detik dan 3 kali ulang:
   - fleksi/ekstensi 0, ±30, ±45, ±60°;
   - radial 10, 15, 20°; ulnar 15, 20, 25°;
   - pronasi/supinasi 0, ±45, ±60, ±70° (siku ditekuk ±90°).
4. Hitung bias, SD, batas kesesuaian Bland–Altman, dan RMSE per sudut. Cek tanda (+/−) setiap sudut **untuk tangan kanan dan kiri terpisah**: arah `a_ru` terbalik di tangan kiri, jadi tanda FE dan RUD ikut terbalik bila tidak dikoreksi. (Fungsi `signed_angle` sudah dicek dengan geometri buatan: input 0/30/45/−30° keluar 0/30/45/−30°.)

**Kode inti:** `src/kimcam/triang.py` dan `angles.py`
```python
import numpy as np
from aniposelib.cameras import CameraGroup
from scipy.signal import butter, filtfilt

def triangulate(calib_toml, p2d, scores, min_score=0.3):
    """p2d: (kamera, frame, 133, 2) piksel mentah; aniposelib meng-undistort fisheye sendiri."""
    p2d = np.where(scores[..., None] >= min_score, p2d, np.nan)
    cg = CameraGroup.load(calib_toml)
    n_cam, n_fr, n_kp, _ = p2d.shape
    return cg.triangulate(p2d.reshape(n_cam, -1, 2), progress=True).reshape(n_fr, n_kp, 3)

def lowpass(x, fs=30, fc=6):
    b, a = butter(4, fc, fs=fs)
    return filtfilt(b, a, x, axis=0)          # isi NaN pendek sebelum memanggil ini

def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)

def signed_angle(a, b, axis):
    """Sudut dari a ke b (derajat) setelah keduanya diproyeksikan ke bidang tegak lurus axis."""
    a = unit(a - (a * axis).sum(-1, keepdims=True) * axis)
    b = unit(b - (b * axis).sum(-1, keepdims=True) * axis)
    return np.degrees(np.arctan2((np.cross(a, b) * axis).sum(-1), (a * b).sum(-1)))
```

**Lulus jika:** bias, SD, batas kesesuaian, dan RMSE tercatat untuk setiap sudut; tanda setiap sudut benar. Usulan target: |bias| ≤ 5° dan RMSE ≤ 10° di sekitar batas. Sudut yang gagal diberi label "eksperimental" (terutama pronasi/supinasi), lalu didiskusikan dengan pengguna.

**Catat:** tabel galat per sudut → menjadi masukan P4 (`configs/angle_error.yaml`).

---

## Tahap 10: Segmentasi siklus dan aksi

**Tujuan:** setiap frame punya label siklus, aksi, tangan, dan **jari yang menekan**. Semua dari kamera saja (tidak ada data gaya selama tugas, keputusan 14 Nov).

**Langkah:**
1. Zona dalam koordinat 3D (`configs/zones.yaml`: nampan, jig, kotak jadi; tinggi permukaan cover di jig diukur sekali dengan penggaris).
2. Aksi dari posisi dan kecepatan tangan (3D, setelah filter). Label memakai nama di `configs/session.yaml: moves` (`move_1`, `move_2`, …). Daftar di bawah hanya contoh usulan untuk cover (move_1 = ambil … move_4 = letakkan); definisi final menunggu rapat dosen:
   - **Ambil** = tangan di zona nampan.
   - **Posisikan** = tangan di zona jig, belum menekan.
   - **Tekan** = tangan di zona jig **dan** ujung ibu jari (lokal 4) atau ujung telunjuk (lokal 8) berada ≤ d mm dari permukaan cover **dan** tangan hampir diam selama ≥ k frame. Nilai d dan k adalah Asumsi, disetel dari data pilot.
   - **Letakkan** = tangan di zona kotak jadi.
   - Siklus = dari awal "ambil" ke awal "ambil" berikutnya.
3. **Jari yang menekan** = ujung jari yang paling dekat ke cover saat tekan (ibu jari atau telunjuk). Ini menentukan FmaxM yang dipakai (80 N atau 50 N; lihat `PROJECT_OVERVIEW.md` §3.3), jadi wajib dicatat per tekan.
4. Hitung jumlah per menit tiap aksi per tangan, dan detik tahan per menit bila ada lengan statis ≥ 4 detik.
5. Anotasi manual: (a) nomor frame awal tiap aksi untuk 10% siklus; (b) jumlah tekan dan jari yang dipakai pada 3 menit acak, ditonton dari `top`.

**Lulus jika:** ≥ 90% batas aksi otomatis berada dalam ±3 frame dari anotasi manual; jumlah tekan otomatis vs manual berbeda ≤ 2% (Asumsi); label jari benar ≥ 95% (Asumsi).

**Keluaran:** `labels.parquet` dengan format label di Tahap 12 (kolom `t`, `cycle`, `hand`, `move`, `finger`, `ang_<sendi>`, `oor_<sendi>`).

**Catat:** definisi zona, nilai d dan k, hasil kecocokan. Definisi aksi final dikonfirmasi pengguna.

---

## Tahap 11: Kalkulator KIM-MHO

**Tujuan:** fungsi yang menghitung skor resmi persis seperti formulir BAuA.

**Langkah:**
1. Salin tabel dari **formulir PDF asli** ke `configs/kim.yaml`, dua kali secara terpisah (double entry). Selesai 15 Nov: entri 1 (PROJECT_OVERVIEW §3) dan entri 2 (`sources/transcription/kim_form_entry2.yaml`, dibaca dari gambar formulir) cocok; dicek ulang dengan `sources/pages/form_p-2.png`, `form_p-3.png` → `verified: true`. Sumber (PDF, gambar halaman, transkripsi) di `sources/` (tidak masuk Git; lihat `sources/README.md` dan `sources/FINDINGS.md`). FmaxM: `fmax_n: {thumb: 80, index: 50}`, `fmax_scenarios_thumb: [56, 70, 80, 137]`.
2. Fungsi murni (tanpa I/O) di `src/kimcam/kim.py`. Masukan gaya dari `meta.yaml: force_n` (satu angka N per gerakan, Tahap 5): tingkat gaya = `force_level(force_n[move], fmax_n[jari])`, jari dari Tahap 10.
3. **Aksi dengan tingkat gaya yang sama dijumlah frekuensinya dulu, baru dilihat di tabel** (`level_frequencies`), lalu poin semua sel dijumlah per tangan (gerak dan tahan pada tingkat yang sama sama-sama dihitung, A55 cetak hlm. 32); dipakai tangan tertinggi. **[Bersumber]**
4. Kasus uji resmi A55 (jawaban dihitung BAuA) di `tests/data/kim_cases.yaml` (salinan `sources/transcription/a55_test_cases.yaml`): 5 poin waktu (hlm. 23), 7 kasus gaya (hlm. 30–35), 1 skor lengkap (hlm. 47: 3,5 × 12 = 42, risiko 2).

**Kode inti:** `src/kimcam/kim.py` (`time_points`, `time_word_points`, `force_level`, `lookup`, `level_frequencies`, `force_cells`, `force_points`, `kim_score` → rincian poin, skor, kategori, peringatan), `configs/kim.yaml`.

**Aturan dari sumber asli (diterapkan 15 Nov atas izin pengguna; bukti di `sources/FINDINGS.md`, dicek ulang di gambar halaman):**
- **Poin waktu linear** = jam sub-aktivitas, minimal 1, maksimal 10 (A55 cetak hlm. 23: 5,5 jam → 5,5; hlm. 47: 3,5 × 12 = 42). Bukan dibulatkan ke atas.
- **Frekuensi dan detik tahan memakai nilai mentah, tanpa pembulatan.** "< 5" eksklusif (A55 cetak hlm. 34: 4,5/menit → "< 5"; hlm. 35: 4,65 → "< 5"); kolom lain inklusif di batas atas; nilai di celah (15,5) masuk kolom berikutnya (Asumsi, selaras "poin berlaku di ujung rentang", hlm. 28). Keputusan "dibulatkan ke terdekat" (15 Nov pagi) **dibatalkan** karena membuat contoh resmi hlm. 34 salah (11, bukan 5,5).
- **Sel abu-abu = 100 poin** + peringatan (A55 cetak hlm. 28: "graue Felder"). "Sangat tinggi 61–90" dan "memukul 16–90" ikut 100 (Sebagian: sel tanpa angka sendiri). Sel diarsir (tahan × memukul) = tidak berlaku → error.
- Aturan formulir lain (hlm. 2): waktu tahan hanya dihitung bila lengan statis ≥ 4 detik tanpa putus (A55 cetak hlm. 33: tahan 3 s diabaikan; ini tugas Tahap 10, bukan `kim.py`); frekuensi > 90/menit → ekstrapolasi linear atau KIM-MHO-E (tanya pengguna). Bila tingkat "puncak" atau "memukul" muncul, nilai juga dengan KIM-BF → peringatan di `kim.json`.

Yang dihentikan dengan error (bukan 0): sel diarsir, nilai di atas tabel (> 90/menit, > 60 s tahan/menit, > 10 jam), nilai negatif, nilai indikator di luar skala formulir.

**Tes:** `tests/test_stage11_kim.py`: batas 4,5 · 4,99 · 5 · 15 · 15,5 · 16 · 30 · 30,5 · 60 · 61 · 90 · 90,5 · 91 gerak/menit dan 15 · 15,5 · 16 · 30 · 31 · 60 detik tahan/menit; sel abu-abu = 100; sel diarsir error; batas tingkat gaya; kata waktu; penjumlahan frekuensi tingkat sama; **semua kasus resmi A55** (kasus hlm. 35 tangan kanan butuh interpolasi → di-skip sampai versi 2).

**Lulus jika (disetujui pengguna 15 Nov):** ≥ 10 kasus resmi A55 menghasilkan skor yang sama persis dengan jawaban BAuA (selisih 0), termasuk 2 contoh hlm. 30–31 dan skor lengkap hlm. 47. "KIM Tool 2019 COAPRE" dihapus dari kriteria (sumbernya tidak ditemukan, `sources/FINDINGS.md` #6). Formulir interaktif LMM-MA-E dipakai nanti untuk menguji versi interpolasi (v2).

**Catat:** daftar kasus dan hasilnya.

---

## Tahap 12: P1–P3 dan uji jawaban-diketahui

**Tujuan:** skema menunjuk aksi dan bagian tubuh yang benar.

**Format label** (keluaran Tahap 10, `data/interim/<P>/<S>/labels.parquet`; dipakai P1–P3; ditetapkan 15 Nov): satu baris per frame per tangan, kolom `t` (detik), `cycle`, `hand` (`left`/`right`), `move` (`move_1`… atau `""`), `finger` (`thumb`/`index`/`""`), `ang_<sendi>` (derajat, tanda sesuai PROJECT_OVERVIEW §4.3; ditambah 15 Nov untuk P4), dan `oor_<sendi>` (True = sendi di luar batas, mis. `oor_wrist_fe`), dihitung dari `ang_<sendi>` + `configs/thresholds.yaml` lewat `angles.oor_from_angles`. Satu kejadian aksi = frame berurutan dengan `move` sama di satu tangan.

**Langkah:**
1. `attribution.py` (P1), `whatif.py` (P2), `profile.py` (P3) sesuai `PROJECT_OVERVIEW.md` §6.
   - P1: poin gaya tiap tingkat di tangan penentu dibagi ke aksi sebanding jumlah kejadian (tangan seri → dibagi dua); poin posisi tangan/lengan dibagi ke aksi sebanding frame di luar batas pada sendi terburuk (sendi seri → dibagi rata); indikator lain (pegangan, kondisi, postur, organisasi) dicatat sebagai baris sendiri.
   - P2: perbaikan yang dicoba per aksi: `posture` (semua sendi aksi itu di dalam batas) dan `thumb` (telunjuk → ibu jari); greedy dengan hitung ulang sampai tidak ada penurunan.
   - P3: per siklus, % frame di luar batas per (aksi × sendi × tangan), penyumbang terbesar (frame di luar batas terbanyak), jari tekan; "konsisten" bila penyumbang terbesar sama di ≥ 70% siklus.
   - Aksi tanpa label jari memakai FmaxM telunjuk (lebih konservatif, Asumsi). Tahan statis ≥ 4 s belum dihitung (`shortcut:` di kode, menunggu label tahan Tahap 10). Perbandingan antar orang (Wilson 95%) menyusul saat ada > 1 peserta.
2. Uji jumlah: jumlah semua bagian P1 = poin indikator resmi, dan total = skor resmi.
3. **Uji jawaban-diketahui** (1–2 orang, boleh peneliti sendiri):
   - A: 15 siklus normal, lalu 15 siklus dengan pergelangan sengaja ditekuk > 45° **hanya saat tekan**;
   - B: 15 siklus menekan dengan ibu jari, lalu 15 siklus menekan dengan **telunjuk** (FmaxM 80 → 50 N, jadi tingkat gaya tekan harus naik).

**Lulus jika:** uji jumlah lulus (toleransi 1e-9). Pada A, P1 menunjuk tekan × pergelangan × tangan yang dipakai sebagai penyumbang terbesar, dan P2 menempatkan "perbaiki tekan" di urutan pertama. Pada B, label jari benar dan poin gaya tekan naik sesuai tabel.

**Uji dini (label buatan):** `tests/test_stage12_p123.py`: uji jumlah; A (15 + 15 siklus, tekuk saat `move_3`) → P1 menunjuk `move_3 × wrist_fe × right`, P2 nomor 1 = `move_3 posture`; B (telunjuk vs ibu jari, 30 N) → gaya 5,5 → 7,5, P2 nomor 1 = `move_3 thumb`; P2 kosong bila tidak ada yang bisa diturunkan; P3 konsisten/tidak; jari per siklus.

Catatan: karena KIM memakai fungsi tangga, P2 bisa memberi penurunan **0** untuk perbaikan yang nyata (mis. sendi terburuk turun dari 15% ke 6% masih 1 poin). Ini sifat aturan resmi, bukan bug; versi interpolasi (v2) akan lebih halus.

**Catat:** hasil uji, contoh kartu hasil.

---

## Tahap 13: P4 kestabilan

**Tujuan:** melaporkan seberapa tahan kesimpulan P1–P3 terhadap galat dan asumsi.

**Langkah:** Monte Carlo 1.000 kali per orang (`src/kimcam/stability.py`, `simulate`). Butuh kolom sudut `ang_<sendi>` di label; `oor_<sendi>` dihitung ulang dari sudut + `configs/thresholds.yaml` (`angles.oor_from_angles`). Setiap kali (semua Asumsi, disetujui pengguna 15 Nov):
- galat sudut tetap per sendi ~ N(bias, SD) dari `configs/angle_error.yaml` (sekarang Asumsi: bias 0°, SD 5°, pronasi/supinasi SD 10°; diganti hasil goniometer Tahap 9);
- batas sudut tiap sendi digeser seragam ±5°;
- FmaxM ibu jari dari distribusi segitiga (min 56, modus 80, maks 137 N; dari `fmax_scenarios_thumb`); FmaxM telunjuk tetap;
- **gaya tiap gerakan × seragam(0,9; 1,1)** (pengganti bootstrap 10 tekan yang dihapus 14 Nov);
- label aksi digeser bersama ±3 frame terhadap sudut.

Laporkan juga tabel skenario tetap FmaxM 56 / 70 / 80 / 137 N (`fmax_scenarios`, tanpa acak), supaya dosen bisa melihat pengaruh tiap pilihan.

**Uji dini (label buatan, `tests/test_stage13_stability.py`):** sudut → label sama dengan label Tahap 12; tekuk 55° (jelas) vs 46° (tipis, batas 45°): perbaikan nomor 1 sama di 94% vs 49% dari 200 simulasi; hasil bisa diulang dengan `seed`; skenario FmaxM 56/70/80/137 N → skor 42/34/34/30. Waktu: ±0,12 s per simulasi untuk 5 menit label → ±2 menit per 1.000 simulasi (±6–7 menit untuk 15 menit).

**Lulus jika:** laporan terbentuk berisi % simulasi dengan penyumbang terbesar sama dan perbaikan nomor 1 sama. Ini laporan, bukan lulus/gagal.

**Catat:** angka kestabilan per orang.

---

## Tahap 14: Pilot satu orang end-to-end

**Tujuan:** menjalankan seluruh protokol dari persetujuan sampai kartu hasil, dan mengukur waktu serta ruang disk.

**Protokol sesi (dipakai juga untuk pengambilan data):**
1. Sebelum peserta datang:
   - cek ruang disk (≥ 40 GB);
   - kalibrasi hari itu ada;
   - exposure sesuai `cameras.yaml`;
   - perangkat load cell menyala dan dinolkan.
2. Persetujuan.
3. Rekam posisi netral 2 detik.
4. Penjelasan tugas yang sama untuk semua orang (baca naskah), 3 siklus latihan. Jangan mengajari jari mana yang dipakai; biarkan cara alami.
5. **Ukur gaya:** setiap gerakan di `moves` dilakukan di perangkat load cell dengan cara alami (cara menghitung dari Tahap 4). Catat satu angka N per gerakan.
6. `tools/record_session.py --participant P001 --session S01`: isi formulir (nama, gender, tangan dominan, pengalaman, gaya per gerakan), konfirmasi, lalu rekam tugas **15 menit** (kamera saja).
7. Setelah sesi: manifest + salin cadangan ke disk kedua (termasuk `participants_private.csv`); cek jumlah frame.
8. Proses: `tools/process_session.py P001 S01` → pose → 3D → sudut → segmen → KIM → P1–P4 → `card.md`.

*(Opsional, ditunda: tes tekan maksimal ibu jari (MVC) dengan protokol Lo/Caldwell — naik 1–2 detik, tahan 5 detik, rata-rata 3 detik tengah, 3 kali, istirahat ≥ 2–3 menit. Hanya untuk laporan tambahan "persen dari kemampuan sendiri", bukan untuk skor resmi.)*

**Lulus jika:** kartu hasil lengkap. Waktu proses dan ukuran data tercatat. Semua masalah dicatat dan diperbaiki sebelum peserta berikutnya.

---

## Templat `docs/progress-log.md`

```
## Tahap XX: <nama> (tanggal)
- Uji dini: <angka utama> (info)
- Uji final: <angka utama>  → LULUS / GAGAL / menunggu setup beku
- Yang berubah: <file, versi, setting>
- Masalah + solusi:
- Keputusan baru (status: Bersumber / Sebagian / Asumsi / Usulan):
- Commit / tag: stage-XX-pass
```
