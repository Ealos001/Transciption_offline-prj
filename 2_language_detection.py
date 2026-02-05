"""
STEP 2: Language Detection

Rileva la lingua di ogni chunk. Modalità disponibili:
- "auto": Tutto italiano (default, nessuna interazione)
- "manual": Chiede per ogni chunk con preview audio
- "fixed": Usa FIXED_LANGUAGE per tutti i chunk
"""

from pathlib import Path
import subprocess
import json
import sys
from config import *
from utils import *


# Mappatura tasti -> lingue per modalità manual
LANG_OPTIONS = {
    'i': 'it',  # Italiano
    'e': 'es',  # Español
    'g': 'en',  # enGlish
    'f': 'fr',  # Français
}


def manual_classify_language(video_path: Path, index: int, total: int) -> str:
    """
    Classificazione manuale con preview audio primi 10s
    
    Args:
        video_path: Percorso chunk video
        index: Numero chunk corrente
        total: Totale chunk
        
    Returns:
        Codice lingua ('it', 'es', 'en', 'fr')
    """
    print(f"\n[{index}/{total}] {video_path.name}")
    print("   Lingua (invio=IT, e=ES, g=EN, f=FR, p=play 10s): ", end="")

    while True:
        choice = input().lower().strip()

        # Default italiano (invio)
        if choice in ("", "i"):
            return "it"

        # Altre lingue
        if choice in LANG_OPTIONS:
            return LANG_OPTIONS[choice]

        # Preview audio
        if choice == "p":
            print("   ▶️  Riproducing primi 10 secondi...")
            try:
                subprocess.run(
                    ["ffplay", "-autoexit", "-t", "10", "-nodisp", str(video_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            except FileNotFoundError:
                print("   ❌ ffplay non trovato!")
            except subprocess.CalledProcessError:
                print("   ❌ Errore riproduzione")
            
            # Riproponi scelta
            print("   Lingua (invio=IT, e=ES, g=EN, f=FR, p=play): ", end="")
            continue

        # Input non valido
        print("   ❌ Scelta non valida. ", end="")
        print("Lingua (invio=IT, e=ES, g=EN, f=FR, p=play): ", end="")


def detect_languages() -> dict:
    """
    Rileva lingua per tutti i chunk secondo LANGUAGE_DETECTION_MODE
    
    Returns:
        Dict {percorso_chunk: codice_lingua}
    """
    print_header("RILEVAMENTO LINGUE")

    chunks = sorted(CHUNKS_DIR.glob("chunk_*.mp4"))

    if not chunks:
        print("❌ Nessun chunk trovato! Esegui prima: python 1_chunking.py")
        sys.exit(1)

    print(f"📦 Trovati {len(chunks)} chunk")
    print(f"🔧 Modalità: {LANGUAGE_DETECTION_MODE}\n")

    language_map = {}

    # === MODALITÀ MANUAL ===
    if LANGUAGE_DETECTION_MODE == "manual":
        print("👤 Classificazione manuale")
        print("   • Invio = italiano (default)")
        print("   • 'e'   = spagnolo")
        print("   • 'g'   = inglese")
        print("   • 'f'   = francese")
        print("   • 'p'   = play primi 10 secondi\n")

        for i, chunk in enumerate(chunks, 1):
            lang = manual_classify_language(chunk, i, len(chunks))
            language_map[str(chunk)] = lang
            
            # Emoji per feedback visivo
            emoji = {
                'it': '🇮🇹',
                'es': '🇪🇸',
                'en': '🇬🇧',
                'fr': '🇫🇷',
            }.get(lang, '🌍')
            
            print(f"   → {emoji} {lang.upper()}")

    # === MODALITÀ FIXED ===
    elif LANGUAGE_DETECTION_MODE == "fixed":
        print(f"📌 Lingua fissa: {FIXED_LANGUAGE.upper()}\n")
        for chunk in chunks:
            language_map[str(chunk)] = FIXED_LANGUAGE
            
            emoji = {
                'it': '🇮🇹',
                'es': '🇪🇸',
                'en': '🇬🇧',
                'fr': '🇫🇷',
            }.get(FIXED_LANGUAGE, '🌍')
            
            print(f"   {emoji} {chunk.name}")

    # === MODALITÀ AUTO (default: tutto italiano) ===
    else:
        print("📌 Lingua predefinita: ITALIANO\n")
        for chunk in chunks:
            language_map[str(chunk)] = "it"
            print(f"   🇮🇹 {chunk.name}")

    # Statistiche finali
    print_section("RIEPILOGO")

    stats = {}
    for lang in language_map.values():
        stats[lang] = stats.get(lang, 0) + 1

    emoji_map = {'it': '🇮🇹', 'es': '🇪🇸', 'en': '🇬🇧', 'fr': '🇫🇷'}
    for lang, count in sorted(stats.items()):
        emoji = emoji_map.get(lang, '🌍')
        lang_name = {'it': 'Italiano', 'es': 'Spagnolo', 'en': 'Inglese', 'fr': 'Francese'}.get(lang, lang.upper())
        print(f"{emoji} {lang_name}: {count} chunk")
    print()

    # Salva mappa
    map_file = CHUNKS_DIR / "language_map.json"
    map_file.write_text(json.dumps(language_map, indent=2), encoding="utf-8")
    print(f"💾 Mappa salvata: {map_file}\n")

    return language_map


def main():
    """Esegue detection e salva mappa"""
    
    language_map = detect_languages()

    if language_map:
        print("✅ Rilevamento completato!")
        print("➡️  Prossimo step: python 3_transcription.py")


if __name__ == "__main__":
    main()