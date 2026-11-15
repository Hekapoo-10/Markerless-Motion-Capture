# kimcam: Markerless Motion Capture untuk penilaian teknik kerja KIM-MHO

Skema penilaian teknik kerja perakitan berbasis **KIM-MHO** (*Key Indicator Method for Manual Handling Operations*, BAuA 2019), memakai 6 kamera tanpa penanda (*markerless*) dan load cell.

Proyek riset di **CSDI Lab, National Taipei University of Technology (Taipei Tech)**, di bawah supervisi **Hendri Sutrisno**.

> Alat ini membantu menilai dan memperbaiki teknik kerja. Alat ini **tidak** mengklaim setara dengan penilaian ahli ergonomi.

## Latar belakang

Riset otomatisasi penilaian ergonomi (RULA, REBA, OCRA, KIM/HAL, EAWS) hampir selalu berhenti di satu pertanyaan: *apakah skor otomatis sama dengan skor ahli?* Ada tiga hal yang jarang disentuh:

1. **Gaya jarang diukur.** Faktor gaya sering diganti tebakan atau jenis pegangan, padahal gaya menentukan tingkat risiko.
2. **Pergelangan dan lengan bawah lemah.** Sudut-sudut kecil inilah yang paling sulit diukur kamera, padahal paling penting untuk kerja perakitan.
3. **Hasilnya hanya satu angka per pekerjaan.** Pekerja dan perancang kerja tidak tahu *bagian mana* dari cara kerjanya yang menyebabkan skor tinggi.

Proyek ini memakai skor **resmi** KIM-MHO apa adanya, lalu menambahkan lapisan penjelasan di atasnya:

| | Pertanyaan yang dijawab |
|---|---|
| **P1 – Atribusi** | Skor resmi berasal dari aksi apa, bagian tubuh apa, dan tangan mana? Jumlah semua bagian tetap sama dengan skor resmi. |
| **P2 – Bagaimana jika** | Kalau satu aksi diperbaiki (postur, atau menekan dengan ibu jari, bukan telunjuk), skor resmi turun berapa? Perbaikan diurutkan dari yang paling berpengaruh. |
| **P3 – Profil kesalahan** | Apakah pola kesalahan seseorang konsisten dari siklus ke siklus (±90 siklus per orang)? |
| **P4 – Kestabilan** | Seberapa tahan kesimpulan P1–P2 terhadap galat kamera dan pilihan asumsi (Monte Carlo)? |

Pertanyaan utama riset: **di mana kesalahan teknik kerja menumpuk (aksi, bagian tubuh, tangan), dan apakah polanya konsisten di dalam satu orang dan antar orang?**

Kepercayaan pada hasil dibangun dari akurasi alat (goniometer, beban kalibrasi, kalkulator vs contoh resmi BAuA) dan kestabilan (P4), bukan dari kecocokan dengan satu penilai ahli. Ahli sendiri sering tidak sepakat untuk sudut pergelangan.

## Tugas dan protokol

- Peserta duduk dan merakit benda pada jig (cover baterai snap-fit atau gear; belum final) selama **15 menit** (±90 siklus).
- Gerakan diberi nama sementara `move_1`, `move_2`, … sampai definisinya ditetapkan.
- **Gaya** diukur sekali sebelum rekaman dengan perangkat load cell terpisah (HX711 + Arduino). Satu angka (N) per gerakan diketik di formulir peserta. Kamera tidak perlu disinkronkan dengan load cell.
- Tingkat gaya = gaya ÷ FmaxM. Dorong ibu jari 80 N, telunjuk 50 N (dari literatur pekerja manufaktur Taiwan dan BAuA), sehingga jari yang menekan ikut dicatat kamera.
- Nama peserta hanya disimpan di file privat lokal. Semua data lain memakai ID (P001).

## Cara kerja

```
Perangkat load cell terpisah ─► gaya (N) per gerakan ─► formulir peserta
6 kamera mono 30 fps (15 menit) ─► pose 2D (RTMW) ─► sinkron antar kamera dari gerakan tangan
   ─► 3D (aniposelib, fisheye) ─► sudut sendi (pergelangan, lengan bawah, bahu)
   ─► siklus, gerakan, jari yang menekan ─► frekuensi per menit + % waktu sendi di luar batas (OCRA)
   ─► kalkulator KIM-MHO v12.5 ─► P1–P4 ─► kartu hasil
```

**Kamera:** 6 × InnoMaker U20CAM-9281M (OV9281 mono, global shutter, 1280×800 MJPG, 30 fps), posisi `front_left`, `front`, `front_right`, `top`, `wing_left`, `wing_right` (kiri/kanan = sisi peserta). Kamera dikenali dari port USB fisik, karena keenamnya punya nomor seri yang sama.

## Status

Pengerjaan bertahap (Tahap 0–14). Setiap tahap punya **uji dini** (dengan setup apa adanya) dan **uji final** (setelah setup fisik selesai). Detail di [`docs/STAGES.md`](docs/STAGES.md) dan [`docs/progress-log.md`](docs/progress-log.md).

| Tahap | Isi | Status |
|---|---|---|
| 0 | Lingkungan dan repo | **Lulus** |
| 1–3 | Label kamera, tes 1 dan 6 kamera (DSHOW, 30,2 fps tanpa frame hilang) | Uji dini lulus |
| 4 | Perangkat load cell | Belum |
| 5 | Formulir peserta + program rekam 6 kamera | Uji dini lulus |
| 6–10 | Sinkron, kalibrasi kamera, pose, sudut, segmentasi aksi | Menunggu rig kamera final |
| 11 | Kalkulator KIM-MHO | **Lulus** (12 kasus resmi BAuA A55 identik) |
| 12–13 | P1–P4 | Uji dini lulus (data buatan) |
| 14 | Pilot satu orang | Belum |

## Teknologi

Python 3.12 (conda + pip) · OpenCV (DirectShow) · rtmlib (RTMW) · onnxruntime-gpu · aniposelib · NumPy / SciPy / pandas · Arduino + HX711 · pytest · ruff

## Struktur

```
configs/      kamera, sesi, tabel KIM-MHO, batas sudut, galat sudut
src/kimcam/   kode utama (kamera, formulir, KIM, P1–P4)
tools/        skrip cek kamera, rekam, dan proses
tests/        tes per tahap (+ kasus resmi A55 di tests/data/)
hardware/     dudukan load cell (CAD) dan sketsa Arduino
docs/         PROJECT_OVERVIEW, STAGES, progress-log
```

`data/` (rekaman dan data peserta) dan `sources/` (PDF acuan BAuA) **tidak** disimpan di Git.

## Memulai (Windows)

```powershell
conda create -n kimcam python=3.12 -y
conda activate kimcam
pip install -r requirements.txt
pip install --no-deps rtmlib==0.0.16
pip install "onnxruntime-gpu[cuda,cudnn]==1.30.*"
pip install -e . --no-build-isolation
pytest
```

Semua paket dipasang lewat pip, bukan conda, supaya tidak ada dua OpenCV atau dua CUDA. Versi terkunci ada di `requirements.lock.txt`. Panduan kerja untuk Claude Code ada di [`CLAUDE.md`](CLAUDE.md).

## Acuan utama

- BAuA (2019). *Key Indicator Method for Manual Handling Operations (KIM-MHO)*, versi 12.5.
- BAuA. *Manuelle Arbeitsprozesse – Gefährdungsbeurteilung mit der Leitmerkmalmethode* (A55).
- ISO 11228-3. *Ergonomics – Manual handling – Handling of low loads at high frequency*.
- Occhipinti, E. (2006); BGIA-Report 2/2007. OCRA: batas rentang gerak sendi.
- Lo, V.E.-W. dkk. (2019, 2021). Kekuatan tangan normatif pekerja Taiwan. *IJERPH* 16:4742; 18:187.

Daftar lengkap dan status tiap klaim ada di [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md).
