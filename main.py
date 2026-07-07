import os
import re
import time  # Ditambahkan untuk menghitung latensi sistem
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from difflib import SequenceMatcher
from dotenv import load_dotenv
from google.colab import userdata # Import userdata dari google.colab

load_dotenv()

# KONFIGURASI GROQ API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = userdata.get('GROQ_API_KEY') # Mengambil API key dari Google Colab Secrets
MODEL_NAME = "llama-3.3-70b-versatile"


# HELPER: DETEKSI URL PDF
def _find_pdf_url(article_url: str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    if "/article/view/" in article_url:
        download_url = article_url.replace("/article/view/", "/article/download/")
        try:
            test = requests.get(download_url, headers=headers, timeout=10, stream=True)
            if "application/pdf" in test.headers.get("Content-Type", ""):
                return download_url
        except Exception:
            pass

    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        # Jika URL langsung mengarah ke PDF
        if "application/pdf" in response.headers.get("Content-Type", ""):
            return article_url
        # Jika bukan PDF, lakukan parsing HTML untuk mencari link PDF
        soup = BeautifulSoup(response.text, "html.parser")

        pdf_tag = soup.find("a", class_="pdf")
        if pdf_tag and pdf_tag.get("href"):
            href = pdf_tag["href"]
            if not href.startswith("http"):
                href = urljoin(article_url, href)
            return href.replace("/article/view/", "/article/download/") if "/article/view/" in href else href

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if any(kw in href.lower() for kw in [".pdf", "/pdf", "download", "fulltext"]):
                if not href.startswith("http"):
                    href = urljoin(article_url, href)
                return href

    except Exception:
        return None

    return None


# HELPER: EKSTRAKSI TEKS DARI PDF
def _extract_text_from_pdf(pdf_url: str) -> tuple[str, str]:
    headers = {
        "User-Agent": "Mozilla/500 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(pdf_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Gagal mengunduh PDF: {str(e)}")

    if "application/pdf" not in response.headers.get("Content-Type", ""):
        raise ValueError("URL tidak mengembalikan file PDF yang valid")

    doc = fitz.open(stream=response.content, filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    doc.close()

    # Memisahkan naskah utama dengan daftar pustaka asli dokumen
    split_pattern = r'\b(daftar pustaka|daftar referensi|references|bibliografi|bibliography)\b'
    parts = re.split(split_pattern, text, flags=re.IGNORECASE)

    main_text = parts[0]
    raw_bibliography = ""
    if len(parts) > 2:
        raw_bibliography = "".join(parts[2:])

    # Pembersihan teks utama
    main_text = re.sub(r'\n+', ' ', main_text)
    main_text = re.sub(r'\s+', ' ', main_text).strip()

    words = main_text.split()
    main_text = " ".join(words[:3000])

    lines = [line for line in main_text.split('. ') if len(line) > 40]
    main_text = '. '.join(lines)

    # Pembersihan teks daftar pustaka kasar (dibatasi agar tidak over-token)
    raw_bibliography = re.sub(r'\n+', ' ', raw_bibliography)
    raw_bibliography = re.sub(r'\s+', ' ', raw_bibliography).strip()
    bib_words = raw_bibliography.split()
    raw_bibliography = " ".join(bib_words[:500]) # Mengambil sekitar 500 kata pertama dari referensi

    return main_text, raw_bibliography


# HELPER: PARSING HASIL RINGKASAN MENJADI BBRP BAGIAN
def _parse_summary(raw: str) -> dict:
    result = {
        "judul": "",
        "author": "",
        "kompetensi": "",
        "isi_materi": "",
        "temuan": "",
        "kesimpulan": "",
        "daftar_pustaka": ""  # Field baru ditambahkan
    }

    patterns = {
        "judul": r"(?:Judul|Identitas Dokumen):\s*(.*?)(?=Author|Penulis|Kompetensi Utama|$)",
        "author": r"(?:Author|Penulis):\s*(.*?)(?=Kompetensi Utama|$)",
        "kompetensi": r"Kompetensi Utama\s*/\s*Tujuan:\s*(.*?)(?=Isi Materi|$)",
        "isi_materi": r"Isi Materi & Metodologi:\s*(.*?)(?=Inti Pembahasan|$)",
        "temuan": r"Inti Pembahasan & Temuan:\s*(.*?)(?=Kesimpulan|$)",
        "kesimpulan": r"Kesimpulan Keseluruhan:\s*(.*?)(?=Daftar Pustaka|$)",
        "daftar_pustaka": r"Daftar Pustaka:\s*(.*?)$"  # Pola baru ditambahkan
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()

    return result


# CORE: RINGKASAN MENGGUNAKAN GROQ API
def summarize(text: str, raw_bibliography: str = "") -> dict:
    if not text.strip():
        return {}

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables atau Colab Secrets")

    prompt = (
        "Bertindaklah sebagai penulis materi ajar, pakar pendidik, dan asisten peneliti senior. "
        "Tugas Anda adalah menyusun ringkasan yang mendalam, informatif, detail, "
        "dan mudah dipahami dari naskah dokumen yang diberikan.\n"
        "Dokumen ini bisa berupa jurnal ilmiah ataupun materi pembelajaran sekolah.\n"
        "Meskipun naskah asli menggunakan Bahasa Inggris atau bahasa asing lainnya, "
        "Anda WAJIB menuliskan seluruh hasil ringkasan dalam Bahasa Indonesia yang "
        "baku, formal, dan mengalir natural.\n\n"
        "PERATURAN KETAT:\n"
        "1. Bagian Kesimpulan wajib ditulis dalam bentuk PARAGRAF padat (bukan poin-poin).\n"
        "2. Tuliskan kembali daftar pustaka atau referensi penting yang relevan berdasarkan data yang disediakan "
        "di bagian akhir dengan format yang rapi dan teratur.\n\n"
        "Contoh Format output yang digunakan seperti berikut (sesuaikan dengan dokumen atau artikel):\n"
        "Judul: (judul)\n"
        "Author: (nama penulis/author dari dokumen/artikel)\n"
        "Kompetensi Utama / Tujuan: (fokus masalah, tujuan penelitian, atau target kompetensi)\n"
        "Isi Materi & Metodologi: (isi pembahasan pokok, konsep utama, atau metodologi)\n"
        "Inti Pembahasan & Temuan: (fakta penting, data, rumus, atau poin inti materi)\n"
        "Kesimpulan Keseluruhan: (PARAGRAF UTUH, naratif, mengalir, dan tuntas)\n"
        "Daftar Pustaka: (Tuliskan daftar referensi utama yang valid dari dokumen asli)\n\n"
        f"[TEKS NASKAH DOKUMEN]\n{text}\n\n"
        f"[TEKS DAFTAR PUSTAKA ASLI]\n{raw_bibliography if raw_bibliography else 'Tidak terdeteksi pada dokumen.'}"
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1200,  # Sedikit dinaikkan untuk mengakomodasi teks daftar pustaka
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        raw = data["choices"][0]["message"]["content"].strip()
        return _parse_summary(raw)
    except requests.exceptions.Timeout:
        raise ValueError("Request ke Groq API timeout")
    except requests.exceptions.RequestException as e:
        error_detail = ""
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.text
        raise ValueError(f"Koneksi gagal ke Groq API: {str(e)} | Detail: {error_detail}")
    except (KeyError, IndexError):
        raise ValueError("Response dari Groq API tidak valid")


# API UTAMA — dipanggil oleh router FastAPI
def summarize_from_url(article_url: str) -> dict:
    pdf_url = _find_pdf_url(article_url)
    if not pdf_url:
        raise ValueError("PDF tidak ditemukan atau artikel di balik paywall")

    text, raw_bibliography = _extract_text_from_pdf(pdf_url)
    if not text.strip():
        raise ValueError("Gagal mengekstrak teks dari PDF")

    return summarize(text, raw_bibliography)


# =====================================================================
# MODUL EVALUASI SKRIPSI (DITAMBAHKAN UNTUK PENGUJIAN BAB IV)
# =====================================================================
def _normalize_text(text: str) -> str:
    if not text:
        return ""

    # Hapus markdown
    text = re.sub(r'[*_`#>-]', '', text)

    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text)

    return text.strip().lower()


def _similarity(text1: str, text2: str) -> float:
    """
    Menghitung tingkat kemiripan dua string dalam persen.
    """
    return round(
        SequenceMatcher(
            None,
            _normalize_text(text1),
            _normalize_text(text2)
        ).ratio() * 100,
        2
    )

def evaluate_modul(article_url: str, expected_judul: str = "", expected_author: str = "") -> dict:
    """
    Fungsi khusus untuk mengevaluasi kinerja modul ML.
    Pencocokan dilakukan pada atribut 'judul' dan 'author'.
    """
    evaluation_report = {
        "url": article_url,
        "latency_seconds": 0.0,
        "regex_parsing_success": False,
        "empty_fields": [],
        "match_results": {
            "judul_similarity": 0.0,
            "judul_match": False,
            "author_similarity": 0.0,
            "author_match": False
        },
        "error": None
    }

    start_time = time.time()
    try:
        summary_result = summarize_from_url(article_url)
        end_time = time.time()
        evaluation_report["latency_seconds"] = round(end_time - start_time, 3)
    except Exception as e:
        end_time = time.time()
        evaluation_report["latency_seconds"] = round(end_time - start_time, 3)
        evaluation_report["error"] = str(e)
        return {
            "result": {},
            "metrics": evaluation_report
        }

    # Evaluasi Kepatuhan Format (Regex Parsing Rate)
    empty_fields = [key for key, val in summary_result.items() if not val.strip()]
    evaluation_report["empty_fields"] = empty_fields
    evaluation_report["regex_parsing_success"] = len(empty_fields) == 0

    judul_similarity = _similarity(
        expected_judul,
        summary_result.get("judul", "")
    )

    author_similarity = _similarity(
        expected_author,
        summary_result.get("author", "")
    )

    evaluation_report["match_results"]["judul_similarity"] = judul_similarity
    evaluation_report["match_results"]["author_similarity"] = author_similarity

    # Ambang batas validasi
    SIMILARITY_THRESHOLD = 90.0

    evaluation_report["match_results"]["judul_match"] = (
        judul_similarity >= SIMILARITY_THRESHOLD
    )

    evaluation_report["match_results"]["author_match"] = (
        author_similarity >= SIMILARITY_THRESHOLD
    )

    return {
        "result": summary_result,
        "metrics": evaluation_report
    }


# CONTOH SIMULASI PENGGUNAAN EVALUASI DI LINGKUNGAN PENGUJIAN (LOKAL)
if __name__ == "__main__":
    # Ganti dengan URL jurnal/artikel asli yang valid dan ingin Anda uji
    sample_url = "https://jurnal.uns.ac.id/inkuiri/article/viewFile/50085/30869"

    # Input manual untuk dicocokkan
    input_judul_manual = "MENYELIDIKI ENERGI PADA FOTOSINTESIS TUMBUHAN"
    input_author_manual = "Suyatman"

    print("--- Memulai Pengujian Evaluasi Modul ML ---")

    # Jalankan evaluasi
    laporan_uji = evaluate_modul(sample_url, input_judul_manual, input_author_manual)

    # Tampilkan hasil metriknya di terminal
    import json
    print("\n[HASIL METRIK EVALUASI]:")
    print(json.dumps(laporan_uji["metrics"], indent=4))

    print("\n[HASIL RINGKASAN TERSTRUKTUR]:")
    print(json.dumps(laporan_uji["result"], indent=4))
