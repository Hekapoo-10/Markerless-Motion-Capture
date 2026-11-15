// TES REAL-TIME: lihat bacaan load cell dengan rapi
// Sambungan: HX711 DT -> D3, SCK -> D2, VCC -> 5V, GND -> GND
// Kecepatan Serial: 115200 baud.
// MODE 1 = teks rapi di Serial Monitor, MODE 2 = grafik di Serial Plotter.
// Ketik z lalu Enter (Serial Monitor) untuk menolkan ulang, load cell jangan disentuh.

#include "HX711.h"

const int PIN_DT  = 3;
const int PIN_SCK = 2;

const int   MODE = 1;               // 1 = teks rapi, 2 = grafik
const float ANGKA_PER_NEWTON = 0;   // isi dari hasil Tes 2 kalau sudah kalibrasi (0 = belum)
const long  SKALA_BAR = 2000;       // 1 tanda # = sekian angka mentah
const long  BATAS_MENTOK = 8388000; // mendekati batas HX711 (8388607)

HX711 scale;
long titikNol = 0;
long mentahTerakhir = 0;
int  sampelDetikIni = 0;
int  sampelPerDetik = 0;
bool adaData = false;
unsigned long waktuDetik = 0;
unsigned long waktuCetak = 0;

// cetak angka rata kanan supaya kolomnya lurus
void cetakRata(long nilai, int lebar) {
  char buf[12];
  ltoa(nilai, buf, 10);
  for (int i = strlen(buf); i < lebar; i++) Serial.print(' ');
  Serial.print(buf);
}

// rata-rata n bacaan; kembali 0 kalau HX711 tidak menjawab
long rataRata(int n) {
  long total = 0;
  for (int i = 0; i < n; i++) {
    unsigned long t = millis();
    while (!scale.is_ready()) {
      if (millis() - t > 500) return 0;
    }
    total += scale.read();
  }
  return total / n;
}

void cetakBaris() {
  long perubahan = mentahTerakhir - titikNol;

  Serial.print(F("Mentah:"));       cetakRata(mentahTerakhir, 9);
  Serial.print(F(" | Berubah:"));   cetakRata(perubahan, 9);
  if (ANGKA_PER_NEWTON != 0) {
    Serial.print(F(" | Gaya: "));
    Serial.print(perubahan / ANGKA_PER_NEWTON, 1);
    Serial.print(F(" N"));
  }
  Serial.print(F(" | Sampel/dtk:")); cetakRata(sampelPerDetik, 4);
  Serial.print(F(" | "));

  if (!adaData)                             Serial.print(F("TIDAK ADA DATA "));
  else if (sampelPerDetik > 100)            Serial.print(F("CEK KABEL DT   "));
  else if (mentahTerakhir >= BATAS_MENTOK)  Serial.print(F("MENTOK ATAS    "));
  else if (mentahTerakhir <= -BATAS_MENTOK) Serial.print(F("MENTOK BAWAH   "));
  else                                      Serial.print(F("OK             "));

  // bar sederhana: makin panjang = makin besar perubahan
  long kotak = labs(perubahan) / SKALA_BAR;
  if (kotak > 30) kotak = 30;
  Serial.print(perubahan < 0 ? '-' : '+');
  for (long i = 0; i < kotak; i++) Serial.print('#');
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  scale.begin(PIN_DT, PIN_SCK);
  delay(500);
  if (MODE == 1) {
    Serial.println(F("=== TES REAL-TIME LOAD CELL ==="));
    Serial.println(F("Jangan sentuh load cell. Mengukur titik nol..."));
  }
  titikNol = rataRata(20);
  if (MODE == 1) {
    Serial.print(F("Titik nol = "));
    Serial.println(titikNol);
    Serial.println(F("Ketik z + Enter untuk menolkan ulang."));
    Serial.println(F("--------------------------------------------------------------------------"));
  }
  waktuDetik = millis();
  waktuCetak = millis();
}

void loop() {
  // perintah: z = nolkan ulang
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'z' || c == 'Z') {
      titikNol = rataRata(20);
      if (MODE == 1) Serial.println(F(">>> Dinolkan ulang"));
    }
  }

  // baca HX711 setiap kali ada data baru
  if (scale.is_ready()) {
    mentahTerakhir = scale.read();
    adaData = true;
    sampelDetikIni++;
    if (MODE == 2) {
      long perubahan = mentahTerakhir - titikNol;
      Serial.print(F("Nol:0,"));
      if (ANGKA_PER_NEWTON != 0) {
        Serial.print(F("Gaya_N:"));
        Serial.println(perubahan / ANGKA_PER_NEWTON, 2);
      } else {
        Serial.print(F("Berubah:"));
        Serial.println(perubahan);
      }
    }
  }

  // hitung sampel per detik
  if (millis() - waktuDetik >= 1000) {
    sampelPerDetik = sampelDetikIni;
    sampelDetikIni = 0;
    waktuDetik = millis();
    if (sampelPerDetik == 0) adaData = false;
  }

  // tampilkan satu baris rapi 5x per detik
  if (MODE == 1 && millis() - waktuCetak >= 200) {
    waktuCetak = millis();
    cetakBaris();
  }
}
