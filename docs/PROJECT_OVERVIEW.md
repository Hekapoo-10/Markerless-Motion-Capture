# PROJECT OVERVIEW: Skema Penilaian Teknik Kerja Berbasis KIM-MHO

Versi 14 Nov 2026 (revisi malam: load cell di perangkat terpisah, gaya diketik satu angka per gerakan di formulir pendataan, gerakan generik `move_1`, `move_2`, …; FmaxM ditetapkan). Dokumen acuan untuk Claude Code. Dokumen ini berisi **apa** yang dibangun dan **kenapa**. Cara mengerjakannya tahap demi tahap ada di `STAGES.md`.

Label status: **Bersumber** (dicek di sumber primer) · **Sebagian** (sumber sekunder, abstrak, preprint) · **Asumsi** (pilihan atau perkiraan kita, harus diuji) · **Usulan** (belum disetujui).

---

## 1. Riset dalam satu halaman

| Komponen | Isi |
|---|---|
| Masalah | Riset otomatisasi penilaian ergonomi (RULA, REBA, OCRA, HAL, EAWS) hampir selalu berhenti di "skor otomatis vs skor ahli". Gaya jarang diukur, pergelangan/lengan bawah lemah, dan hasilnya hanya satu angka per pekerjaan. |
| Kontribusi | **Skema** yang (P1) memecah skor resmi KIM-MHO ke aksi × bagian tubuh × tangan dengan total tetap, (P2) menghitung ulang skor resmi untuk skenario "aksi X diperbaiki" lalu mengurutkan perbaikan, (P3) membuat profil kesalahan per orang lintas siklus. |
| Bukti kepercayaan | Akurasi alat (goniometer, beban kalibrasi, cek aturan vs formulir BAuA, uji jawaban-diketahui) + kestabilan (P4, Monte Carlo). |
| Pertanyaan utama | Di mana kesalahan teknik menumpuk (aksi, bagian tubuh, tangan), dan apakah polanya konsisten di dalam satu orang dan antar orang? |
| Tidak diklaim | Setara penilaian ahli; "KIM-MHO otomatis pertama" sebagai kebaruan utama; "skor risiko per aksi"; "pekerja X berisiko tinggi"; gaya per tangan atau per siklus terukur; mengurangi cedera. |
| Dihapus | Avatar MuJoCo, perbandingan kelompok avatar vs SOP, ANCOVA, Soft-DTW, Borg CR-10. |

Dasar celah riset: laporan *Celah riset penilaian ergonomi otomatis* (13 Nov 2026). Contoh pembanding: OCRA-AI (Camargo Salinas dkk. 2026, SSRN 7524739) memakai 1 kamera RGB dan mengganti faktor gaya dengan jenis pegangan. **[Sebagian: pencarian non-sistematis, perlu konfirmasi Scopus/WoS]**

## 2. Tugas, peserta, dan sesi

| Item | Keputusan | Status |
|---|---|---|
| Tugas | Duduk; merakit benda pada jig (cover baterai snap-fit PETG ±30 N, atau gear) | Asumsi (benda belum diputuskan) |
| Aksi | Nama generik `move_1`, `move_2`, … dari `configs/session.yaml: moves` (satu daftar untuk semua peserta). Contoh untuk cover: ambil → posisikan → tekan sampai klik → letakkan | Disetujui pengguna 14 Nov (nama generik); jumlah dan definisi menunggu rapat dosen |
| Peserta | Minimal 10–15 orang; berhenti saat orang baru tidak lagi memunculkan pola kesalahan baru (kejenuhan). Formulir pendataan di program rekam: ID (P001), nama, gender, tangan dominan, pengalaman perakitan, gaya tiap gerakan. **Nama hanya** disimpan di `data/participants_private.csv`; file lain memakai ID. Gender hanya data deskriptif (FmaxM tidak dibedakan per gender, A55 cetak hlm. 15) | Disetujui pengguna 14 Nov |
| Rekaman | 15 menit tugas per orang (±90 siklus bila 1 siklus ±10 detik), **6 kamera saja** | Usulan |
| Gaya | Diukur di **perangkat load cell terpisah** sebelum rekaman. Hasilnya **satu angka (N) per gerakan** per peserta, diketik ke formulir pendataan. Tidak ada ukur ulang sesudah rekaman, tidak ada sinkron dengan kamera. Usulan cara mendapat angka itu: nilai tengah puncak dari beberapa kali gerakan di alat | Disetujui pengguna 14 Nov (satu angka per gerakan); cara menghitung Usulan |
| Jumlah aksi | Dihitung kamera, termasuk **jari yang menekan** (ibu jari/telunjuk) karena FmaxM-nya berbeda | Usulan |
| Sebelum rekaman | Persetujuan; pendataan peserta (termasuk gaya dari alat load cell); rekam posisi netral 2 detik (tangan lurus di meja) untuk offset sudut; 3 siklus latihan | Usulan |
| Opsional (ditunda) | Tes tekan maksimal ibu jari (MVC) per orang, hanya untuk laporan tambahan "persen dari kemampuan sendiri" | Usulan |
| Skenario poin waktu | ≥ 1 jam per shift (syarat ISO 11228-3:2026 §4.2.1), usulan 4 jam. Rekaman hanya memberi laju dan % waktu | Bersumber (syarat) / Usulan (angka) |

Skor = **poin waktu dari skenario** × **jumlah poin indikator dari rekaman**. Bukan 15 menit × 4. Rekaman diperlakukan sebagai sampel cara kerja yang mewakili seluruh skenario (A55 cetak hlm. 22: contoh siklus 6 detik × 3.000 kali = 5 jam → poin waktu 5). **[Bersumber]**

## 3. Aturan KIM-MHO yang diimplementasikan (`src/kimcam/kim.py`, `configs/kim.yaml`)

Sumber utama: formulir KIM-MHO v12.5 (BAuA/ASER, 04.2019, "Draft for practical testing") dan panduan BAuA A55 *Manuelle Arbeitsprozesse – Gefährdungsbeurteilung mit der Leitmerkmalmethode*. Semua angka di bawah **wajib dicocokkan ulang dengan formulir PDF asli** saat Tahap 11.

### 3.1 Unit dan rumus

- Yang dinilai: **sub-aktivitas** = kumpulan siklus dengan ciri yang sama (A55 cetak hlm. 22). Bukan per aksi. **[Bersumber]**
- Skor total = poin waktu × (gaya + pegangan + posisi tangan/lengan + kondisi kerja + postur badan + organisasi kerja). **[Bersumber]**
- Kategori v12.5: < 20 rendah · 20–< 50 sedikit meningkat · 50–< 100 meningkat nyata · ≥ 100 tinggi. **[Bersumber]**

### 3.2 Poin waktu

- Total jam sub-aktivitas per hari → poin 1–10 (sampai 1 jam = 1, sampai 2 jam = 2, …, sampai 10 jam = 10; formulir hlm. 2). Hubungannya linear: **poin = jam** (3,5 jam = 3,5; A55 cetak hlm. 22–23, 47). Poin waktu minimal 1 (formulir hlm. 4). **[Bersumber]**
- Di proyek ini diambil dari `configs/session.yaml: scenario_hours`.

### 3.3 Gaya jari/tangan (per tangan)

- Tingkat gaya = gaya ÷ FmaxM (gaya maksimum populasi sesuai jenis pegangan): ≤ 15% · ≤ 30% · ≤ 50% · ≤ 80% · > 80%. **[Bersumber]**
- Memegang dihitung hanya bila lengan statis **≥ 4 detik** tanpa putus. **[Bersumber]**
- Setiap tingkat gaya yang muncul diberi poin sesuai kolom frekuensi (per menit) atau lama tahan (detik per menit). Poinnya **dijumlahkan per tangan**, lalu dipakai **tangan yang lebih tinggi** (A55 cetak hlm. 25). **[Bersumber]**
- Aksi-aksi dengan **tingkat gaya yang sama dijumlah frekuensinya dulu**, baru dilihat di tabel. Contoh BAuA: 3 aksi rendah per kotak × 30 kotak/menit = 90/menit → 7 poin (A55 cetak hlm. 30); 54 rendah + 12 sedang per menit → 5 + 2 = 7 poin (hlm. 31). **[Bersumber]**
- KIM memakai gaya **khas/rata-rata** per sub-aktivitas: bila ada sedikit variasi, "average values must be formed" (formulir hlm. 4). BAuA sendiri menghitung aksi dari video (A55 cetak hlm. 26, 30) dan biasanya hanya *memperkirakan* tingkat gaya (hlm. 15). Inilah dasar memakai satu angka gaya per gerakan dari pendataan + hitungan kamera. **[Bersumber]**
- Tingkat gaya setiap gerakan = angka gaya dari formulir pendataan ÷ FmaxM jari yang dipakai. Gerakan ringan (beberapa gram) akan otomatis jatuh di tingkat rendah, sesuai contoh formulir "insertion of small parts / material guidance" (formulir hlm. 2). **[Bersumber (contoh)]**

| Tingkat (FmaxM) | Tahan 31–60 s/min | 16–30 | ≤ 15 | Gerak < 5 /min | 5–15 | 16–30 | 31–60 | 61–90 |
|---|---|---|---|---|---|---|---|---|
| Rendah (≤ 15%) | 5,5 | 3 | 1,5 | 0,5 | 1 | 2,5 | 5 | 7 |
| Sedang (≤ 30%) | 9 | 4,5 | 2,5 | 0,5 | 2 | 4 | 7,5 | 11 |
| Tinggi (≤ 50%) | 14 | 7 | 3,5 | 1 | 3 | 6 | 12 | 18 |
| Sangat tinggi (≤ 80%) | 22 | 11 | 5,5 | 1,5 | 5 | 10 | 19 | abu-abu = 100 |
| Puncak (> 80%) | 100 (abu-abu, gabungan 16–60) | ← | 35 | 8 | 30 | 100 (abu-abu, gabungan 16–90) | ← | ← |
| Memukul (pangkal ibu jari, telapak, kepalan) | diarsir (tidak berlaku) | ← | ← | 8 | 30 | abu-abu = 100 | ← | ← |

Status: **Bersumber**, dibaca dari gambar formulir PDF hlm. 2 (14 Nov) dan dicocokkan dengan entri kedua (15 Nov, `sources/transcription/kim_form_entry2.yaml`). Sel abu-abu = 100 poin (A55 cetak hlm. 28, "graue Felder"); untuk "sangat tinggi 61–90" dan "memukul 16–90" sel tidak bertuliskan angka sendiri → **Sebagian**. Catatan formulir: tahan ≥ 4 detik (catatan 1); bila memilih puncak/memukul, nilai juga dengan KIM-BF (catatan 2); frekuensi > 90/menit diekstrapolasi linear atau memakai KIM-MHO-E (catatan 3). Di kode: sel abu-abu = 100 + peringatan; sel diarsir = `null` → error.

### 3.3a FmaxM (ditetapkan 14 Nov; dikunci sebelum data peserta dianalisis)

FmaxM adalah penyebut yang mengubah newton menjadi persen. Definisinya: gaya aksi maksimal rata-rata **pria** dalam keadaan segar, berbeda per jenis pegangan (A55 cetak hlm. 14). BAuA sengaja tidak memberi angka newton dan tidak membedakan jenis kelamin (hlm. 15). Angka di bawah dicek lewat laporan riset 14 Nov ("Patokan FmaxM untuk Dorong Ibu Jari").

| Pegangan | FmaxM | Dasar | Status |
|---|---|---|---|
| **Dorong ibu jari** (utama) | **80 N** | Lo dkk. 2019 (IJERPH 16:4742) dan Lo dkk. 2021 (IJERPH 18:187) Tab. 5: pria pekerja manufaktur Taiwan, thumb press kanan 8,2 kgw. Alat dan protokol mirip kita (load cell, tekan ke bawah, rata-rata 3 detik) | Bersumber (via laporan riset; buka PDF sebelum dikunci) |
| Dorong telunjuk | **50 N** | BAuA *Manuelle Arbeit ohne Schaden* (2011) hlm. 9: Druckkraft mit Zeigefinger 50 N; Di Domenico & Nussbaum 2003 Tab. 2 hlm. 1537: pria duduk 50,9 N | Bersumber (via laporan riset) |

Contoh: tekan 30 N dengan ibu jari = 38% → **tinggi**; dengan telunjuk = 60% → **sangat tinggi**. Karena itu jari yang menekan dicatat kamera (Tahap 10).

Catatan kritis: (1) Lo memakai posisi **berdiri**, sedangkan tugas kita duduk; menurut BAuA gaya ke depan lebih kecil saat duduk, jadi 80 N cenderung membuat risiko sedikit **terlalu rendah**. (2) Angka 8,2 kgw kemungkinan rata-rata hasil transformasi log (geometrik), sehingga rata-rata biasa bisa ±85–90 N (Asumsi). (3) Angka lama "5,7 kgf" ternyata data **pekerja kesehatan**, bukan pekerja perakitan; sekarang dipakai sebagai skenario bawah.

Skenario P4 (ibu jari, tekan 30 N):

| Skenario | FmaxM | 30 N = | Tingkat | Dasar |
|---|---|---|---|---|
| Bawah | 56 N | 54% | Sangat tinggi | Lo 2021, pria kesehatan Taiwan |
| BAuA konservatif | 70 N | 43% | Tinggi | BAuA 2011 hlm. 9 (≈ 85% pekerja mampu, bukan rata-rata) |
| **Utama** | **80 N** | **38%** | **Tinggi** | Lo 2019/2021, pria manufaktur Taiwan |
| Atas | 137 N | 22% | Sedang | Choi dkk. 2020, pria Korea (mahasiswa, berdiri) |

### 3.4 Indikator lain

| Indikator | Poin | Cara mengisi | Status |
|---|---|---|---|
| Pegangan / transfer gaya | 0 / 2 / 4 | Dinilai sekali dari desain cover (sama untuk semua) | Bersumber (skala) |
| Posisi tangan/lengan | 0 / 1 / 2 / 3 | % waktu sendi di luar batas (§4) → kata waktu: < 5% = 0 · 5–< 25% = 1 · 25–< 75% = 2 · ≥ 75% = 3. **Sendi terburuk menentukan** | Bersumber (A55 cetak hlm. 24, 38–39) |
| Kondisi kerja | 0 / 1 / 2 | Lab: dinilai sekali | Bersumber (skala) |
| Postur badan | 0 / 2 / 4 / 6 | Dari video: condong badan, kepala, jangkauan > 17 cm dari dada | Bersumber (skala) |
| Organisasi kerja | 0 / 2 / 4 | Dari skenario | Bersumber (skala) |

- Interpolasi antar-kategori (misalnya 1,5) **diizinkan** (A55 cetak hlm. 39). Rumus resmi ada di *baua: Fokus – LMM-E: Algorithmen für Interpolation und Zusammenfassung*. **[Bersumber: ada; isi belum dibaca]**
- Versi 1 kalkulator memakai **fungsi tangga** (tanpa interpolasi). Interpolasi ditambahkan setelah dokumen LMM-E dibaca, sebagai opsi `interpolate: true`.
- Frekuensi dan detik tahan per menit memakai **nilai mentah, tanpa pembulatan**: "< 5" eksklusif (4,5 → "< 5", A55 cetak hlm. 34), kolom lain inklusif di batas atas, nilai di celah (15,5) masuk kolom berikutnya. **[Bersumber (4,5 dan 4,65) / Asumsi (15,5); disetujui pengguna 15 Nov, menggantikan keputusan "dibulatkan" pagi harinya]**
- **Poin waktu linear** (3,5 jam = 3,5; minimal 1) dan **sel abu-abu = 100 poin** (A55 cetak hlm. 23, 28, 47). **[Bersumber; disetujui pengguna 15 Nov]**

## 4. Sudut sendi dan batas (`src/kimcam/angles.py`, `configs/thresholds.yaml`)

### 4.1 Batas "ujung rentang gerak" (dari OCRA, dipakai sebagai kamus sudut)

| Sendi | Batas | Sumber | Status |
|---|---|---|---|
| Pergelangan fleksi / ekstensi | > 45° / > 45° | Occhipinti 2006 Tab. 3 (hlm. 4); BGIA 2007 Arbeitsbogen 8 (hlm. 18) | Bersumber |
| Pergelangan radial / ulnar | > 15° / > 20° (opsi: > 20° digabung, Occhipinti 2006) | BGIA 2007 hlm. 18 | Bersumber (pilihan belum final) |
| Lengan bawah pronasi / supinasi | > 60° / > 60° | Occhipinti 2006; BGIA 2007 | Bersumber |
| Siku fleksi–ekstensi | Gerak > 60° | Occhipinti 2006; BGIA 2007 | Bersumber (dipakai belakangan) |
| Bahu abduksi / fleksi / ekstensi | > 45° / > 70–80° / > 20° | BGIA 2007 hlm. 18 | Bersumber |

Pemetaan ini adalah **asumsi kita**: KIM hanya menulis "joints at the limit of the movement ranges" tanpa derajat (formulir hlm. 2). Pemetaan ini diuji di P4.

### 4.2 Titik tubuh (COCO-WholeBody 133 titik dari RTMW)

- Badan: 5/6 bahu kiri/kanan, 7/8 siku, 9/10 pergelangan, 11/12 pinggul.
- Tangan kiri 91–111, tangan kanan 112–132. Urutan lokal: 0 pergelangan, **4 ujung ibu jari**, 5 pangkal telunjuk (MCP2), **8 ujung telunjuk**, 9 pangkal jari tengah (MCP3), 17 pangkal kelingking (MCP5). Ujung jari dipakai untuk mendeteksi jari yang menekan (Tahap 10).

Status: **Sebagian**, cek di metadata rtmlib saat Tahap 8. Skor titik dari RTMW adalah nilai maksimum SimCC mentah, **bukan probabilitas 0–1** (dicek di kode rtmlib 0.0.16), jadi ambang skor disetel dari data.

### 4.3 Definisi sudut (terinspirasi ISB, Wu dkk. 2005; tanpa penanda anatomi)

```
y_f   = unit(wrist − elbow)                    # sumbu lengan bawah
y_h   = unit(MCP3 − wrist)                     # sumbu memanjang tangan
a_ru  = unit(MCP2 − MCP5)                      # arah radial (kelingking → telunjuk)
n_p   = unit(cross(a_ru, y_h))                 # normal telapak (tanda dibalik untuk tangan kiri)

FE    = signed_angle(y_f, y_h, axis=a_ru)      # + fleksi (ke arah telapak)
RUD   = signed_angle(y_f, y_h, axis=n_p)       # + radial
PS    = signed_angle(n_elbow, n_p, axis=y_f)   # n_elbow = unit(cross(upper_arm, y_f)); butuh siku > 20°
sudut_final = sudut − sudut_posisi_netral      # offset dari rekaman netral 2 detik
```

`signed_angle(a, b, axis)` = sudut dari proyeksi a ke proyeksi b pada bidang tegak lurus `axis`. Tanda (+/−) **wajib dicek dengan goniometer** di Tahap 9. Pronasi/supinasi adalah sudut paling lemah (markerless dilaporkan meleset > 30°, *Sensors* 2026, 26(19):6248). Bila galatnya > 10°, beri label "eksperimental". **[Asumsi + Sebagian]**

## 5. Alur data

```
Perangkat load cell terpisah ─► angka N per gerakan ─┐ (diketik)
                                                     ▼
record_session.py: formulir pendataan ─► meta.yaml (ID, gender, tangan, pengalaman, gaya per move)
                                      └► participants_private.csv (ID ↔ nama)
6 kamera (MJPG 30 fps) + timestamp per frame ─► record_session.py (15 menit) ─► data/raw/P001/S01/
Kalibrasi ChArUco (per hari) ─► calibration.toml

pose2d.py (RTMW, frame abu-abu → 3 kanal) ─► triang.py (aniposelib, fisheye) ─► filter 6 Hz
─► angles.py (FE, RUD, PS, siku, bahu, condong)
─► segment.py (siklus + aksi dari zona dan gerak tangan; jari yang menekan)
─► label per frame (move, tangan, jari, sendi di luar batas) + tingkat gaya dari meta.yaml ÷ FmaxM
─► kim.py (skor resmi) ─► attribution.py (P1) ─► whatif.py (P2) ─► profile.py (P3) ─► stability.py (P4)
─► data/results/P001/  (kartu hasil)
```

Catatan teknis:
- **Fisheye:** pose dijalankan di frame mentah. aniposelib meng-undistort titik secara internal saat triangulasi (`fisheye=True`). Jangan meng-undistort dua kali. **[Sebagian]**
- **Sinkron:** hanya **antar kamera** (timestamp `time.perf_counter_ns()` per frame + offset per kamera dari korelasi gerakan tangan antar kamera, Tahap 6; tanpa LED, keputusan pengguna 15 Nov). Frame dipasangkan berdasarkan timestamp, bukan nomor urut. Tidak ada sinkron kamera ↔ load cell. **[Usulan]**

### 5.1 Tata letak data

```
data/
  manifest.csv                       # path, ukuran, sha256, tanggal
  participants_private.csv           # ID ↔ nama; satu-satunya tempat nama; jangan dibagikan
  calib/2026-MM-DD/calibration.toml  # + video papan
  raw/P001/S01/  <label>.avi + <label>_ts.csv per kamera (front_left … wing_right), meta.yaml (data peserta tanpa nama + gaya per move)
  interim/P001/S01/  pose2d_C1.npz … , pose3d.npz, angles.parquet, labels.parquet
  results/P001/  kim.json, p1_attribution.csv, p2_whatif.csv, p3_profile.csv, card.md
```

## 6. Algoritma analisis

### 6.1 P1: pecah skor resmi (`attribution.py`)

1. Hitung skor resmi seperti biasa (§3).
2. **Gaya:** poin setiap baris tingkat gaya dibagi ke aksi sebanding jumlah kejadian aksi itu di baris tersebut, per tangan.
3. **Posisi tangan/lengan:** poin indikator dibagi ke (aksi × sendi × tangan) sebanding dengan waktu di luar batas yang disumbang masing-masing pada **sendi terburuk**.
4. Cek wajib: jumlah semua bagian = poin indikator resmi, dan total = skor resmi (toleransi 1e-9).

Aturan pembagian ini **buatan kita** (Asumsi). Alternatif yang lebih teoritis: nilai Shapley (skor dihitung untuk semua subset aksi yang "diperbaiki"). Dipertimbangkan setelah versi sederhana lulus uji jawaban-diketahui.

### 6.2 P2: bagaimana jika (`whatif.py`)

```
untuk setiap aksi a:
    label_baru = label dengan frame aksi a dibuat "di dalam batas"
                 (opsi gaya: tekan dengan ibu jari, bukan telunjuk; atau gaya tekan = gaya pasang minimum cover)
    delta[a] = skor_resmi(label) − skor_resmi(label_baru)
urutan = greedy: pilih delta terbesar, terapkan, hitung ulang, ulangi sampai delta = 0
```

Greedy dan hitung ulang wajib dilakukan karena aturan "sendi terburuk" dan "tangan tertinggi". Setelah satu perbaikan, penyumbang berikutnya bisa berpindah. **[Asumsi]**

### 6.3 P3: profil per orang (`profile.py`)

- Per siklus: % waktu di luar batas per (aksi × sendi × tangan), jari yang menekan, penyumbang terbesar. Gaya per gerakan **per orang** (bukan per siklus) dari formulir pendataan.
- Per orang: sebaran antar-siklus; "konsisten" bila penyumbang terbesar sama di ≥ 70% siklus (ambang Asumsi); kiri vs kanan.
- Antar orang (deskriptif saja): berapa orang punya penyumbang terbesar yang sama, dengan interval kepercayaan Wilson 95%.

### 6.4 P4: kestabilan (`stability.py`)

Monte Carlo (misalnya 1.000 kali). Setiap kali:
- tambahkan galat sudut tetap per sendi sesuai hasil goniometer (bias + SD per sendi; galat sistematis satu sesi);
- geser ambang tiap sendi ±5°;
- FmaxM ibu jari dari distribusi segitiga (min 56, modus 80, maks 137 N; §3.3a) (Asumsi);
- kalikan gaya tiap gerakan dengan faktor acak 0,9–1,1 (pengganti bootstrap 10 tekan; disetujui pengguna 15 Nov);
- geser label aksi ±3 frame terhadap sudut.

Karena itu label menyimpan sudut (`ang_<sendi>`), bukan hanya status di luar batas.

Ditambah tabel skenario tetap FmaxM 56 / 70 / 80 / 137 N.

Laporkan % simulasi yang menghasilkan (a) penyumbang terbesar yang sama dan (b) perbaikan nomor 1 yang sama. **[Usulan]**

## 7. Bukti kepercayaan (tanpa validasi ahli)

| Lapis | Yang dibuktikan | Kriteria lulus (usulan) |
|---|---|---|
| Akurasi sudut | Kamera vs goniometer di sekitar batas (FE 35–55°, RUD 10–25°, PS 50–70°) | Bias dan batas kesesuaian Bland–Altman dilaporkan; \|bias\| ≤ 5°, RMSE ≤ 10° (pronasi: label eksperimental bila gagal) |
| Akurasi gaya | Load cell (perangkat terpisah) vs beban kalibrasi | Galat ≤ 0,3 N di rentang 0–50 N |
| Akurasi hitungan | Jumlah tekan dan jari dari kamera vs hitungan manual (3 menit acak) | Selisih jumlah ≤ 2%; jari benar ≥ 95% (Asumsi) |
| Akurasi waktu | % waktu di luar batas vs anotasi manual | Selisih ≤ 5 poin persen |
| Aturan benar | Kalkulator vs kasus resmi A55 (jawaban BAuA); versi interpolasi nanti vs formulir LMM-MA-E | ≥ 10 kasus, selisih 0 poin (15 Nov: 12 kasus identik) |
| Jawaban diketahui | Peserta sengaja salah di satu aksi | P1 menunjuk aksi itu; P2 memulihkan skornya |
| Kestabilan (P4) | Kesimpulan tahan galat dan asumsi | Dilaporkan sebagai % (bukan lulus/gagal) |

Kenapa tidak membandingkan dengan ahli: ahli sendiri tidak sepakat untuk sudut pergelangan (Lowe 2004: ICC 0,12–0,34; Rhén & Forsman 2020: κw 0,43 OCRA Checklist). **[Sebagian]**

## 8. Risiko teknis dan mitigasi

| Risiko | Mitigasi | Tes cepat |
|---|---|---|
| Kamera ke-6 gagal dibuka (bandwidth USB 2.0) | Coba MSMF; maks. 2–3 kamera per controller; kartu PCIe USB | 6 kamera 60 s, fps ≥ 29,5 |
| Kamera tertukar setelah reboot | Seri kembar (`SN0001`) → dikenali dari alamat port USB fisik di `cameras.yaml` | Reboot, cocokkan label |
| Kabel kamera bertukar port | Label fisik di kabel dan port hub; jalankan ulang `identify_cameras.py` bila colokan berubah | Uji tutup lensa sebelum tiap sesi |
| onnxruntime-gpu tertimpa versi CPU | rtmlib `--no-deps` | `get_available_providers()` memuat CUDA |
| Dua paket OpenCV | Hanya `opencv-contrib-python` | `uv pip list` |
| Kalibrasi tidak stabil (aniposelib issue #121) | Ulang 3×, bandingkan; cek dengan caliscope | Reproyeksi < 0,5 px, posisi < 5 mm |
| Selisih waktu antar kamera | Offset per kamera dari korelasi gerakan tangan; cadangan: kedip senter HP atau FSIN | Offset stabil antar potongan 1 menit |
| Model pose dilatih gambar berwarna; kamera mono | Gray → BGR; cahaya cukup; cek visual | Tangan terdeteksi di `top` |
| Pronasi/supinasi tidak akurat | Goniometer; label eksperimental | RMSE ≤ 10° |
| HX711 masih 10 SPS (puncak snap tercatat terlalu kecil) | Potong jumper RATE | ±80 baris/detik; tes puncak 10 vs 80 SPS |
| Gaya berubah selama 15 menit (lelah/belajar) | **Tidak terdeteksi** (gaya hanya diukur sebelum rekaman). Dilaporkan sebagai keterbatasan | — |
| Salah ketik gaya di formulir | Formulir menolak angka kosong/negatif/bukan angka; tampilkan ringkasan dan minta konfirmasi sebelum rekam | Tes input salah di Tahap 5 |
| Kamera salah hitung tekan atau salah jari | Aturan zona + jarak ujung jari; anotasi manual | Selisih ≤ 2%; jari benar ≥ 95% |
| Pilihan FmaxM menggeser kategori | Dikunci sebelum analisis; skenario 56/70/80/137 N di P4 | Tabel skenario dilaporkan |
| Skor KIM salah | Uji regresi vs formulir BAuA | 10 kasus, selisih 0 |
| Disk penuh | ±8,5 GB per orang (diukur 15 Nov: 9,4 MB/s, adegan uji); data di D: (±446 GB) | `record_session.py` menolak bila < 40 GB |

## 9. Keputusan yang masih terbuka

| # | Keputusan | Pilihan | Kapan |
|---|---|---|---|
| 1 | Persetujuan dosen untuk arah baru | — | Sebelum Tahap 14 |
| 2 | Angka skenario poin waktu | ≥ 1 jam; usulan 4 jam | Sebelum Tahap 11 |
| 3 | Batas miring pergelangan | 15°/20° atau 20° gabungan | Setelah Tahap 9 |
| 4 | ~~Sumber FmaxM~~ | **Diputuskan 14 Nov:** ibu jari 80 N, telunjuk 50 N (§3.3a). Sisa tugas: buka PDF Lo 2019/2021 dan brosur BAuA 2011, cek mean aritmetik vs geometrik | Sebelum Tahap 11 |
| 5 | Jumlah, definisi, dan batas gerakan | Sementara `move_1`, `move_2`, … (usulan 4 untuk cover) | Rapat dosen berikutnya; final di Tahap 10 |
| 6 | Benda | Cover snap-fit atau gear (gaya pasang gear belum diukur) | Sebelum Tahap 14 |
| 7 | ~~Backend kamera~~ | **Diputuskan 15 Nov (data Tahap 3):** DSHOW. MSMF mengisi frame kosong dengan frame dobel (±3%) | — |
| 8 | Peran expert | Dihapus / profil acuan / penilai bonus | Sebelum Tahap 14 |
| 9 | Tes gaya maksimum (MVC) per orang | Ditunda; opsional untuk laporan tambahan | Sebelum Tahap 14 |
| 10 | ~~Load cell merekam selama 15 menit~~ | **Diputuskan 14 Nov:** tidak; load cell di perangkat terpisah | — |
| 11 | ~~Jumlah tekan kalibrasi~~ | **Diputuskan 14 Nov:** satu angka per gerakan, diukur sebelum rekaman. Sisa: cara menghitung angka itu di alat | Tahap 4 |

## 10. Referensi inti

- BAuA (2019). Formulir KIM-MHO v12.5, *Draft for practical testing*. https://www.baua.de/EN/Topics/Work-design/Physical-workload/Key-indicator-method/Key-indicator-method_node.html (hlm. 1, 2, 4). **Bersumber**
- BAuA. A55 *Manuelle Arbeitsprozesse – Gefährdungsbeurteilung mit der Leitmerkmalmethode*; formulir di https://www.baua.de/lmm (cetak hlm. 13, 14, 15, 22, 24, 25, 26, 30, 31, 38, 39). **Bersumber**
- Steinberg U., Liebers F., Klußmann A. (2011). *Manuelle Arbeit ohne Schaden*, BAuA, hlm. 9 (Druckkraft mit Daumen 70 N, Zeigefinger 50 N). https://d-nb.info/1016425066/34. **Bersumber (via laporan riset)**
- BAuA (2020a). *baua: Fokus – LMM-E: Algorithmen für Interpolation und Zusammenfassung*. https://www.baua.de/DE/Angebote/Publikationen/Fokus/Algorithmen-Leitmerkmalmethoden.pdf. **Sebagian**
- BAuA. Formblatt LMM-MA-E (PDF dengan fungsi hitung). https://www.baua.de/formblatt-lmm-ma-e. **Sebagian**
- Klussmann A. dkk. (2017). *BMC Musculoskelet Disord* 18:184. doi:10.1186/s12891-017-1542-0. **Bersumber**
- ISO 11228-3:2026 (contoh dokumen): §4.2.1 hlm. 5, §4.2.3, A.1.3, A.1.11, A.2. https://www.iso.org/standard/11228-3. **Bersumber**
- Occhipinti E. (2006). *International standards on repetitive actions at high frequency* (IEA). https://www.premus2004.ethz.ch/Vorlesungen/Beweg/Literatur_06-07/13-occhipinti_IEA06_OCRA.pdf (Tab. 3 hlm. 4). **Bersumber**
- BGIA-Report 2/2007. *OCRA-Index und OCRA-Checkliste*. https://presse.dguv.de/medien/ifa/de/pub/rep/pdf/rep07/biar0207/ocra1.pdf (Arbeitsbogen 8 hlm. 18). **Bersumber**
- Wu G. dkk. (2005). ISB recommendation, Part II. *J Biomech* 38(5):981–992. https://pubmed.ncbi.nlm.nih.gov/15844264/. **Sebagian**
- aniposelib 0.8.0: https://github.com/lambdaloop/aniposelib · rtmlib 0.0.16: https://github.com/Tau-J/rtmlib · onnxruntime CUDA EP: https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html · cv2_enumerate_cameras: https://github.com/lukehugh/cv2_enumerate_cameras · InnoMaker U20CAM-9281M: https://github.com/INNO-MAKER/U20CAM-9281M · caliscope: https://github.com/mprib/caliscope. **Sebagian**
- Pagnon dkk. (2022). *Sensors* 22(7):2712 (Pose2Sim mengunci rotasi pergelangan). *Sensors* (2026) 26(19):6248 (galat pronasi markerless). **Sebagian**
- Lo V.E.-W., Chao S.-M., Tu H.-H. (2021, terbit online 29 Des 2020). Normative Hand Strength of Healthcare Industry Workers in Central Taiwan. *IJERPH* 18(1):187, Tab. 5. https://doi.org/10.3390/ijerph18010187. **Bersumber (via laporan riset)**
- Lo V.E.-W. dkk. (2019). A Pilot Study of Five Types of Maximum Hand Strength among Manufacturing Industry Workers in Taiwan. *IJERPH* 16(23):4742. https://doi.org/10.3390/ijerph16234742. **Bersumber (via laporan riset)**
- Di Domenico A., Nussbaum M.A. (2003). Measurement and prediction of single and multi-digit finger strength. *Ergonomics* 46(15):1531–1548, Tab. 2 hlm. 1537. https://doi.org/10.1080/0014013032000121660. **Bersumber (via laporan riset)**
- Choi J. dkk. (2020). Gender-Based Differences in Actual Thumb Force Exertions at Various Target Force Levels. *Applied Sciences* 10(1):194. https://doi.org/10.3390/app10010194. **Bersumber (angka) / Sebagian (postur)**
- Camargo Salinas M.A., Suárez-Pérez J.F. dkk. (2026). *Development and Validation of OCRA-AI*. SSRN 7524739. **Bersumber**
- Claude Code docs (CLAUDE.md, skills): https://code.claude.com/docs/en/memory · ponytail: https://github.com/dietrichgebert/ponytail. **Sebagian**
