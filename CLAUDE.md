# CLAUDE.md: Skema Penilaian Teknik Kerja Berbasis KIM-MHO (6 kamera + load cell)

Versi 14 Nov 2026 (revisi malam: load cell di perangkat terpisah, gaya diketik per gerakan, gerakan generik). Detail lengkap ada di `docs/PROJECT_OVERVIEW.md` (riset, aturan KIM, algoritma) dan `docs/STAGES.md` (tahap kerja, kode, tes). File ini sengaja pendek (< 200 baris). Baca bagian dokumen yang relevan saat dibutuhkan saja.

## 1. Proyek dalam 5 kalimat

- Peserta duduk dan merakit benda (belum diputuskan: cover snap-fit atau gear) di atas jig, 15 menit per orang (±90 siklus). Gerakan diberi nama umum `move_1`, `move_2`, … sampai definisinya diputuskan bersama dosen.
- 6 kamera (3D) mengukur sudut sendi, jumlah aksi, dan jari yang menekan. Gaya diukur di **perangkat load cell terpisah** sebelum rekaman, lalu **satu angka (N) per gerakan** diketik ke formulir pendataan peserta di program rekam. Tidak ada sinkron dengan kamera. Skor **resmi** KIM-MHO v12.5 (BAuA 2019) dihitung per sub-aktivitas, dengan batas sudut dari OCRA dan FmaxM ibu jari 80 N / telunjuk 50 N.
- **P1:** poin skor dipecah ke aksi × bagian tubuh × tangan. **P2:** "bagaimana jika" (skor resmi dihitung ulang bila satu aksi diperbaiki). **P3:** pola kesalahan per orang lintas siklus.
- Bukti kepercayaan: akurasi (goniometer, beban kalibrasi, cek aturan vs formulir BAuA) dan kestabilan (P4, Monte Carlo).
- Tidak mengklaim setara penilaian ahli. Avatar, perbandingan kelompok, dan Borg sudah **dihapus** dari rencana.

## 2. Aturan kerja (wajib)

1. **Satu tahap, uji dini + uji final.** Kerjakan tahap di `docs/STAGES.md` berurutan. **Uji dini** dikerjakan sekarang dengan setup apa adanya; hasilnya dicatat sebagai info dan cukup untuk lanjut ke tahap berikutnya. **Uji final** (yang menentukan LULUS, dicatat di `docs/progress-log.md`, di-commit dengan tag `stage-XX-pass`) baru dikerjakan setelah **setup fisik dibekukan**, berurutan dari Tahap 1. Tahap 7 ke atas (kalibrasi dan seterusnya) baru dimulai setelah setup dibekukan. Pembagian per tahap: `docs/STAGES.md` bagian "Uji dini vs uji final". Keputusan pengguna 15 Nov.
2. **Jelaskan kode ke pengguna.** Pengguna ingin mengerti kodenya. Sebelum menulis file baru, jelaskan dalam bahasa Indonesia sederhana: tujuannya, input → proses → output, dan cara mengetesnya. Sesudahnya, ringkas apa yang berubah. Komentar di kode singkat dan hanya untuk bagian yang tidak jelas.
3. **Kode seminimal mungkin.** Pakai plugin ponytail. Jangan membuat abstraksi, kelas, atau opsi yang belum dibutuhkan tahap ini.
4. **Tanya sebelum keputusan besar**: mengganti library/versi, mengubah aturan KIM, mengubah protokol rekaman, atau menghapus data. Jangan langsung setuju; beri pendapat kritis.
5. **Perangkat keras: jangan menebak.** Pengguna masih baru di elektronika. Jelaskan langkah demi langkah dan minta foto/screenshot bila ragu (kabel, Device Manager, label kamera).
6. **Label status** untuk setiap klaim di dokumen: Bersumber / Sebagian / Asumsi / Usulan. Bedakan kutipan langsung dari parafrase, dan sertakan link.
7. **Data tidak masuk Git.** Folder `data/` (rekaman, nama peserta) dan `sources/` (PDF berhak cipta) ada di `.gitignore`. Repo GitHub **public** (keputusan pengguna 15 Nov), jadi jangan pernah `git add -f` file dari kedua folder itu, dan jangan menulis nama peserta di file lain. Integritas file dijaga dengan `data/manifest.csv` (SHA-256).
8. **Versi dikunci.** Jangan menaikkan versi paket di `requirements.txt` tanpa izin. Setelah instalasi berubah, perbarui `requirements.lock.txt`.
9. Bahasa Indonesia untuk penjelasan dan dokumen. Nama variabel/fungsi dalam bahasa Inggris pendek.

## 3. Lingkungan (Tahap 0, 14 Nov 2026; detail di `configs/environment.yaml`, perbarui dengan `python tools/env_report.py`)

| Item | Nilai |
|---|---|
| OS | Windows 11 Enterprise LTSC 10.0.26100 |
| CPU / core | AMD Ryzen 9 9950X3D / 16 core |
| RAM | 64 GB |
| GPU / VRAM / driver CUDA | RTX 5060 Ti / 16 GB / driver 610.88, CUDA 13.3 → onnxruntime-gpu 1.30.0 |
| Disk kosong (SSD) | C: ±155 GB, D: ±446 GB (satu NVMe 1 TB). ±8,5 GB per orang per 15 menit (diukur 15 Nov, adegan uji) → data di **D:\kimcam-data** (junction `data/`) |
| USB host controller | 5 (AMD USB 3.10 ×3, ASMedia USB 3.20 ×1, AMD USB 2.0 ×1); 6 "USB Camera" sudah terlihat |
| Python | 3.12, conda env `kimcam` (Anaconda); semua paket lewat **pip**, bukan conda |
| Arduino | Tidak tersambung ke PC ini. Nano clone (CH340) + HX711 (DT → D3, SCK → D2) hanya di perangkat load cell terpisah. Sinkron kamera tanpa LED (Tahap 6, dari gerakan tangan) |

Usulan minimum (Asumsi): GPU NVIDIA ≥ 8 GB VRAM, CPU ≥ 8 core, RAM 32 GB, SSD NVMe, 2–3 USB host controller terpisah. Tanpa GPU NVIDIA: jalur CPU (OpenVINO) hanya untuk tes kecil.

## 4. Kamera (label tetap; jangan pernah memakai nomor index OpenCV)

Kiri/kanan = sisi **peserta** (sama dengan tangan kiri/kanan di analisis). Disetujui pengguna 14 Nov; posisi `front` dan `top` belum final.

| Label | Posisi | Peran (Usulan) |
|---|---|---|
| front_left | Depan kiri | Pergelangan dan siku dari depan |
| front | Depan tengah | Pergelangan dan siku dari depan |
| front_right | Depan kanan | Pergelangan dan siku dari depan |
| top | Tepat di atas tangan | **Utama untuk jari** |
| wing_left | Sayap kiri | Tekuk pergelangan dari samping |
| wing_right | Sayap kanan | Tekuk pergelangan dari samping |

- Model: InnoMaker U20CAM-9281M (OV9281 mono, global shutter, 1280×800, fisheye 148°, USB 2.0, UVC). Di Windows: VID 0C45 / PID 636D, nama "USB Camera".
- Keenam kamera berseri sama (`SN0001`, bawaan pabrik), jadi kamera dikenali dari **alamat fisik port USB** (`usb_port` di `configs/cameras.yaml`, diisi `tools/identify_cameras.py`), bukan seri. Keputusan pengguna 14 Nov: seri tidak diganti.
- Akibatnya: **kabel kamera tidak boleh bertukar port, dan hub tidak boleh pindah port PC.** Label fisik ada di badan kamera, kedua ujung kabel, dan port hub. Kalau colokan berubah, jalankan ulang `identify_cameras.py`.
- Susunan USB sekarang: 3 hub eksternal, masing-masing 2 kamera, di 3 controller berbeda.
- Rekam: 1280×800, MJPG, 30 fps, exposure manual (nilai dari Tahap 2; wajib diisi karena kamera mengingat exposure terakhir).
- OpenCV + DSHOW (dicek 15 Nov): set FOURCC **terakhir**; pakai `read()`, **bukan** `grab()` (grab tidak menunggu frame baru).

## 5. Tech stack (versi dikunci)

| Lapisan | Paket / alat |
|---|---|
| Env | Python 3.12, conda env `kimcam`, paket hanya lewat `pip` (mencampur paket conda + pip berisiko dua OpenCV / dua CUDA); `requirements.txt` + `requirements.lock.txt` |
| Kamera | `opencv-contrib-python==4.13.0.92` (**hanya satu** paket OpenCV), `cv2-enumerate-cameras==1.4.0`. FFmpeg terpisah **tidak wajib** (OpenCV membawa FFmpeg sendiri); hanya cadangan Tahap 5 bila CPU > 80%. Jangan dipasang lewat conda-forge ke env `kimcam` (15 Nov: bentrok `glib` defaults vs conda-forge, ffmpeg gagal jalan) |
| Gaya | Perangkat terpisah (HX711 + Arduino, library `bogde/HX711`). Hasilnya diketik manual: satu angka N per gerakan per peserta |
| Kalibrasi + 3D | `aniposelib==0.8.0` (ChArUco, `fisheye=True`); caliscope sebagai pemeriksa visual |
| Pose 2D | `rtmlib==0.0.16` (**dipasang `--no-deps`**), `mode="performance"` = YOLOX-m + RTMW `rtmw-dw-x-l` 384×288; `onnxruntime-gpu[cuda,cudnn]` 1.30.0 (driver CUDA 13) atau 1.26.0 (driver CUDA 12). Versi 1.32 sudah ada, tapi tetap di versi yang sudah dicek |
| Analisis | numpy, scipy, pandas, pyarrow, numba, pyyaml, toml, tqdm, psutil |
| CAD | manifold3d, trimesh |
| Kualitas | pytest, ruff, pre-commit; plugin Claude Code `ponytail` |

Instalasi (Anaconda Prompt, dari root repo):

```powershell
conda create -n kimcam python=3.12 -y
conda activate kimcam
pip install -r requirements.txt
pip install --no-deps rtmlib==0.0.16
pip install "onnxruntime-gpu[cuda,cudnn]==1.30.*"   # driver CUDA 12: ==1.26.0 ; tanpa GPU: onnxruntime openvino
pip install -e . --no-build-isolation
pip freeze --exclude-editable > requirements.lock.txt
pre-commit install
```

## 6. Struktur repo

```
CLAUDE.md, README.md (penjelasan publik: latar belakang, status, cara mulai)
pyproject.toml (paket kimcam, dipasang `pip install -e . --no-build-isolation`)
requirements.txt, requirements.lock.txt, .gitignore, .pre-commit-config.yaml
configs/   environment.yaml, cameras.yaml, sync.yaml, zones.yaml,
           kim.yaml, thresholds.yaml, angle_error.yaml, session.yaml (skenario jam + daftar gerakan)
hardware/    tes_realtime.ino, tes2_gaya_newton.ino, loadcell_mount.py, loadcell_mount_y.py
             (untuk perangkat load cell terpisah; dudukan load cell + tes lama)
src/kimcam/  cameras.py, intake.py, sync.py, calib.py,
             pose2d.py, triang.py, angles.py, segment.py, kim.py,
             attribution.py, whatif.py, profile.py, stability.py
tools/       env_report.py, list_cameras.py, identify_cameras.py, test_one_camera.py, test_six_cameras.py,
             record_session.py (pendataan peserta + rekam), process_session.py
tests/       test_stage00_env.py ... test_stage14_pilot.py, data/kim_cases.yaml
docs/        PROJECT_OVERVIEW.md, STAGES.md, progress-log.md, decisions.md
sources/     (TIDAK di Git; berhak cipta) PDF formulir KIM-MHO v12.5, A55, dst.
data/        (TIDAK di Git; junction ke D:\kimcam-data) raw/, calib/, interim/, results/, manifest.csv,
             participants_private.csv (ID ↔ nama; satu-satunya tempat nama disimpan)
```

## 7. Perintah umum

```powershell
conda activate kimcam
pytest tests/test_stage00_env.py -v      # ganti nomor sesuai tahap
ruff check src tools tests
python tools/env_report.py               # perbarui configs/environment.yaml
```

## 8. Tahap kerja (status diperbarui setiap tahap lulus)

Status fisik (15 Nov): posisi kamera sudah tetap; rig 3D print sedang dicetak, kabel belum dirapikan (kamera kadang tersenggol). **Setup belum beku.**

| # | Tahap | Lulus jika (ringkas, uji final) | Status |
|---|---|---|---|
| 0 | Lingkungan + repo | 1 paket cv2, provider CUDA aktif, `CharucoDetector` ada, `environment.yaml` terisi | **Lulus** (tag `stage-00-pass`) |
| 1 | Inventaris + label kamera | Peta label→port tetap setelah reboot dan cabut-colok; uji tutup lensa benar | Uji dini lulus 15 Nov; final menunggu setup beku |
| 2 | Tes 1 kamera | ≥ 29,5 fps, tidak ada jeda > 67 ms, exposure manual terkunci | Uji dini lulus 15 Nov; final menunggu lampu final |
| 3 | Tes 6 kamera (DSHOW vs MSMF) | 6 kamera lulus kriteria Tahap 2 selama 5 menit | Uji dini 15 Nov: DSHOW dipilih (MSMF ±3% frame dobel); hub C 2× gangguan |
| 4 | Load cell di perangkat terpisah | Galat ≤ 0,3 N vs beban acuan; cara mendapat 1 angka per gerakan tertulis | [ ] |
| 5 | Pendataan peserta + program rekam 6 kamera | Formulir menolak input salah; nama hanya di `participants_private.csv`; rekaman 5 menit: fps ±0,5% dari fps terukur, frame di jendela waktu bersama sama di 6 kamera ±2, tanpa jeda > 67 ms/dobel; manifest tertulis | Uji dini lulus 15 Nov; final menunggu setup beku |
| 6 | Sinkron antar kamera dari gerakan tangan (**sesudah Tahap 8**) | Offset per kamera stabil (SD < 5 ms antar potongan 1 menit); reproyeksi tidak memburuk | [ ] |
| 7 | Kalibrasi kamera | Reproyeksi < 0,5 px; 3× ulang, posisi kamera beda < 5 mm | [ ] |
| 8 | Pose 2D RTMW | Tangan terlihat ≥ 3 kamera termasuk `top`; getaran pergelangan saat diam < 2 px SD | [ ] |
| 9 | 3D + sudut + uji goniometer | Bias dan batas kesesuaian tercatat per sudut | [ ] |
| 10 | Segmentasi siklus + aksi + jari (kamera saja) | Batas aksi ≥ 90% (±3 frame); jumlah tekan selisih ≤ 2%; jari benar ≥ 95% | [ ] |
| 11 | Kalkulator KIM-MHO | ≥ 10 kasus resmi A55 identik dengan jawaban BAuA (selisih 0), termasuk hlm. 30–31 dan 47 | **Lulus 15 Nov** (12 kasus resmi A55 identik; tag `stage-11-pass`) |
| 12 | P1–P3 | Jumlah atribusi = skor resmi; uji jawaban-diketahui A (pergelangan) dan B (telunjuk) lulus | Uji dini lulus 15 Nov (label buatan); final butuh rekaman nyata |
| 13 | P4 kestabilan | Laporan % simulasi dengan kesimpulan sama | Uji dini lulus 15 Nov (label buatan, galat sudut Asumsi) |
| 14 | Pilot 1 orang end-to-end | Pendataan (termasuk gaya) + rekaman 15 menit → kartu hasil lengkap | [ ] |

## 9. Yang belum diputuskan (jangan diasumsikan; tanya pengguna)

Angka skenario poin waktu (≥ 1 jam, usulan 4 jam) · batas miring pergelangan (15°/20° atau 20° gabungan) · jumlah dan definisi gerakan (sementara `move_1`, `move_2`, …; menunggu rapat dosen) · benda (cover atau gear) · peran expert · tes MVC (ditunda). Detail: `docs/PROJECT_OVERVIEW.md` §9.

**Sudah diputuskan, jangan diubah tanpa izin:** gaya = satu angka N per gerakan per peserta, diukur di perangkat load cell terpisah sebelum rekaman dan diketik ke formulir pendataan (tanpa ukur ulang sesudah rekaman); nama peserta hanya di `data/participants_private.csv`, semua file lain memakai ID (P001); tidak ada sinkron kamera ↔ load cell; FmaxM ibu jari 80 N dan telunjuk 50 N (`PROJECT_OVERVIEW.md` §3.3a); aksi dengan tingkat gaya sama dijumlah frekuensinya dulu (A55 hlm. 30–31).
