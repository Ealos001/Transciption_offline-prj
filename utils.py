"""
Funzioni utility per tutto il progetto

Include: rilevamento device, gestione video, formattazione output
"""

import subprocess
import shutil
from pathlib import Path
import torch


def check_system_dependencies() -> None:
    """
    Verifica che ffmpeg, ffprobe e ffplay siano installati
    
    Raises:
        RuntimeError: Se uno dei tool non è trovato
    """
    for cmd in ["ffmpeg", "ffprobe", "ffplay"]:
        if not shutil.which(cmd):
            raise RuntimeError(
                f"❌ {cmd} non trovato!\n"
                f"   Installa con: sudo apt install ffmpeg (Linux/WSL)\n"
                f"                 brew install ffmpeg (macOS)\n"
                f"   Oppure scarica da: https://ffmpeg.org/download.html"
            )


def get_device() -> str:
    """
    Rileva dispositivo disponibile (CUDA o CPU)
    
    Returns:
        "cuda" se GPU disponibile, altrimenti "cpu"
    """
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        vram_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"🎮 Device: cuda ({device_name}, {vram_GB:.1f}GB VRAM)")
        return "cuda"
    print("💻 Device: CPU")
    return "cpu"


def get_video_duration(video_path: Path) -> float:
    """
    Ottiene durata video in secondi usando ffprobe
    
    Args:
        video_path: Percorso del file video
        
    Returns:
        Durata in secondi (float)
        
    Raises:
        RuntimeError: Se ffprobe fallisce o video non valido
    """
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,  # FIX: rimosso spazio extra
            check=True,
        )
        return float(result.stdout.strip())
    except FileNotFoundError:
        raise RuntimeError("ffprobe non installato! Esegui check_system_dependencies()")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Errore lettura video: {e.stderr}")
    except ValueError:
        raise RuntimeError(f"Durata video non valida per {video_path}")


def seconds_to_timestamp(seconds: float) -> str:
    """
    Converte secondi in formato timestamp HH:MM:SS.mm
    
    Args:
        seconds: Tempo in secondi
        
    Returns:
        Stringa formato "HH:MM:SS.mm"
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:05.2f}"


def print_header(title: str) -> None:
    """Stampa header formattato per separare sezioni principali"""
    print(f"\n{'='*70}")
    print(f"{title.center(70)}")
    print(f"{'='*70}\n")


def print_section(title: str) -> None:
    """Stampa sottosezione formattata"""
    print(f"\n{'─'*70}")
    print(f">> {title}")
    print(f"{'─'*70}\n")