"""Configurazione centralizzata"""

from pathlib import Path

# Percorsi
INPUT_VIDEO = Path("conferenza.mp4")
CHUNKS_DIR = Path("chunks")
OUTPUT_DIR = Path("output")

# Parametri per il chunking
MAX_CHUNK_SECONDS = 480 #8min
OVERLAP_SECONDS = 2

# WHISPER
WHISPER_MODEL = "medium"
WHISPER_DEVICE = "cuda" #o "cpu"

#Datapizza
OLLAMA_API_KEY = ""
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
"""
Configurazione centralizzata del progetto

Modifica questi parametri secondo le tue esigenze prima di eseguire la pipeline.
"""

import os
from pathlib import Path

# =============================================================================
# PERCORSI
# =============================================================================

INPUT_VIDEO = Path("conferenza.mp4")  # Video da trascrivere
CHUNKS_DIR = Path("chunks")           # Directory chunk temporanei
OUTPUT_DIR = Path("output")           # Directory output trascrizioni

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
INITIAL_PROMPT = {
    "it": "Conferenza accademica in italiano con termini tecnici di design e architettura.",
    "es": "Conferencia académica en español con términos técnicos de diseño y arquitectura.",
    "en": "Academic conference in English with technical terminology related to design and architecture.",
    "fr": "Conférence académique en français avec une terminologie technique liée au design et à l'architecture."
}

# =============================================================================
# OLLAMA (Correzione AI)
# =============================================================================

# API Key da variabile d'ambiente (sicuro) o fallback vuoto
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
#Language detection
LANGUAGE_DETECTION_MODE = "auto"
FIXED_LANGUAGE = "it"

# Models config
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

#initial prompt
INITIAL_PROMPT = {
    "it": "Conferenza accademica in italiano con termini tecnici di design e architettura.",
    "es": "Conferencia académica en español con términos técnicos de diseño y arquitectura.",
    "en": "Academic conference in English with technical terminology related to design and architecture.",
    "fr": "Conférence académique en français avec une terminologie technique liée au design et à l’architecture."
}
