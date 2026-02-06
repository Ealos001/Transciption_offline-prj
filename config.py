"""
Configurazione centralizzata del progetto

Modifica questi parametri secondo le tue esigenze prima di eseguire la pipeline.
"""

import os
from pathlib import Path

# =============================================================================
# PERCORSI
# =============================================================================

INPUT_VIDEO = Path("video.mp4")      # Video da trascrivere
CHUNKS_DIR = Path("chunks")          # Directory chunk temporanei
OUTPUT_DIR = Path("output")          # Directory output trascrizioni

# =============================================================================
# PARAMETRI CHUNKING
# =============================================================================

MAX_CHUNK_SECONDS = 480  # Durata massima chunk (8 minuti, raccomandato)
OVERLAP_SECONDS = 2      # Overlap tra chunk per continuità (2s raccomandato)

# =============================================================================
# WHISPER
# =============================================================================

WHISPER_MODEL = "medium"  # Opzioni: base, small, medium, large
WHISPER_DEVICE = "cuda"   # "cuda" per GPU, "cpu" per CPU

# Configurazioni modelli Whisper (beam_size e best_of per accuratezza)
MODEL_CONFIGS = {
    "base": {
        "name": "base",
        "beam_size": 2,
        "best_of": 2,
    },
    "small": {
        "name": "small",
        "beam_size": 3,
        "best_of": 2,
    },
    "medium": {
        "name": "medium",
        "beam_size": 3,
        "best_of": 3,
    },
    "large": {
        "name": "large-v3",
        "beam_size": 5,
        "best_of": 5,
    }
}

# =============================================================================
# RILEVAMENTO LINGUA
# =============================================================================

# Modalità detection: "auto" (tutto IT), "manual" (chiede per ogni chunk), "fixed" (usa FIXED_LANGUAGE)
LANGUAGE_DETECTION_MODE = "auto"
FIXED_LANGUAGE = "it"  # Usato solo se mode = "fixed"

# Prompt iniziali per Whisper (migliorano accuratezza su termini tecnici)
# Personalizza questi prompt in base al contenuto del tuo video
INITIAL_PROMPT = {
    "it": "Trascrizione audio in italiano con terminologia tecnica e formale.",
    "es": "Transcripción de audio en español con terminología técnica y formal.",
    "en": "Audio transcription in English with technical and formal terminology.",
    "fr": "Transcription audio en français avec terminologie technique et formelle."
}

# =============================================================================
# OLLAMA (Correzione AI)
# =============================================================================

# API Key da variabile d'ambiente (sicuro) o fallback vuoto
# Per Ollama locale (default), nessuna chiave necessaria
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
