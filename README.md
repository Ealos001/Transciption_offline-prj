# 🎙️ Video Transcription Pipeline con Whisper

Pipeline automatica per trascrivere conferenze multilingua usando OpenAI Whisper e correzione AI locale.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Whisper](https://img.shields.io/badge/whisper-OpenAI-orange.svg)

---

## ✨ Features

- 🎬 **Chunking intelligente** con overlap configurabile
- 🌍 **Supporto multilingua** (IT 🇮🇹, ES 🇪🇸, EN 🇬🇧, FR 🇫🇷)
- 🔍 **Detection lingua** manuale o automatica con preview audio
- 🤖 **Correzione AI** tramite Ollama (locale, privacy-first)
- 💾 **Salvataggio progressivo** (recupero da crash)
- 🧹 **Rimozione automatica overlap** tra chunk consecutivi
- ⚡ **GPU acceleration** (CUDA opzionale)

---

## 📋 Requisiti

### Sistema
- **Python** 3.10+
- **ffmpeg** (con ffprobe e ffplay)
- **CUDA** 11.8+ (opzionale, per GPU acceleration)

### Installazione ffmpeg

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Scarica da: https://ffmpeg.org/download.html
# Aggiungi alla PATH
```

### Python Dependencies

```bash
# Crea virtual environment (raccomandato)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### Ollama (per correzione AI - Step 4)

```bash
# Installa Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Scarica modello LLaMA
ollama pull llama3.1:8b

# Verifica che sia attivo
ollama list
```

---

## 🚀 Quick Start

### 1️⃣ Configurazione

Modifica `config.py` secondo le tue esigenze:

```python
# Video da trascrivere
INPUT_VIDEO = Path("mia_conferenza.mp4")

# Modello Whisper (base/small/medium/large)
WHISPER_MODEL = "medium"

# Detection lingua: "auto" (tutto IT), "manual" (chiede), "fixed" (usa FIXED_LANGUAGE)
LANGUAGE_DETECTION_MODE = "auto"
```

### 2️⃣ Esecuzione Pipeline

```bash
# Step 1: Chunking video
python 1_chunking.py

# Step 2: Detection lingua
python 2_language_detection.py

# Step 3: Trascrizione
python 3_transcription.py

# Step 4: Correzione AI (opzionale, richiede Ollama)
python 4_correction.py
```

### 3️⃣ Output

I file generati saranno in `output/`:

- `trascrizione_raw.txt` → Trascrizione grezza da Whisper
- `trascrizione_corretta.txt` → Trascrizione corretta dall'AI

---

## 📁 Struttura Progetto

```
.
├── config.py                    # ⚙️  Configurazione centralizzata
├── utils.py                     # 🛠️  Funzioni utility
├── 1_chunking.py               # ✂️  Divisione video in chunk
├── 2_language_detection.py    # 🌍 Rilevamento lingua
├── 3_transcription.py          # 🎤 Trascrizione Whisper
├── 4_correction.py             # 🤖 Correzione AI (Ollama)
├── requirements.txt            # 📦 Dipendenze Python
├── README.md                   # 📖 Documentazione
├── LICENSE                     # 📄 Licenza MIT
│
├── chunks/                     # 📂 Chunk video (generato)
│   ├── chunk_000.mp4
│   ├── chunk_001.mp4
│   ├── ...
│   ├── chunks_info.json       # Metadati chunk
│   └── language_map.json      # Mappa lingue
│
└── output/                     # 📂 Trascrizioni (generato)
    ├── trascrizione_raw.txt
    └── trascrizione_corretta.txt
```

---

## ⚙️ Configurazioni Avanzate

### Modelli Whisper

| Modello | VRAM  | Velocità | Accuratezza | Use Case                    |
|---------|-------|----------|-------------|-----------------------------|
| base    | ~1GB  | ⚡⚡⚡    | ⭐⭐        | Test rapidi, CPU           |
| small   | ~2GB  | ⚡⚡      | ⭐⭐⭐      | Laptop, lingue semplici    |
| medium  | ~5GB  | ⚡       | ⭐⭐⭐⭐    | **Raccomandato** (balance) |
| large   | ~10GB | 🐌       | ⭐⭐⭐⭐⭐  | Massima accuratezza        |

### Chunk Size

```python
# config.py
MAX_CHUNK_SECONDS = 480  # 8 minuti (raccomandato per medium)
OVERLAP_SECONDS = 2      # 2 secondi (previene perdita parole)
```

**Linee guida:**
- Video brevi (<30 min): 240s (4 min)
- Video medi (30-90 min): 480s (8 min) ← **raccomandato**
- Video lunghi (>90 min): 600s (10 min)

### Detection Lingua

```python
# Modalità disponibili
LANGUAGE_DETECTION_MODE = "auto"    # Tutto italiano (no interazione)
LANGUAGE_DETECTION_MODE = "manual"  # Chiede per ogni chunk (con preview)
LANGUAGE_DETECTION_MODE = "fixed"   # Usa FIXED_LANGUAGE per tutti
```

**Modalità Manual:**
- Premi `Invio` = Italiano (default)
- Premi `e` = Spagnolo
- Premi `g` = Inglese
- Premi `f` = Francese
- Premi `p` = Play primi 10 secondi

---

## 🐛 Troubleshooting

### ❌ Errore "ffprobe not found"

```bash
# Verifica installazione
which ffmpeg ffprobe ffplay

# Se mancano, installa ffmpeg (vedi sezione Requisiti)
```

### ❌ Out of Memory (GPU)

Riduci dimensione chunk o usa modello più piccolo:

```python
# config.py
MAX_CHUNK_SECONDS = 240  # 4 minuti invece di 8
WHISPER_MODEL = "small"  # invece di medium
```

### ❌ Ollama non risponde (Step 4)

```bash
# Verifica servizio attivo
ollama list
curl http://localhost:11434/api/tags

# Se non parte, avvia manualmente
ollama serve

# Verifica modello scaricato
ollama pull llama3.1:8b
```

### ❌ Trascrizione imprecisa

1. **Usa modello più grande:**
   ```python
   WHISPER_MODEL = "large"
   ```

2. **Personalizza initial_prompt:**
   ```python
   # config.py - INITIAL_PROMPT
   "it": "Conferenza medica con terminologia anatomica e farmacologica."
   ```

3. **Aumenta beam_size:**
   ```python
   # config.py - MODEL_CONFIGS
   "medium": {
       "beam_size": 5,  # invece di 3
       "best_of": 5,
   }
   ```

---

## 📊 Performance

**Test Hardware:** NVIDIA RTX 3080 (10GB VRAM), AMD Ryzen 5800X

| Video      | Modello | Tempo  | Accuratezza |
|------------|---------|--------|-------------|
| 30 min 1080p | small   | ~8 min  | ~90%        |
| 90 min 1080p | medium  | ~25 min | ~95%        |
| 90 min 1080p | large   | ~60 min | ~98%        |

**CPU Mode (i7-12700K):**
- medium: ~2.5x tempo reale (90 min video = 225 min trascrizione)

---

## 🤝 Contributi

Contributi benvenuti! Apri issue o PR per:

- 🌍 Nuove lingue supportate
- ⚡ Ottimizzazioni performance
- 🐛 Bug fix e miglioramenti
- 📚 Documentazione

### Come Contribuire

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **MIT** - vedi file [LICENSE](LICENSE) per dettagli.

---

## 🙏 Credits

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model (MIT License)
- [Datapizza AI](https://github.com/datapizza/datapizza) - Agent framework
- [Ollama](https://ollama.com) - Local LLM runtime (MIT License)
- **Built with Meta Llama 3** - Language model for text corrections

### Licensing Notes
This project respects all upstream licenses:
- **Whisper:** MIT License (OpenAI) - Used via public API
- **LLaMA 3.1:** Meta Community License - Local inference only
- **FFmpeg:** Called as external process (LGPL compliant)
- **This Project:** MIT License - See [LICENSE](LICENSE) file

---

## 📬 Contatti

Per domande o supporto, apri una [issue](../../issues) su GitHub.

---

<div align="center">

**Made with ❤️ for the transcription community**

⭐ Se questo progetto ti è utile, lascia una stella!

</div>