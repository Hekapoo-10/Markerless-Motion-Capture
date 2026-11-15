// TES 2: kalibrasi dengan beban yang diketahui, lalu tampilkan gaya dalam Newton
// Sambungan: HX711 DT -> D3, SCK -> D2, VCC -> 5V, GND -> GND
// Serial Monitor: 115200 baud, akhir baris "Newline".
// Ketik huruf z lalu Enter kapan saja untuk menolkan ulang (pelat harus kosong).

#include "HX711.h"

const int PIN_DT  = 3;
const int PIN_SCK = 2;

HX711 scale;
long titikNol = 0;        // angka mentah saat pelat kosong
float angkaPerNewton = 0; // hasil kalibrasi. Setelah tahu angkanya, isi di sini supaya tidak perlu kalibrasi ulang

// rata-rata beberapa bacaan supaya lebih stabil
long rataRata(int n) {
  long total = 0;
  for (int i = 0; i < n; i++) {
    while (!scale.is_ready()) { }
    total += scale.read();
  }
  return total / n;
}

void setup() {
  Serial.begin(115200);
  scale.begin(PIN_DT, PIN_SCK);

  Serial.println("Kosongkan pelat atas. Mengukur titik nol dalam 3 detik...");
  delay(3000);
  titikNol = rataRata(40);
  Serial.print("Titik nol = ");
  Serial.println(titikNol);

  if (angkaPerNewton == 0) {
    Serial.println("Taruh beban yang beratnya diketahui di tengah pelat.");
    Serial.println("Lalu ketik beratnya dalam GRAM (contoh: 1000) dan tekan Enter.");
    while (Serial.available() == 0) { }
    float gram = Serial.parseFloat();
    delay(2000);                       // tunggu beban diam
    long denganBeban = rataRata(40);
    float newton = gram / 1000.0 * 9.80665;
    angkaPerNewton = (denganBeban - titikNol) / newton;
    Serial.print("angkaPerNewton = ");
    Serial.println(angkaPerNewton, 3);
    Serial.println("CATAT angka di atas. Angkat bebannya. Mulai membaca gaya dalam 5 detik...");
    delay(5000);
  }
}

void loop() {
  // ketik z + Enter untuk menolkan ulang
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'z' || c == 'Z') {
      titikNol = rataRata(40);
    }
  }

  if (scale.is_ready()) {
    long mentah = scale.read();
    float gaya = (mentah - titikNol) / angkaPerNewton;  // dalam Newton
    Serial.println(gaya, 2);   // satu angka per baris -> bisa dilihat sebagai grafik di Serial Plotter
  }
}
