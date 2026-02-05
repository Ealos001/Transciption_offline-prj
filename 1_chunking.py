"""
STEP 1: Chunking Video

Divide il video in chunk con overlap configurabile.
L'overlap serve per non perdere parole tra un chunk e l'altro.

Esempio con MAX_CHUNK_SECONDS=480s e OVERLAP_SECONDS=2s:
    Chunk 0: 0:00 -> 8:00
    Chunk 1: 7:58 -> 15:58  (overlap 2s con chunk 0)
    Chunk 2: 15:56 -> 23:56 (overlap 2s con chunk 1)
"""

from pathlib import Path
import subprocess
import math
import json
import sys
from config import *
from utils import *


def split_video(input_video: Path, output_dir: Path) -> list[dict]:
    """
    Divide video in chunk con overlap
    
    Args:
        input_video: Percorso video da dividere
        output_dir: Directory dove salvare i chunk
        
    Returns:
        Lista di dict con metadati chunk (index, path, start, end, duration)
        
    Raises:
        RuntimeError: Se ffmpeg fallisce
    """
    duration = get_video_duration(input_video)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calcolo chunk: lo step è ridotto per via dell'overlap
    step = MAX_CHUNK_SECONDS - OVERLAP_SECONDS
    num_chunks = math.ceil(duration / step)

    print_header("CHUNKING VIDEO")

    print(f"📹 Video: {input_video.name}")
    print(f"⏱️  Durata totale: {duration:.1f}s ({duration/60:.1f} min)")
    print(f"✂️  Configurazione:")
    print(f"   • Chunk size: {MAX_CHUNK_SECONDS}s ({MAX_CHUNK_SECONDS/60:.1f} min)")
    print(f"   • Overlap: {OVERLAP_SECONDS}s")
    print(f"   • Step: {step}s")
    print(f"📦 Chunk da creare: {num_chunks}\n")

    chunks_info = []

    for i in range(num_chunks):
        start = i * step
        end = min(start + MAX_CHUNK_SECONDS, duration)
        actual_duration = end - start

        start_ts = seconds_to_timestamp(start)
        end_ts = seconds_to_timestamp(end)

        output = output_dir / f"chunk_{i:03}.mp4"

        # Usa -c copy per velocità (no re-encoding)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-ss", start_ts,
            "-to", end_ts,
            "-c", "copy",
            "-avoid_negative_ts", "1",  # Evita timestamp negativi
            str(output),
        ]

        print(f"  Chunk {i:03}: {start/60:6.2f}min -> {end/60:6.2f}min (durata: {actual_duration:.1f}s)")

        try:
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Errore creazione chunk {i}: {e}")

        chunks_info.append({
            "index": i,
            "path": str(output),
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": actual_duration,
        })

    print(f"\n✅ Completato! {num_chunks} chunk creati in {output_dir}/\n")

    return chunks_info


def main():
    """Esegue chunking e salva metadati"""
    
    # Verifica dipendenze sistema
    try:
        check_system_dependencies()
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    
    # Verifica esistenza video
    if not INPUT_VIDEO.exists():
        print(f"❌ Video non trovato: {INPUT_VIDEO}")
        print("💡 Modifica INPUT_VIDEO in config.py")
        sys.exit(1)
    
    # Esegue chunking
    try:
        chunks_info = split_video(INPUT_VIDEO, CHUNKS_DIR)
    except RuntimeError as e:
        print(f"❌ Errore durante chunking: {e}")
        sys.exit(1)

    # Salva metadati JSON
    info_file = CHUNKS_DIR / "chunks_info.json"
    info_file.write_text(json.dumps(chunks_info, indent=2), encoding="utf-8")
    print(f"💾 Info salvate in {info_file}")
    print("\n➡️  Prossimo step: python 2_language_detection.py")


if __name__ == "__main__":
    main()