# Second Brain AI Agent

AI Assistant pribadi berbasis Telegram — Second Brain, Knowledge Base, Jurnal Investasi, dan Task Manager.

## Prasyarat

- Python 3.12+
- Docker (untuk PostgreSQL + pgvector)
- [Ollama](https://ollama.com) (untuk AI lokal)
- Token bot Telegram dari [@BotFather](https://t.me/BotFather)

## Setup

### 1. Clone & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env — isi TELEGRAM_TOKEN
```

### 3. Database

```bash
docker compose up -d
```

PostgreSQL akan berjalan di `localhost:5432` dengan pgvector dan schema awal.

### 4. Ollama models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 5. Jalankan Aplikasi (API & Bot)

Menjalankan FastAPI secara otomatis juga akan menjalankan Telegram Bot di latar belakang (melalui Lifespan manager).

```bash
uvicorn app.api.main:app --reload
```
API akan berjalan di `http://localhost:8000` dan Swagger Documentation di `http://localhost:8000/docs`.

*Jika ingin menjalankan Bot secara terpisah tanpa API:*
```bash
python bot.py
```

## Perintah Telegram

| Perintah | Deskripsi |
|----------|-----------|
| `/note <teks>` | Simpan catatan dengan embedding |
| `/find <kata kunci>` | Cari catatan (semantic search) |
| `/ask <pertanyaan>` | Tanya AI berdasarkan catatan |
| `/task <teks>` | Tambah task |
| `/today` | Lihat task hari ini |
| `/done <id>` | Tandai task selesai |
| `/invest buy/sell <symbol> <harga> <qty>` | Catat transaksi |
| `/portfolio` | Lihat portfolio |
| `/model` | Lihat model aktif |
| `/models` | Daftar model |
| `/model <nama>` | Ganti model |
| `/summary` | Ringkasan mingguan |

## AI Provider

Default: `AI_PROVIDER=ollama`

Untuk provider lain, set di `.env`:

- `openai` — butuh `OPENAI_API_KEY`
- `gemini` — butuh `GEMINI_API_KEY`
- `groq` — butuh `GROQ_API_KEY`

> **Catatan embedding:** Ollama menggunakan dimensi 768 (`nomic-embed-text`). OpenAI menggunakan 1536 — jika ganti provider, update `EMBEDDING_DIMENSION` dan re-create database.

## Struktur Project

```
app/
├── api/              # FastAPI endpoints & routers
├── bot/handlers/     # Telegram command handlers
├── services/         # Business logic & AI
├── database/         # SQLAlchemy models
└── config.py
migrations/           # SQL schema
bot.py                # Bot Standalone Entry point
docker-compose.yml    # PostgreSQL + pgvector
```

## Deployment ke VPS

1. Copy project ke VPS
2. Set `.env` dengan kredensial production
3. `docker compose up -d`
4. Jalankan bot dengan systemd atau supervisor
5. Ganti `AI_PROVIDER` ke `gemini` atau `openai` jika diperlukan
