# 📊 Dashboard Insight Kesehatan Finansial

Sebuah *dashboard* analitik interaktif berbasis web yang dibangun menggunakan **Streamlit**. Aplikasi ini dirancang untuk menganalisis perilaku pengelolaan keuangan individu, melacak kepatuhan anggaran, mengamati kebiasaan menabung, serta mengevaluasi tingkat kesehatan finansial secara menyeluruh melalui eksplorasi data (EDA) dan pengujian statistik inferensial (A/B Testing).

[🔗 **Live Demo: Dashboard Insight Kesehatan Finansial**](https://dashboard-capstone-kesehatan-finansial.streamlit.app/)

---

## ✨ Fitur Utama

### 1. Interactive Filtering (Sidebar)
- Filter dinamis berdasarkan rentang pendapatan (*Income*).
- Filter multi-pilihan untuk Tingkat Kesehatan Finansial (*Financial Level*), Status Saldo (*Surplus/Deficit*), dan Status Tabungan (*Savings Status*).
- Opsi untuk menampilkan/menyembunyikan tabel dataset mentah.

### 2. Key Performance Indicators (KPI)
Ringkasan metrik instan yang menampilkan Total Individu, jumlah kelompok *Surplus*, *Healthy*, anggaran *On Track*, dan *Healthy Savings* sesuai filter yang diterapkan.

### 3. Exploratory Data Analysis (EDA)
- **Kepatuhan Anggaran:** Distribusi rasio kepatuhan anggaran dan visualisasi kategori pengeluaran yang paling sering mengalami *Over Budget*.
- **Kebiasaan Menabung:** Visualisasi proporsi kelompok tabungan menggunakan *Bar Chart* beserta *insight* persentasenya.
- **Kondisi Finansial Keseluruhan:** Distribusi tingkat kesehatan dan status finansial (*Surplus/Deficit*) menggunakan *Pie Chart*.

### 4. Statistik Inferensial (A/B Testing)
- **T-Test (Independent):** Menguji perbedaan rata-rata pengeluaran hiburan (*Entertainment Expense*) antara kelompok Surplus dan Deficit.
- **Chi-Square Test:** Menganalisis hubungan signifikan antara status tabungan (*Savings Status*) dengan tingkat kebocoran kategori anggaran (*Category Leaks*).

---

## 🛠️ Teknologi yang Digunakan

- **Bahasa Pemrograman:** Python
- **Web Framework:** Streamlit
- **Manipulasi Data:** Pandas, NumPy
- **Visualisasi Data:** Matplotlib, Seaborn
- **Analisis Statistik:** SciPy

---

## 🚀 Cara Menjalankan Secara Lokal

Jika Anda ingin menjalankan *dashboard* ini di komputer Anda sendiri, ikuti langkah-langkah berikut:

**1. Clone Repository**

Buka terminal dan jalankan perintah berikut:
```
git clone https://github.com/RichardLiestianto/dashboard-capstone.git
cd dashboard-capstone
```
**2. Install Dependencies**

Pastikan Python sudah terinstal, lalu instal semua library yang dibutuhkan:
```
pip install -r requirements.txt
```

**3. Jalankan Aplikasi Streamlit**

Eksekusi file utama:
```
streamlit run dashboard.py
```
Aplikasi akan secara otomatis terbuka di browser Anda pada alamat http://localhost:8501.

📁 Struktur Direktori
```
dashboard-capstone/
│
├── dashboard/                               # Folder aplikasi Streamlit
│   ├── dashboard.py
│   └── urban_budget_allocation_dataset.csv
│
├── README.md                                    # Dokumentasi proyek
├── capstone.ipynb                               # Notebook
├── requirements.txt                             # Daftar library
├── urban_budget_allocation_dataset.json         # Data Dictionary
├── urban_budget_allocation_dataset_clean.csv    # Data bersih
├── urban_budget_allocation_dataset_dirty.csv    # Data kotor
└── url.txt                                      # Berisi link deploy
```
---

## 👤 Authors

* **Richard Liestianto** - [@RichardLiestianto](https://github.com/RichardLiestianto)
* **Thirza Elysia Chandra** - [@thirzaely](https://github.com/thirzaely)
