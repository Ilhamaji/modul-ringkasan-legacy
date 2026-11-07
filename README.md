<div align="center">

# Modul Ringkasan — Legacy (ARCHIVED)

> ⚠️ **Repo ini sudah diarsipkan.** Kode di sini **identik** dengan versi lama dan telah digantikan oleh
> **[`groq-article-summarizer`](https://github.com/Ilhamaji/groq-article-summarizer)** yang lebih baru.
> Gunakan repo tersebut untuk versi terbaru.

[![Status](https://img.shields.io/badge/status-archived-lightgrey?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)

</div>

---

## Kenapa Diarsipkan

Repo ini adalah salinan awal modul peringkasan yang dikembangkan untuk keperluan skripsi (Juli 2026). Versi yang lebih baru dan lebih lengkap dipindahkan ke **`groq-article-summarizer`** (September 2026).

Repo ini **tetap dibiarkan publik dan read-only** karena beberapa alasan:

1. **Riwayat skripsi** — menyimpan jejak versi yang dipakai saat pengujian.
2. **Script evaluasi** — berisi pengukuran latensi dan akurasi yang dirujuk di laporan.
3. **Sitasi** — agar tautan lama tidak mati.

## Pindah Ke Versi Terbaru

```bash
git clone https://github.com/Ilhamaji/groq-article-summarizer.git
```

Perbedaan utama di versi baru: dokumentasi lengkap, struktur kode lebih rapi, dan penanganan error yang lebih baik. Fungsi intinya sama.

## Isi Repo

```
main.py            # pipeline peringkasan (identik dengan versi lama)
requirements.txt   # dependensi
```

## Menjalankan (jika masih diperlukan)

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_xxxxx"
python main.py
```

## Tech Stack

Python · Groq API (`llama-3.3-70b-versatile`) · PyMuPDF · BeautifulSoup4 · Regex

---

<div align="center">
Diarsipkan oleh <a href="https://github.com/Ilhamaji">Ilham Aji</a>
</div>
