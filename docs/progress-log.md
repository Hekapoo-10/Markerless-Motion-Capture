# Progress log

## Tahap 0: Lingkungan, repo, dan deklarasi PC (14 Nov 2026)
- Hasil tes: `pytest tests/test_stage00_env.py` → 4/4 lulus (satu OpenCV, CharucoDetector ada, model contoh jalan di CUDAExecutionProvider, aniposelib + rtmlib ter-import); `ruff check` bersih → **LULUS**
- PC (`configs/environment.yaml`): Ryzen 9 9950X3D 16 core, RAM 64 GB, RTX 5060 Ti 16 GB, driver 610.88 / CUDA 13.3, C: ±155 GB kosong, D: ±446 GB kosong, 5 USB host controller, 6 "USB Camera" terlihat.
- Yang berubah: conda env `kimcam` (Python 3.12.15), paket lewat pip (`requirements.txt`, `requirements.lock.txt`); onnxruntime-gpu **1.30.0** (CUDA 13); rtmlib 0.0.16 `--no-deps`; `pyserial` dihapus (load cell tidak tersambung ke PC ini).
- Masalah + solusi:
  - Header `nvidia-smi` baru menulis `CUDA UMD Version`, bukan `CUDA Version` → regex `env_report.py` menerima keduanya.
  - Tes CUDA lama hanya mengecek daftar provider (selalu berisi CUDA walau DLL gagal) → tes sekarang menjalankan `sigmoid.onnx` di GPU.
  - ruff 0.17 tanpa config sudah memakai aturan import (I001) dan PLW1510 → kode diikuti, tidak menambah config.
- Keputusan baru:
  - Env: conda + pip, bukan uv (pengguna sudah memakai Anaconda). **Disetujui pengguna**
  - Load cell di perangkat terpisah; gaya = satu angka N per gerakan, diketik di formulir pendataan (Tahap 5); tanpa ukur ulang sesudah rekaman. **Disetujui pengguna**
  - Gerakan generik `move_1`, `move_2`, … sampai rapat dosen. **Disetujui pengguna**
  - Nama peserta hanya di `data/participants_private.csv`. **Disetujui pengguna**
  - Data disimpan di D: (C: hanya ±155 GB kosong). **Usulan** (diputuskan di Tahap 5)
  - FFmpeg dipasang di Tahap 2. **Disetujui pengguna**
- Commit / tag: commit pertama 15 Nov (bersama pekerjaan Tahap 1–13), tag `stage-00-pass`
- GitHub (15 Nov): remote `origin` = https://github.com/Hekapoo-10/Markerless-Motion-Capture, **public** (rencana awal private; pengguna memilih public setelah diingatkan). `data/` dan `sources/` tidak ikut. **Disetujui pengguna**

## Tahap 1: Inventaris dan label kamera (15 Nov 2026)
- Uji dini: `pytest tests/test_stage01_cameras.py` → 3/3 lulus (DSHOW + MSMF); uji tutup lensa → 6/6 benar → **UJI DINI LULUS**
- Uji final: ulang setelah reboot dan cabut-colok → **menunggu setup beku** (rig 3D print masih dicetak, kabel belum dirapikan; jalankan ulang `identify_cameras.py` dulu karena port bisa berubah)
- Yang berubah: label baru `front_left, front, front_right, top, wing_left, wing_right` (kiri/kanan = sisi peserta); kamera dikenali dari alamat port USB fisik (`usb_port`); file baru `src/kimcam/cameras.py`, `tools/list_cameras.py`, `tools/identify_cameras.py`, `configs/cameras.yaml`, `pyproject.toml` (kimcam dipasang editable).
- Peta sekarang (hub A = `PCI(0004)`, B = `PCI(0003)`, C = `PCI(0C00)`): front_left C·2, front A·2, front_right B·1, top A·1, wing_left C·1, wing_right B·2.
- Masalah + solusi:
  - Keenam kamera berseri sama (`SN0001`); hanya satu yang mendapat ID berbasis seri dari Windows → ID instance tidak dipakai, yang dipakai alamat port fisik perangkat induk (`DEVPKEY_Device_LocationPaths`).
  - Urutan index DSHOW ≠ MSMF (terbukti) → index tidak pernah disimpan.
  - Salah tekan saat memberi label (label dobel) → alat menolak label yang sudah dipakai.
- Keputusan baru:
  - Tata letak kamera: 3 depan (kiri, tengah, kanan), 1 atas tangan, 2 sayap; kamera belakang dihapus. **Disetujui pengguna**
  - Seri kamera tidak diganti; identifikasi lewat port USB. Kabel tidak boleh bertukar port, hub tidak boleh pindah port PC. **Disetujui pengguna**
  - Posisi `front` dan `top` belum final (kalibrasi Tahap 7 menunggu). **Disetujui pengguna**
  - 15 Nov: alat pendukung (`list_cameras`, `test_one_camera`, `test_six_cameras`, `view_cameras`) dipindah ke `tools/support/`; path `tools/…` di catatan lama mengacu ke sebelum pemindahan.
  - 15 Nov (`tools/support/view_cameras.py`): pengguna mengonfirmasi `front_left`/`front_right` benar di kiri/kanan peserta, dan `wing_right` mengarah ke bahu belakang kanan peserta (sesuai).
  - Aturan kerja: uji dini sekarang, uji final setelah setup fisik dibekukan; Tahap 7+ menunggu setup beku. **Disetujui pengguna (15 Nov)**
- Commit / tag: belum

## Tahap 2: Tes satu kamera (15 Nov 2026)
- Uji dini: `tools/test_one_camera.py top 60` (DSHOW) → auto: 30,20 fps, jeda maks 49,1 ms, 0 jeda > 67 ms, 0 dobel, MJPG 1280×800; manual −7: sama, exposure terbaca −7 → **UJI DINI LULUS**. Contoh frame jernih (kamera belum menghadap tangan).
- Uji final: exposure final (setelah lampu final) + cek tajam saat menekan → **menunggu setup beku**
- Yang berubah: `cameras.py` set FOURCC **terakhir**; `tools/test_one_camera.py` baru (pakai `read()`, hitung frame dobel); FFmpeg dihapus dari daftar wajib.
- Masalah + solusi:
  - FOURCC di-set duluan → DSHOW kembali ke YUY2 → FOURCC di-set terakhir.
  - `grab()` DSHOW tidak menunggu frame baru (±2,8 juta/detik) → semua loop memakai `read()`, timestamp setelah `read()` (STAGES Tahap 2, 3, 5 diperbarui).
  - Kamera mengingat exposure manual terakhir → `exposure` wajib diisi sebelum rekaman.
  - MSMF (5 detik): 29,2–29,4 frame baru/detik, ada frame dobel, jeda sampai 80 ms, exposure −8 terbaca −6 → DSHOW lebih baik sejauh ini; diputuskan di Tahap 3.
  - FFmpeg dari conda-forge di env `kimcam` gagal jalan (`0xC0000139`, `glib` defaults vs conda-forge) dan sempat menaikkan openssl → dihapus, openssl/ca-certificates dikembalikan ke `defaults`; env dicek bersih (0 paket conda-forge, pip = lock, 7/7 tes lulus).
- Keputusan baru:
  - FFmpeg terpisah tidak wajib; cadangan Tahap 5 saja. **Disetujui pengguna**
- Commit / tag: belum

## Tahap 3: Tes enam kamera bersamaan (15 Nov 2026)
- Uji dini (`tools/test_six_cameras.py <backend> 300 -7`, 5 menit):
  - DSHOW #1: 5 kamera bersih (30,21 fps, jeda maks ±49 ms, 0 dobel); `front_left` 1 jeda 132,9 ms + 1 dobel (2 frame hilang).
  - MSMF: keenam kamera tepat 9.000 frame tetapi ±275 dobel (±3%) dan 26–32 jeda > 67 ms per kamera → GAGAL semua.
  - DSHOW #2: 5 kamera bersih; `wing_left` berhenti di detik 9,4 (sisa tes hanya frame lama tiap ±1 s, 291 dobel). Kamera tetap terdeteksi Windows; tidak ada event USB di log System.
  - CPU 3–5% rata-rata (maks 9%).
  → **UJI DINI GAGAL** (karena hub C), backend sudah jelas.
- Uji final: ulang 5 menit dengan kabel final → **menunggu setup beku**
- Masalah + temuan:
  - Kedua gangguan DSHOW terjadi di **hub C** (`PCI(0201)…USB(11)`: `front_left`, `wing_left`); hub A dan B bersih di 3 run. Dugaan: kabel/colokan hub C tersenggol atau hub C sendiri (Asumsi; belum dibuktikan).
  - Kamera bisa berhenti mengirim gambar tanpa hilang dari Windows → program rekam (Tahap 5) **wajib** mendeteksi frame beku/dobel dan memberi peringatan langsung.
  - Kamera jalan di 30,2 fps (±9.062 frame / 5 menit) → kriteria Tahap 5 "±0,5% dari 9.000" (maks 9.045) akan menggagalkan kamera sehat.
- Keputusan baru:
  - Backend **DSHOW** (MSMF memalsukan 30,00 fps dengan frame dobel). **Bersumber: diukur**
  - Gangguan hub C ditunda ke uji final (dianggap karena kabel belum dirapikan). **Disetujui pengguna**
  - Kriteria Tahap 5: frame ±0,5% dari (fps terukur × durasi), sama di 6 kamera ±2, tanpa jeda > 67 ms dan tanpa dobel. **Disetujui pengguna**
  - Program rekam Tahap 5 memberi peringatan langsung bila ada kamera beku/dobel. **Usulan**
- Commit / tag: belum

## Tahap 5: Pendataan peserta + program rekam (15 Nov 2026)
- Uji dini:
  - `pytest tests/test_stage05_intake.py` → 3/3 lulus.
  - `record_session.py --participant TEST --session S03 --minutes 5 --exposure -7 --skip-intake` → fps 30,205–30,210; frame di jendela bersama (299,9 s) 9.057–9.058; 0 jeda > 67 ms; 0 dobel; jumlah frame `.avi` = `meta.yaml`; frame terakhir terbaca; 13 baris manifest → **CEK REKAMAN: LULUS**
  - Penolakan benar: tanpa exposure, folder sesi sudah ada.
  - Ukuran: 2,83 GB / 5 menit (±9,4 MB/s) → **±8,5 GB per 15 menit** (bukan ±16 GB; tergantung isi gambar, dicek ulang dengan adegan nyata). Hash SHA-256 ±30 s.
- Uji final: rekaman 5 menit dengan exposure final + rekaman dengan formulir peserta → **menunggu setup beku**
- Yang berubah: `src/kimcam/intake.py`, `tools/record_session.py`, `configs/session.yaml`, `tests/test_stage05_intake.py`; `cameras.yaml` + `format.fps_measured: 30.2`; `data/` = junction ke `D:\kimcam-data`.
- Masalah + solusi:
  - Cek awal "sama ±2 frame" gagal di rekaman 30 detik karena satu kamera mulai ±0,2 s lebih lambat (tanpa frame hilang) → jumlah frame dibandingkan di jendela waktu bersama; fps dicek per kamera.
  - `VideoWriter` MJPG 1 kanal diterima di Windows (sebelumnya "(cek)").
  - Satu peserta bisa beberapa sesi → ID sama diterima bila nama sama.
- Data uji tersisa di `D:\kimcam-data\raw\TEST\` (S01–S03, ±3,5 GB); boleh dihapus pengguna.
- Keputusan baru:
  - Data di `D:\kimcam-data` lewat junction `data/`. **Disetujui pengguna**
- Commit / tag: belum

## Tahap 6: Sinkron antar kamera (15 Nov 2026, keputusan saja)
- Uji dini / final: belum; dikerjakan **sesudah Tahap 8** (butuh pose 2D).
- Keputusan baru:
  - Tanpa LED/Arduino; offset per kamera dicari dari korelasi kecepatan titik tangan antar kamera (cara Pose2Sim). **Disetujui pengguna**. Cadangan bila tidak stabil: kedip senter HP atau FSIN.
  - Kriteria lulus baru (offset stabil SD < 5 ms antar potongan 1 menit; reproyeksi tidak memburuk). **Disetujui pengguna**
- Catatan: fps tiap kamera sedikit berbeda (30,205–30,210) → frame dipasangkan berdasarkan timestamp, bukan nomor urut.

## Tahap 11: Kalkulator KIM-MHO (15 Nov 2026)
- Uji dini: `pytest tests/test_stage11_kim.py` → 46/46 lulus (batas kelompok, sel abu-abu, tingkat gaya, poin waktu, kata waktu, kedua contoh A55 hlm. 30–31 = 7 poin, penjumlahan frekuensi tingkat sama, skor lengkap). Semua tes proyek 56/56.
- Uji final: **belum** — (1) `configs/kim.yaml` entri 2 dari PDF asli (sekarang `verified: false`, dari PROJECT_OVERVIEW §3); (2) ≥ 10 kasus dengan skor dari formulir BAuA LMM-MA-E / KIM Tool 2019.
- Yang berubah: `src/kimcam/kim.py`, `configs/kim.yaml`, `tests/test_stage11_kim.py`; `.gitignore` + `sources/` (PDF berhak cipta).
- Masalah + solusi: situs BAuA menolak akses otomatis (HTTP 403) → pengguna mengirim PDF/halaman yang dibutuhkan.
- Keputusan baru:
  - Frekuensi/detik tahan dibulatkan ke bilangan bulat terdekat (0,5 ke atas) sebelum lookup. **Disetujui pengguna**
  - Error (bukan 0) untuk: sel abu-abu, di atas tabel, gerak + tahan pada tingkat sama di satu tangan, nilai indikator di luar skala. **Usulan** (diganti sore, lihat di bawah)

### Tahap 11, lanjutan (15 Nov sore): pencocokan dengan sumber asli
- Sumber dari pengguna dipindah ke `sources/` (32 file: formulir EN/DE, A55, gambar halaman, transkripsi, `FINDINGS.md`); tidak masuk Git.
- Double entry: `configs/kim.yaml` (entri 1) = `sources/transcription/kim_form_entry2.yaml` (entri 2) untuk semua angka; dicek ulang di gambar formulir hlm. 2–3 → `verified: true`.
- Temuan dari `sources/FINDINGS.md`, **dicek sendiri di gambar halaman**:
  - Poin waktu linear (A55 cetak hlm. 23, 47: 3,5 × 12 = 42; kode lama memberi 48).
  - Sel abu-abu = 100 poin (A55 cetak hlm. 28); sel diarsir = tidak berlaku.
  - Frekuensi tidak dibulatkan: 4,5/menit → "< 5" (A55 cetak hlm. 34; pembulatan memberi 11, buku 5,5).
  - Gerak + tahan pada tingkat sama di satu tangan dijumlah (A55 cetak hlm. 32: kiri 5,5 + 1 + 2 = 8,5) → error buatan sendiri dihapus.
- Uji: `pytest tests/test_stage11_kim.py` → 51 lulus, 1 skip (hlm. 35 kanan butuh interpolasi). Kasus resmi identik: 5 poin waktu + 6 kasus gaya (hlm. 30, 31, 32, 33, 34, 35 kiri) + skor lengkap hlm. 47 = **12 kasus**.
- Keputusan baru:
  - Batas frekuensi: nilai mentah, "< 5" eksklusif, celah (15,5) ke kolom berikutnya — **menggantikan** "dibulatkan ke terdekat". **Disetujui pengguna**
  - Poin waktu linear; sel abu-abu = 100 + peringatan. **Disetujui pengguna**
  - Kriteria lulus Tahap 11: ≥ 10 kasus resmi A55 identik; "KIM Tool 2019 COAPRE" dihapus (tidak ditemukan). **Disetujui pengguna**
- Uji final: 12 kasus resmi A55 identik (selisih 0) → **LULUS** (software, tidak butuh setup beku).
- Terbuka: sel abu-abu tanpa angka (sangat tinggi 61–90, memukul 16–90) = 100 masih Sebagian; nilai di celah (15,5) ke kolom berikutnya masih Asumsi; versi interpolasi (v2) butuh `Algorithmen-Leitmerkmalmethoden.pdf`.
- Commit / tag: commit pertama 15 Nov, tag `stage-11-pass`

## Tahap 12: P1–P3 (15 Nov 2026)
- Uji dini (label buatan, 30 siklus × 10 s): `pytest tests/test_stage12_p123.py` → 7/7 lulus. Uji jumlah (1e-9); A: P1 `move_3 × wrist_fe × right`, P2 nomor 1 `move_3 posture` (−4 = 4 jam × 1 poin); B: gaya 5,5 → 7,5, bagian tekan 5 poin, P2 nomor 1 `move_3 thumb`; P3 konsisten 50% (tidak) vs 100% (ya). Contoh campuran (5 siklus telunjuk + 15 tekuk): skor 40, P2: ibu jari −6 lalu postur −4.
- Uji final: uji jawaban-diketahui A dan B dengan rekaman nyata → **menunggu Tahap 7–10**
- Yang berubah: `src/kimcam/attribution.py`, `whatif.py`, `profile.py`, `tests/test_stage12_p123.py`; format label ditetapkan (STAGES Tahap 10 dan 12).
- Keputusan baru (**Usulan**): aksi tanpa label jari → FmaxM telunjuk; tangan/sendi seri → poin dibagi rata; tahan statis belum dihitung (`shortcut:`); P2 mencoba `posture` dan `thumb` per aksi.
- Catatan: P2 bisa memberi penurunan 0 untuk perbaikan nyata karena fungsi tangga KIM.

## Tahap 13: P4 kestabilan (15 Nov 2026)
- Uji dini (label buatan + sudut): `pytest tests/test_stage13_stability.py` → 8/8 lulus. 200 simulasi: tekuk 55° → perbaikan nomor 1 sama di 94%; tekuk 46° (batas 45°) → 49%. Skenario FmaxM 56/70/80/137 N → skor 42/34/34/30 (kategori tetap "sedikit meningkat"). Waktu ±0,12 s/simulasi (5 menit label).
- Uji final: dengan galat goniometer (Tahap 9) dan rekaman nyata → **menunggu**.
- Yang berubah: `src/kimcam/stability.py`, `src/kimcam/angles.py` (`oor_from_angles`), `configs/thresholds.yaml`, `configs/angle_error.yaml` (Asumsi), `tests/test_stage13_stability.py`; format label + `ang_<sendi>`.
- Keputusan baru:
  - Label menyimpan sudut `ang_<sendi>`; `oor_` dihitung dari sudut + batas. **Disetujui pengguna**
  - Gaya tiap gerakan digoyang ±10% di P4. **Disetujui pengguna**
  - Galat sudut = offset tetap per sendi per simulasi; batas digeser per sendi; label digeser bersama; FmaxM telunjuk tetap; sudut NaN dihitung di dalam batas. **Usulan**
  - Bahu fleksi memakai batas 80° (rentang OCRA 70–80°). **Asumsi**

## Uji final Tahap 1: label kamera (16 Nov 2026)
- Setup dibekukan (rig terpasang dan sesuai, dikonfirmasi pengguna 16 Nov).
- Port USB keenam kamera sama persis dengan `cameras.yaml` → pelabelan ulang tidak perlu.
- Sebelum reboot: uji tutup lensa 6/6 OK; `pytest tests/test_stage01_cameras.py` → 3/3 lulus.
- (a) Setelah cabut-colok semua kabel ke port yang sama: tes 3/3 lulus, uji tutup lensa 6/6 OK → **lulus**
- (b) Setelah reboot: tes 3/3 lulus, uji tutup lensa 6/6 OK → **lulus**
- Hasil: **Tahap 1 LULUS** (uji final). Commit / tag: `stage-01-pass`
