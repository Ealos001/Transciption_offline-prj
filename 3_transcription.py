"""
STEP 3: Trascrizione con Whisper

Trascrive ogni chunk usando la lingua rilevata.
Gestisce overlap tra chunk e cambio lingua.
"""

from pathlib import Path
import subprocess
import json
import sys
import torch
import whisper
import gc
from config import *
from utils import *


def extract_audio(video_path: Path) -> Path:
    """
    Estrae traccia audio da video in formato WAV mono 16kHz (richiesto da Whisper)
    
    Args:
        video_path: Percorso chunk video
        
    Returns:
        Percorso file WAV estratto (cache, se esiste già non rielabora)
    """
    wav_path = video_path.with_suffix(".wav")

    # Cache: se WAV già esiste, riutilizza
    if wav_path.exists():
        return wav_path
    
    # Estrae audio: mono (-ac 1), 16kHz (-ar 16000)
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn",           # No video
        "-ac", "1",      # Mono
        "-ar", "16000",  # 16kHz sample rate
        "-f", "wav", str(wav_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    return wav_path


def clean_overlap(prev: str, curr: str, overlap_second: int = 2) -> str:
    """
    Rimuove sovrapposizione tra chunk consecutivi
    
    Algoritmo:
    1. Cerca pattern comune tra fine di prev e inizio di curr
    2. Match minimo: 30 caratteri (~1.2 secondi di parlato italiano)
    3. Stima: ~25 caratteri/secondo in italiano medio
    
    Args:
        prev: Testo chunk precedente
        curr: Testo chunk corrente
        overlap_second: Secondi di overlap configurati
        
    Returns:
        Testo curr senza duplicazione
    """
    if not prev:
        return curr
    
    # Cerca solo nella coda di prev (zona overlap stimata)
    max_overlap_chars = overlap_second * 25  # ~25 caratteri/secondo
    tail = prev[-max_overlap_chars:]

    min_match_len = 30  # ~1.2s di parlato, evita falsi positivi
    best_cut = 0

    # Cerca il match più lungo tra tail e inizio di curr
    for i in range(len(tail) - min_match_len):
        match_len = 0
        
        # BUG FIX 1: Era ">" invece di "<" (loop usciva subito)
        # Continua FINCHÉ c'è spazio, non quando finisce
        while (i + match_len < len(tail) and 
               match_len < len(curr) and
               tail[i + match_len].lower() == curr[match_len].lower()):
            match_len += 1

        if match_len >= min_match_len:
            best_cut = match_len
            break

    # BUG FIX 2: Questo blocco era DENTRO il for (eseguiva ad ogni iterazione)
    # Deve eseguirsi DOPO il loop, una volta trovato il match
    if best_cut > 0:
        cleaned = curr[best_cut:].lstrip()
        overlap_text = curr[:best_cut]
        print(f"      🔗 Overlap rimosso ({best_cut} char): \"{overlap_text[:40]}...\"")
        return cleaned
    
    return curr


def transcribe_chunk(model, wav_path: Path, language: str, device: str, config: dict) -> str:
    """
    Trascrive singolo chunk con Whisper
    
    Args:
        model: Modello Whisper caricato
        wav_path: Percorso audio WAV
        language: Codice lingua ('it', 'es', 'en', 'fr')
        device: 'cuda' o 'cpu'
        config: Configurazione beam_size/best_of dal MODEL_CONFIGS
        
    Returns:
        Testo trascritto
    """
    initial_prompts = INITIAL_PROMPT

    result = model.transcribe(
        str(wav_path),
        task="transcribe",
        language=language,
        # BUG FIX 3: Era "initial_prompts" (plurale), parametro corretto è "initial_prompt"
        initial_prompt=initial_prompts.get(language, ""),
        fp16=(device == "cuda"),          # Precisione mista su GPU
        verbose=False,
        beam_size=config["beam_size"],    # Ricerca fascio (qualità)
        best_of=config["best_of"],        # Candidati da valutare
        temperature=0.0,                  # Deterministico (no random)
        condition_on_previous_text=False  # Ogni chunk indipendente
    )

    return result["text"].strip()


def transcribe_all():
    """Pipeline completa trascrizione tutti i chunk"""
    
    print_header("TRASCRIZIONE WHISPER")

    # Carica mappa lingue
    map_file = CHUNKS_DIR / "language_map.json"

    if not map_file.exists():
        print("❌ Language map non trovata!")
        print("   Esegui prima: python 2_language_detection.py")
        sys.exit(1)
    
    with open(map_file, encoding="utf-8") as f:
        language_map = json.load(f)

    chunks = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    if not chunks:
        print("❌ Nessun chunk trovato!")
        sys.exit(1)
    
    print(f"📦 Chunk da trascrivere: {len(chunks)}")
    print(f"🤖 Modello: {WHISPER_MODEL}")
    
    device = get_device()
    print()

    # Carica modello Whisper
    print(f"▶️  Caricamento modello {WHISPER_MODEL}...")
    model = whisper.load_model(WHISPER_MODEL, device=device)
    config = MODEL_CONFIGS[WHISPER_MODEL]
    print("✅ Modello caricato\n")
    
    # Crea output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Variabili accumulo
    full_text = ""
    # BUG FIX 4: Inizializza tutte le lingue supportate per evitare KeyError
    stats = {'it': 0, 'es': 0, 'en': 0, 'fr': 0}
    prev_lang = None

    # Loop trascrizione
    for idx, chunk in enumerate(chunks, 1):
        lang = language_map.get(str(chunk), "it")
        stats[lang] = stats.get(lang, 0) + 1  # Usa .get() per sicurezza

        # Emoji lingua per feedback visivo
        lang_emoji = {
            'it': '🇮🇹',
            'es': '🇪🇸',
            'en': '🇬🇧',
            'fr': '🇫🇷',
        }.get(lang, '🌍')
        
        print(f"▶️  [{idx}/{len(chunks)}] {lang_emoji} {chunk.name}")

        # Estrai audio
        wav_path = extract_audio(chunk)
        print(f"   ├─ Audio: {wav_path.name}")
            
        # Trascrivi
        print(f"   ├─ Trascrizione...", end=" ", flush=True)
        text = transcribe_chunk(model, wav_path, lang, device, config)
        print(f"✅ ({len(text)} char)")
            
        # Gestione overlap e cambio lingua
        if full_text and prev_lang == lang:
            # Stessa lingua → rimuovi overlap
            print(f"   ├─ Controllo overlap...")
            text = clean_overlap(full_text, text, OVERLAP_SECONDS)
        elif prev_lang and prev_lang != lang:
            # Cambio lingua → separatore visivo
            full_text += "\n\n--- CAMBIO LINGUA ---\n\n"
            print(f"   ├─ 🔄 Cambio lingua: {prev_lang.upper()} → {lang.upper()}")
        
        full_text += text + " "
        prev_lang = lang
        
        # Salva progressivo (non perdi tutto se crasha)
        output_raw = OUTPUT_DIR / "trascrizione_raw.txt"
        output_raw.write_text(full_text, encoding="utf-8")
        print(f"   └─ 💾 Salvato progressivo\n")
        
        # Libera memoria GPU
        if device == "cuda":
            torch.cuda.empty_cache()
    
    # Cleanup finale memoria
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    gc.collect()

    # Statistiche finali
    print_section("STATISTICHE")
    print(f"🇮🇹 Chunk italiani:  {stats.get('it', 0)}")
    print(f"🇪🇸 Chunk spagnoli:  {stats.get('es', 0)}")
    print(f"🇬🇧 Chunk inglesi:   {stats.get('en', 0)}")
    print(f"🇫🇷 Chunk francesi:  {stats.get('fr', 0)}")
    print(f"📝 Caratteri totali: {len(full_text):,}")
    print(f"💾 File: {output_raw}\n")
    
    print("✅ Trascrizione completata!")
    print("➡️  Prossimo step (opzionale): python 4_correction.py")


def main():
    """Entry point"""
    transcribe_all()


if __name__ == "__main__":
    main()