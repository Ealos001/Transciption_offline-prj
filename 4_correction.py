"""
STEP 4: Correzione Testo con AI (Ollama + Datapizza)

Obiettivo:
- Correggere errori grammaticali, ortografici e refusi evidenti
- NON riscrivere il testo
- NON cambiare stile o contenuto
- Mantenere struttura e a capo

⚠️ IMPORTANTE: Questo script corregge IL TESTO INTERO, non solo entità.
               Richiede Ollama attivo su localhost:11434
"""

from pathlib import Path
import re
import requests
import sys

# Import da directory parent (se eseguito da subdirectory)
sys.path.insert(0, str(Path(__file__).parent.parent))

from datapizza.agents import Agent
from datapizza.clients.openai_like import OpenAILikeClient
from config import *
from utils import *


# =============================================================================
# UTILITY
# =============================================================================

def extract_text(response) -> str:
    """
    Estrae testo puro dalla risposta dell'agente
    
    Gestisce diversi formati di risposta:
    - Lista di blocchi (content = [block1, block2, ...])
    - Oggetto con attributo .text
    - Oggetto con attributo .content
    - Stringa diretta
    """
    content = response.content

    if isinstance(content, list):
        # Concatena blocchi testuali
        text = " ".join(
            str(getattr(block, "text", getattr(block, "content", block)))
            for block in content
        )
    elif hasattr(content, "text"):
        text = content.text
    elif hasattr(content, "content"):
        text = content.content
    else:
        text = str(content)

    # Rimuove intestazioni spurie che l'AI potrebbe aggiungere
    prefixes = [
        "Ecco il testo corretto:",
        "Trascrizione corretta:",
        "Testo corretto:",
        "Output:",
    ]
    for p in prefixes:
        if text.strip().startswith(p):
            text = text.strip()[len(p):]

    return text.strip()


def validate_output(original: str, corrected: str) -> str:
    """
    Evita output troncati o espansi in modo sospetto
    
    Args:
        original: Testo originale
        corrected: Testo corretto dall'AI
        
    Returns:
        Testo corretto se valido, altrimenti originale
    """
    # Troppo corto → probabilmente troncato
    if len(corrected) < len(original) * 0.6:
        print("⚠️  Output troppo corto, uso originale")
        return original

    # Troppo lungo → AI ha aggiunto spiegazioni
    if len(corrected) > len(original) * 1.4:
        print("⚠️  Output troppo lungo, possibile spiegazione AI")
        # Prendi solo primo paragrafo (probabile testo corretto)
        corrected = corrected.split("\n\n")[0]

    return corrected.strip()


def chunk_text(text: str, max_len: int = 2000) -> list[str]:
    """
    Divide il testo in chunk per lunghezza, preservando i paragrafi
    
    Strategia:
    1. Split per paragrafi (\n\n)
    2. Accorpa paragrafi finché sotto max_len
    3. Se paragrafo singolo > max_len, lo mette da solo (gestito da AI)
    
    Args:
        text: Testo da dividere
        max_len: Lunghezza massima chunk (caratteri)
        
    Returns:
        Lista di chunk di testo
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for p in paragraphs:
        # Prova ad aggiungere paragrafo a chunk corrente
        if len(current) + len(p) + 2 <= max_len:
            current += p + "\n\n"
        else:
            # Salva chunk corrente e inizia nuovo
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"
            
            # TODO: Se p > max_len, potrebbe essere utile splittare per frasi
            # Al momento lasciamo gestire all'AI (Ollama ha context ~4k token)

    # Aggiungi ultimo chunk
    if current.strip():
        chunks.append(current.strip())

    return chunks


# =============================================================================
# AGENT AI
# =============================================================================

def create_correction_agent() -> Agent:
    """
    Crea agente AI per correzione trascrizioni
    
    Returns:
        Agent configurato con prompt specifico
    """
    client = OpenAILikeClient(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
        model=OLLAMA_MODEL,
        temperature=0.1,  # Bassa temperatura = output più deterministico
    )

    # System prompt: istruzioni chiare per l'AI
    system_prompt = """
Sei un correttore automatico di trascrizioni in lingua italiana.

COMPITO:
Correggi errori grammaticali, ortografici e refusi evidenti.

REGOLE ASSOLUTE:
1. Restituisci SOLO il testo corretto
2. NON aggiungere spiegazioni o commenti
3. NON riformulare le frasi
4. NON migliorare lo stile
5. NON cambiare il significato
6. Mantieni ordine, struttura e a capo

PUOI correggere:
- parole duplicate ("non non" → "non")
- concordanze errate ("il casa" → "la casa")
- articoli e preposizioni sbagliate ("la università" → "l'università")
- refusi evidenti e interferenze linguistiche IT/ES ("el problema" → "il problema")
- errori di genere e numero

NON puoi:
- sintetizzare o riassumere
- riscrivere frasi
- aggiungere contenuti
- usare sinonimi non necessari

ESEMPI:
Input:  "il problema è che non non c'è tempo"
Output: "il problema è che non c'è tempo"

Input:  "la università di Roma ha ha pubblicato el studio"
Output: "l'università di Roma ha pubblicato lo studio"
"""

    return Agent(
        name="Correttore Trascrizioni",
        client=client,
        system_prompt=system_prompt,
    )


# =============================================================================
# CORE LOGIC
# =============================================================================

def correct_transcription(text: str) -> str:
    """
    Corregge trascrizione completa usando AI
    
    Args:
        text: Testo da correggere
        
    Returns:
        Testo corretto (o originale se errori)
    """
    print_header("CORREZIONE TRASCRIZIONE COMPLETA")

    # Verifica che Ollama sia disponibile
    try:
        r = requests.get(OLLAMA_BASE_URL.replace("/v1", "/api/tags"), timeout=5)
        r.raise_for_status()
        print("✅ Ollama disponibile\n")
    except Exception as e:
        print(f"❌ Ollama non disponibile: {e}")
        print("💡 Avvia Ollama: ollama serve")
        print("💡 Scarica modello: ollama pull llama3.1:8b\n")
        return text

    # Crea agente
    agent = create_correction_agent()
    
    # Divide in chunk
    chunks = chunk_text(text, max_len=2000)
    print(f"📦 Chunk totali: {len(chunks)}\n")

    corrected_chunks = []

    # Processa ogni chunk
    for i, chunk in enumerate(chunks, 1):
        print(f"▶️  Chunk {i}/{len(chunks)} ({len(chunk)} char)")

        try:
            # Invia a AI
            response = agent.run(chunk)
            corrected = extract_text(response)
            
            # Valida output
            corrected = validate_output(chunk, corrected)
            corrected_chunks.append(corrected)

            # Feedback
            if corrected.strip() != chunk.strip():
                print("   ✅ Corretto")
            else:
                print("   ⚪ Nessuna modifica")

        except Exception as e:
            print(f"   ❌ Errore: {e}")
            # Fallback: mantieni originale
            corrected_chunks.append(chunk)

    # Ricompone testo mantenendo struttura
    final_text = "\n\n".join(corrected_chunks)

    # Pulizia soft (spazi multipli, newline eccessive)
    final_text = re.sub(r"[ \t]+", " ", final_text)      # Spazi multipli → singolo
    final_text = re.sub(r"\n{3,}", "\n\n", final_text)   # Max 2 newline consecutive

    return final_text.strip()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Entry point"""
    
    input_file = OUTPUT_DIR / "trascrizione_raw.txt"
    output_file = OUTPUT_DIR / "trascrizione_corretta.txt"

    # Verifica esistenza input
    if not input_file.exists():
        print(f"❌ File non trovato: {input_file}")
        print("💡 Esegui prima: python 3_transcription.py")
        sys.exit(1)

    # Carica testo
    text = input_file.read_text(encoding="utf-8")
    print(f"📂 Caricato: {len(text):,} caratteri\n")

    # Correggi
    corrected = correct_transcription(text)
    
    # Salva
    output_file.write_text(corrected, encoding="utf-8")

    # Statistiche
    changes = abs(len(corrected) - len(text))
    print_section("RISULTATO")
    print(f"📊 Caratteri originali:  {len(text):,}")
    print(f"📊 Caratteri corretti:   {len(corrected):,}")
    print(f"📊 Differenza:           {changes:,} ({changes/len(text)*100:.1f}%)")
    print(f"\n✅ Correzione completata")
    print(f"💾 Salvato in: {output_file}")


if __name__ == "__main__":
    main()