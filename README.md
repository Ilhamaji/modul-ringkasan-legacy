
# Modul Ekstraksi dan Ringkasan Dokumen Otomatis (Groq API & PyMuPDF)

Modul Python ini dirancang untuk mengunduh, mengekstrak, dan meringkas naskah dokumen akademis (jurnal ilmiah atau materi pembelajaran) dari sebuah URL web secara otomatis. Evaluasi performa sistem juga diintegrasikan untuk mengukur latensi dan akurasi ekstraksi teks guna kebutuhan pengujian performa model machine learning.

---

## 🚀 Fitur Utama

* **Deteksi & Unduh PDF Otomatis:** Melakukan parsing HTML untuk menemukan tautan unduhan file PDF dari URL artikel jurnal (mendukung pola Open Journal Systems / OJS).
* **Ekstraksi Teks Cerdas (PyMuPDF):** Mengekstrak teks dari file PDF dan memisahkan konten naskah utama dari bagian daftar pustaka secara otomatis menggunakan ekspresi reguler (Regex).
* **Ringkasan Mendalam (Groq API):** Memanfaatkan model LLM `llama-3.3-70b-versatile` untuk menghasilkan ringkasan terstruktur dalam Bahasa Indonesia yang baku dan mengalir natural.
* **Modul Evaluasi Skripsi:** Menyediakan fungsi pengujian otomatis untuk mengukur durasi latensi (*system latency*), kepatuhan format hasil (*regex parsing rate*), serta perhitungan tingkat kemiripan judul dan penulis menggunakan algoritma *SequenceMatcher*.

---

## 🛠️ Prasyarat & Instalasi

Pastikan Anda telah memasang Python 3.10 atau versi yang lebih baru di lingkungan kerja Anda.

### 1. Instalasi Package Dependensi
Pasang seluruh pustaka eksternal yang dibutuhkan melalui terminal:
```bash
pip install -r requirements.txt

```

### 2. Konfigurasi Environment Variables

Modul ini membutuhkan API Key dari Groq. Buat sebuah file bernama `.env` di direktori akar proyek Anda dan tambahkan baris berikut:

```env
GROQ_API_KEY=tp_gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

> ⚠️ **Catatan Lingkungan Kerja:** > Jika dijalankan di dalam **Google Colab**, simpan API Key Anda pada menu **Secrets** (ikon gembok di panel kiri) dengan nama kunci `GROQ_API_KEY`, lalu aktifkan akses notebook ke kunci tersebut.

---

## 💻 Struktur Output Ringkasan

Hasil pemrosesan akhir dari Groq API akan di-parsing ke dalam bentuk objek *dictionary* dengan struktur sebagai berikut:

* **judul:** Identitas atau judul lengkap dokumen/artikel.
* **author:** Nama penulis dari dokumen asli.
* **kompetensi:** Fokus utama masalah, tujuan penelitian, atau target kompetensi materi.
* **isi_materi:** Pembahasan pokok, konsep dasar, atau metodologi yang digunakan.
* **temuan:** Fakta penting, data riset, rumus, atau inti sari pembahasan.
* **kesimpulan:** Kesimpulan menyeluruh yang ditulis dalam format **paragraf utuh** (naratif).
* **daftar_pustaka:** Daftar referensi utama yang valid dari dokumen asli.

---

## 📈 Modul Pengujian (Evaluasi Performa)

Modul ini menyediakan fungsi `evaluate_modul()` yang berguna untuk pengujian sistem pada Bab IV (Hasil dan Pembahasan) tugas akhir Anda. Metrik yang dihasilkan meliputi:

1. **Latency (Detik):** Kecepatan waktu respon sistem dari proses pengunduhan hingga inferensi selesai.
2. **Regex Parsing Success (Boolean):** Mengukur tingkat keberhasilan sistem dalam mengisi seluruh field tanpa adanya struktur output yang kosong.
3. **Similarity Score (%):** Tingkat kecocokan teks hasil generasi terhadap data *ground truth* (manual) untuk atribut Judul dan Penulis.

### Cara Menjalankan Skrip Pengujian

Anda dapat langsung mengeksekusi skrip utama untuk melihat simulasi pengujian pada terminal:

```bash
python main.py


```

```
