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
pip install -r requirements.txt

###2) Jalankan Streamlit
streamlit run app.py

🧭 Cara Pakai (Step-by-step)
1) Pilih Scenario (Sidebar)
Misal: Mahasiswa / Desainer / Gamer
Kamu juga bisa:
Add (buat skenario baru)
Copy (duplikat skenario)
Reset (balik default)
Del (hapus skenario)
2) Setup
Menu: ⚙️ Setup
Tambah / hapus / urutkan Kriteria
Tambah / hapus / urutkan Alternatif Laptop (misal: ASUS Vivobook 14, Samsung Galaxy Book 4, Lenovo IdeaPad, dll)
Catatan: kalau kriteria/alternatif berubah, ukuran matriks akan disesuaikan.
3) Isi Matriks Kriteria
Menu: 📌 Kriteria (Matrix Editor)
Isi nilai perbandingan kriteria (segitiga atas).
Contoh:
Jika Performa lebih penting dari Harga → isi nilai 3 atau 5 (sesuai kekuatan).
Akan muncul:
bobot kriteria
λmax, CI, CR
status konsistensi (OK/jelek)
4) Isi Matriks Alternatif per Kriteria
Menu: 💻 Alternatif per Kriteria (Matrix Editor)
Pilih kriteria (misal Performa)
Bandingkan laptop-laptop satu sama lain untuk kriteria tersebut.
5) Cek Heatmap & Konflik (kalau CR jelek)
Menu: 🔥 Heatmap & Konflik
Heatmap membantu lihat nilai besar/kecil
Tabel konflik menunjukkan pasangan yang paling bikin input tidak konsisten → perbaiki nilai itu.
6) Lihat Hasil Ranking
Menu: 📊 Hasil & Compare Scenario
Ranking laptop (skor AHP)
breakdown kontribusi per kriteria
compare antar skenario
7) Export PDF
Menu: 📄 Report PDF
klik generate → download PDF

8) Save/Load Project
Menu: 📦 Import/Export
Download JSON project
Upload JSON untuk lanjut kerja

🧮 Skala Saaty (1–9)
Nilai pairwise artinya:
1 = sama penting
3 = sedikit lebih penting
5 = lebih penting
7 = sangat penting
9 = mutlak lebih penting
(2,4,6,8 nilai tengah)

🗂 Struktur Folder (Umum)
ahp-laptop/
├─ app.py
├─ requirements.txt
└─ src/
   ├─ ahp.py
   ├─ compute.py
   ├─ matrix_ui.py
   ├─ state.py
   ├─ styles.py
   ├─ specs_state.py
   ├─ criteria_meta.py
   └─ pages/
      ├─ home.py
      ├─ methodology.py
      ├─ setup.py
      ├─ criteria_editor.py
      ├─ alt_editor.py
      ├─ quick_input.py
      ├─ data_specs.py
      ├─ heatmap_conflict.py
      ├─ results_compare.py
      ├─ report_pdf.py
      └─ import_export.py

🛠 Troubleshooting
1) ModuleNotFoundError: reportlab
pip install reportlab
2) CR aneh / minus nol (-0.0000)
Itu efek floating point, anggap saja 0.0000.
3) CR jelek (lebih dari 0.10)
buka menu Heatmap & Konflik
perbaiki pasangan nilai yang paling konflik
