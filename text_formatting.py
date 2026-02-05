"""
Formattazione finale trascrizione

Obiettivo:
- Wrappare il testo a max 150 caratteri per riga
- Mantenere la leggibilità
- Preservare paragrafi e struttura logica
- NON spezzare parole a metà
"""

import sys
from pathlib import Path

# Aggiungi parent directory al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import textwrap
from config import OUTPUT_DIR
from utils import print_header


# ---------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------

def smart_wrap(text: str, width: int = 150) -> str:
    """
    Wrapper intelligente che rispetta paragrafi e struttura.
    
    Metafora: come un tipografo che impagina un libro - rispetta
    i capoversi dell'autore ma sistema la larghezza delle righe.
    """
    # Divide il testo in paragrafi (separati da righe vuote)
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []
    
    for paragraph in paragraphs:
        # Pulisce spazi multipli e a capo singoli interni al paragrafo
        paragraph = re.sub(r'\s+', ' ', paragraph.strip())
        
        if not paragraph:
            continue
        
        # Wrappa il paragrafo rispettando la larghezza
        wrapped = textwrap.fill(
            paragraph,
            width=width,
            break_long_words=False,      # NON spezza parole
            break_on_hyphens=False,       # NON spezza su trattini
            expand_tabs=False,
            replace_whitespace=True,
            drop_whitespace=True
        )
        
        wrapped_paragraphs.append(wrapped)
    
    # Ricompone con doppio a capo tra paragrafi
    return '\n\n'.join(wrapped_paragraphs)


def clean_text(text: str) -> str:
    """
    Pulizia soft del testo prima del wrapping.
    
    Rimuove:
    - Spazi multipli
    - A capo tripli o più
    - Spazi prima della punteggiatura
    """
    # Normalizza spazi
    text = re.sub(r' +', ' ', text)
    
    # Normalizza a capo (max 2 consecutivi)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Rimuove spazi prima della punteggiatura
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    
    # Rimuove spazi a inizio/fine riga
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def add_visual_separators(text: str) -> str:
    """
    Aggiunge separatori visivi per migliorare leggibilità.
    
    Opzionale: puoi commentare questa funzione se non vuoi separatori.
    """
    # Nessun separatore per default - restituisce testo invariato
    return text


def format_statistics(original: str, formatted: str) -> dict:
    """
    Calcola statistiche sulla formattazione.
    """
    original_lines = original.split('\n')
    formatted_lines = formatted.split('\n')
    
    original_words = len(original.split())
    formatted_words = len(formatted.split())
    
    max_line_length = max(len(line) for line in formatted_lines) if formatted_lines else 0
    avg_line_length = sum(len(line) for line in formatted_lines) / len(formatted_lines) if formatted_lines else 0
    
    return {
        'original_lines': len(original_lines),
        'formatted_lines': len(formatted_lines),
        'original_words': original_words,
        'formatted_words': formatted_words,
        'max_line_length': max_line_length,
        'avg_line_length': avg_line_length,
        'original_chars': len(original),
        'formatted_chars': len(formatted)
    }


# ---------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------

def format_transcription(text: str, width: int = 150) -> str:
    """
    Formatta la trascrizione con larghezza fissa.
    
    Metafora: trasformare un rotolo di carta continua in un libro
    ben impaginato con margini uniformi.
    """
    print_header(f"FORMATTAZIONE TRASCRIZIONE (max {width} char/riga)")
    
    print("🧹 Pulizia testo...")
    cleaned = clean_text(text)
    
    print(f"📏 Wrapping a {width} caratteri...")
    wrapped = smart_wrap(cleaned, width=width)
    
    print("✨ Applicazione separatori...")
    formatted = add_visual_separators(wrapped)
    
    # Statistiche
    stats = format_statistics(text, formatted)
    
    print("\n📊 Statistiche formattazione:")
    print(f"   • Righe: {stats['original_lines']} → {stats['formatted_lines']}")
    print(f"   • Parole: {stats['original_words']} → {stats['formatted_words']}")
    print(f"   • Caratteri: {stats['original_chars']:,} → {stats['formatted_chars']:,}")
    print(f"   • Lunghezza max riga: {stats['max_line_length']} char")
    print(f"   • Lunghezza media riga: {stats['avg_line_length']:.1f} char")
    
    # Verifica conformità
    lines_too_long = [i for i, line in enumerate(formatted.split('\n'), 1) 
                      if len(line) > width]
    
    if lines_too_long:
        print(f"\n⚠️  ATTENZIONE: {len(lines_too_long)} righe superano {width} caratteri!")
        print(f"   Righe problematiche: {lines_too_long[:5]}...")
    else:
        print(f"\n✅ Tutte le righe rispettano il limite di {width} caratteri")
    
    return formatted


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    input_file = OUTPUT_DIR / "trascrizione_corretta.txt"
    output_file = OUTPUT_DIR / "trascrizione_formattata.txt"
    
    # Fallback: se non esiste la versione corretta, usa raw
    if not input_file.exists():
        input_file = OUTPUT_DIR / "trascrizione_raw.txt"
        print(f"⚠️  File corretta non trovato, uso: {input_file.name}")
    
    if not input_file.exists():
        print(f"❌ File non trovato: {input_file}")
        return
    
    text = input_file.read_text(encoding="utf-8")
    print(f"📂 Caricato: {len(text):,} caratteri\n")
    
    # Formattazione (modifica WIDTH qui se necessario)
    WIDTH = 150
    formatted = format_transcription(text, width=WIDTH)
    
    # Salva
    output_file.write_text(formatted, encoding="utf-8")
    
    print(f"\n✅ Formattazione completata")
    print(f"💾 Salvato in: {output_file}")
    
    # Mostra anteprima
    print("\n" + "="*80)
    print("📄 ANTEPRIMA (prime 20 righe):")
    print("="*80)
    preview_lines = formatted.split('\n')[:20]
    for i, line in enumerate(preview_lines, 1):
        # Mostra numero caratteri a destra
        print(f"{line}{' '*(WIDTH - len(line))}│{len(line):3}")
    print("="*80)


if __name__ == "__main__":
    main()