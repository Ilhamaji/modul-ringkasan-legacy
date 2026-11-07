<div align="center">

# Modul Ringkasan — Legacy (ARCHIVED)

> ⚠️ **This repository is archived.** The code here is **identical** to the older version and has been superseded by
> **[`groq-article-summarizer`](https://github.com/Ilhamaji/groq-article-summarizer)**. Use that repo for the latest version.

[![Status](https://img.shields.io/badge/status-archived-lightgrey?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)

**English** · [Bahasa Indonesia](README.id.md)

</div>

---

## Why This Is Archived

This repository is the early copy of the summarisation module, developed for thesis work in July 2026. The newer, more complete version lives in **`groq-article-summarizer`** (September 2026).

It stays public and read-only for three reasons:

1. **Thesis record** — it preserves the exact version used during testing.
2. **Evaluation scripts** — it contains the latency and accuracy measurements referenced in the report.
3. **Citations** — so existing links do not rot.

## Move to the Current Version

```bash
git clone https://github.com/Ilhamaji/groq-article-summarizer.git
```

The newer version adds full documentation, cleaner code structure, and better error handling. The core function is the same.

## Contents

```
main.py            # summarisation pipeline (identical to the old version)
requirements.txt   # dependencies
```

## Running It (if still needed)

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_xxxxx"
python main.py
```

## Tech Stack

Python · Groq API (`llama-3.3-70b-versatile`) · PyMuPDF · BeautifulSoup4 · Regex

---

<div align="center">
Archived by <a href="https://github.com/Ilhamaji">Ilham Aji</a>
</div>
