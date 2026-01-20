import streamlit as st


def render_methodology():
    st.title("📚 Metodologi (Cara Kerja Program AHP Laptop Comparator)")
    st.caption("Halaman ini menjelaskan logika & alur kerja aplikasi secara pelan-pelan agar kamu paham.")

    st.divider()

    # =========================
    # 1) Apa itu AHP
    # =========================
    st.header("1) Apa itu AHP?")
    st.write(
        """
AHP (Analytical Hierarchy Process) adalah metode pengambilan keputusan untuk memilih alternatif terbaik
berdasarkan beberapa kriteria.

AHP bekerja dengan **perbandingan berpasangan (pairwise comparison)**:
- Kita bandingkan 2 item sekaligus: *mana yang lebih penting / lebih baik*, dan seberapa kuat.
- Dari perbandingan itu, AHP menghitung **bobot** (prioritas) secara matematis.
        """
    )

    st.info(
        """
Di aplikasi ini:
- **Kriteria** = aspek penilaian (Harga, Performa, Baterai, Portabilitas, Layar, Garansi, dll)
- **Alternatif** = laptop yang akan dibandingkan (ASUS..., Lenovo..., HP..., dll)
- **Scenario** = konteks pengguna (Mahasiswa/Desainer/Gamer), karena bobot bisa beda-beda
        """
    )

    # =========================
    # 2) Struktur Hirarki
    # =========================
    st.header("2) Struktur Hirarki Keputusan")
    st.write(
        """
Aplikasi ini memakai struktur hirarki AHP seperti ini:

**Tujuan**
→ Pilih laptop terbaik

**Kriteria**
→ Harga, Performa, Baterai, Portabilitas, Layar, Garansi, dst.

**Alternatif**
→ Laptop 1, Laptop 2, Laptop 3, ...
        """
    )

    # =========================
    # 3) Pairwise: Skala Saaty
    # =========================
    st.header("3) Skala Perbandingan (Saaty 1–9)")
    st.write(
        """
Saat mengisi matriks, angka yang dipakai mengacu ke skala Saaty:

- **1** = sama penting / sama baik  
- **3** = sedikit lebih penting / lebih baik  
- **5** = lebih penting / lebih baik  
- **7** = sangat penting / sangat baik  
- **9** = ekstrim penting / ekstrim baik  
Nilai **2,4,6,8** = nilai tengah.

Kalau kamu isi A[i,j] = 5 artinya:
**item baris i lebih penting/bagus daripada item kolom j sebesar 5x.**

Dan aplikasi otomatis membuat kebalikannya:
A[j,i] = 1/5.
        """
    )

    # =========================
    # 4) Matriks Kriteria & Alternatif
    # =========================
    st.header("4) Dua Jenis Matriks yang Kamu Isi")
    st.subheader("A) Matriks Kriteria")
    st.write(
        """
Menu: **📌 Kriteria (Matrix Editor)**  
Di sini kamu membandingkan antar kriteria: misalnya *Harga vs Performa*, *Harga vs Baterai*, dst.

Outputnya:
- **Bobot Kriteria** (berapa besar pengaruh tiap kriteria)
- **CR Kriteria** (konsistensi penilaian kriteria)
        """
    )

    st.subheader("B) Matriks Alternatif per Kriteria")
    st.write(
        """
Menu: **💻 Alternatif per Kriteria (Matrix Editor)**  
Di sini kamu membandingkan laptop untuk **setiap** kriteria.
Contoh:
- Untuk kriteria Harga: ASUS vs Lenovo vs HP ...
- Untuk kriteria Performa: ASUS vs Lenovo vs HP ...
dst.

Outputnya:
- **Bobot Alternatif** untuk kriteria itu
- **CR Alternatif** untuk kriteria itu
        """
    )

    # =========================
    # 5) Hitung Bobot (cara aplikasi)
    # =========================
    st.header("5) Cara Aplikasi Menghitung Bobot")
    st.write(
        """
Aplikasi menghitung bobot menggunakan langkah umum AHP:
1) **Normalisasi matriks** (membagi setiap kolom dengan jumlah kolom)
2) **Rata-rata baris** dari matriks normalisasi → jadi bobot (priority vector)
3) Bobot dinormalisasi sehingga totalnya = 1

Hasilnya:
- `w_criteria` = bobot tiap kriteria
- `w_alt_per_criterion` = bobot tiap laptop untuk setiap kriteria
        """
    )

    # =========================
    # 6) Konsistensi (CR)
    # =========================
    st.header("6) Kenapa Ada Konsistensi (CR)?")
    st.write(
        """
Karena manusia kadang menilai tidak konsisten.

Contoh tidak konsisten:
- Kamu bilang A > B (3x)
- B > C (3x)
- Tapi kamu bilang A ≈ C (1x)  
Padahal seharusnya A > C juga (sekitar 9x).

AHP punya pengukuran konsistensi:
- **λmax (lambda max)**
- **CI (Consistency Index)**
- **CR (Consistency Ratio)**

Aturan umum:
- **CR ≤ 0.10** → konsisten (OK)
- **CR > 0.10** → tidak konsisten (perlu perbaikan)
        """
    )

    st.success("Di sidebar kamu bisa atur batas CR (default 0.10).")

    # =========================
    # 7) Heatmap & Konflik
    # =========================
    st.header("7) Heatmap & Indikator Konflik (Kenapa CR jelek?)")
    st.write(
        """
Menu: **🔥 Heatmap & Konflik**

Aplikasi menampilkan:
- **Heatmap** matriks → biar kelihatan pola nilai perbandingan
- **Top Konflik** → pasangan yang paling bikin inkonsisten

“Konflik” dihitung dari deviasi log antara:
- nilai perbandingan A[i,j]
- rasio bobot w_i / w_j

Semakin besar konflik → pasangan itu paling perlu kamu revisi.
        """
    )

    # =========================
    # 8) Menghasilkan Ranking Akhir
    # =========================
    st.header("8) Cara Aplikasi Membuat Ranking Laptop (Skor Akhir)")
    st.write(
        """
Skor akhir setiap laptop dihitung dengan menjumlahkan kontribusi dari semua kriteria:

**Skor(laptop i) = Σ ( BobotKriteria(k) × BobotLaptop(i pada kriteria k) )**

Hasilnya tampil di menu:
- **📊 Hasil & Compare Scenario**
        """
    )

    # =========================
    # 9) Multi Scenario
    # =========================
    st.header("9) Multi-Skenario (Mahasiswa / Desainer / Gamer)")
    st.write(
        """
Menu scenario ada di sidebar.

Tujuannya:
- Setiap scenario bisa punya **bobot kriteria berbeda**
- Kamu bisa bandingkan hasil ranking antar scenario

Contoh:
- Mahasiswa mungkin lebih berat ke Harga + Baterai
- Gamer lebih berat ke Performa + Layar
- Desainer berat ke Layar + Performa + Portabilitas
        """
    )

    # =========================
    # 10) Data Spesifikasi + Auto Pairwise (opsional)
    # =========================
    st.header("10) Data Spesifikasi + Auto Pairwise (opsional)")
    st.write(
        """
Menu: **🧾 Data Spesifikasi + Auto Pairwise**

Fitur ini untuk membantu kamu kalau capek isi matriks manual.
Kamu isi data angka seperti:
- Harga, RAM, SSD, CPU Score, Baterai, Berat, Garansi, dll.

Lalu nanti bisa dipakai untuk:
- membantu pengisian pairwise (semi otomatis),
- memperkaya tampilan perbandingan laptop,
- filtering seperti budget, min RAM, berat max, dsb.
        """
    )

    # =========================
    # 11) Import Export
    # =========================
    st.header("11) Import / Export Project")
    st.write(
        """
Menu: **📦 Import/Export**

Aplikasi bisa:
- Export semua data (kriteria, alternatif, semua scenario, semua matriks) ke JSON
- Import JSON untuk lanjutkan proyek tanpa hilang data
        """
    )

    # =========================
    # 12) Report PDF
    # =========================
    st.header("12) Report PDF Otomatis")
    st.write(
        """
Menu: **📄 Report PDF**

PDF berisi:
- Bobot kriteria + grafik
- Ranking laptop + grafik
- Konsistensi (CI/CR) untuk kriteria dan alternatif
        """
    )

    st.divider()
    st.subheader("✅ Alur Paling Mudah (Rekomendasi)")
    st.markdown(
        """
1. **⚙️ Setup** → isi kriteria & alternatif laptop  
2. **📌 Kriteria** → isi matriks kriteria (segitiga atas)  
3. **💻 Alternatif per Kriteria** → isi matriks alternatif tiap kriteria  
4. **🔥 Heatmap & Konflik** → perbaiki kalau CR jelek  
5. **📊 Hasil & Compare Scenario** → lihat ranking  
6. **📄 Report PDF** → download laporan  
        """
    )

    st.info("Kalau kamu bingung nilai pairwise, mulai dulu dari nilai sederhana: 1, 3, 5. Jangan terlalu ekstrem.")
