# 🧠 AHP Laptop Comparator PRO (Streamlit)

Aplikasi web berbasis **Streamlit** untuk **membandingkan & memilih laptop terbaik** menggunakan metode **AHP (Analytic Hierarchy Process)**.  
Kamu bisa input pairwise matrix manual (tabel), pakai **Quick Input (sliders)** biar cepat, atau gunakan **Data Spesifikasi** untuk bantu auto-pairwise & ranking lebih realistis.

---

## ✨ Fitur Utama

✅ **Multi-skenario** (Mahasiswa / Desainer / Gamer + custom)  
Setiap skenario punya bobot & matriks sendiri.

✅ **Input Matriks (Tabel) + Auto Reciprocal**  
Isi hanya segitiga atas (upper triangle), diagonal otomatis `1`, bagian bawah otomatis `1/value`.

✅ **Quick Input (Sliders)**  
Input pairwise lebih cepat pakai:
- pilih pemenang (A / Sama / B)
- pilih kekuatan (1–9) skala Saaty

✅ **Heatmap Matriks + Deteksi Konflik Konsistensi**  
Visual heatmap matriks + tabel “pasangan paling konflik” untuk bantu perbaiki CR.

✅ **Hasil Ranking + Compare Scenario**  
Lihat ranking akhir tiap skenario & perbandingan antar skenario.

✅ **Report PDF Otomatis**  
Generate PDF berisi:
- bobot kriteria
- ranking akhir
- grafik
- nilai CI/CR

✅ **Import/Export Project (JSON)**  
Simpan/lanjutkan project tanpa ulang input.

✅ (Opsional Upgrade) **Data Spesifikasi Laptop**
Masukkan data laptop (harga, RAM, SSD, baterai, berat, dll) untuk perbandingan lebih nyata.

---

## 📌 Konsep Dasar AHP (Singkat)

AHP bekerja dengan **perbandingan berpasangan (pairwise comparison)**.

1) Kamu bandingkan **Kriteria vs Kriteria** → menghasilkan **bobot kriteria**  
2) Kamu bandingkan **Alternatif vs Alternatif** untuk tiap kriteria → menghasilkan bobot alternatif per kriteria  
3) Skor akhir laptop = ∑ (bobot kriteria × bobot alternatif)

AHP juga menghitung konsistensi input:
- **CI (Consistency Index)**
- **CR (Consistency Ratio)**  
Biasanya **CR ≤ 0.10** dianggap konsisten.

---

## 🚀 Cara Menjalankan

### 1) Install dependency
```bash
pip install -r requirements.txt

###2) Jalankan Streamlit
'''bash
streamlit run app.py
