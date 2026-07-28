"""External ffmpeg and whisper.cpp process integration."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def generate_srt(
    video: Path,
    output_base: Path,
    language: str,
    model_path: Path,
    ffmpeg_bin: str,
    whisper_bin: str,
) -> Path:
    """Extract mono 16 kHz audio and transcribe it through whisper-cli."""
    with tempfile.TemporaryDirectory(prefix="capcut-subtitles-") as temp_dir:
        audio_path = Path(temp_dir) / "audio.wav"
        subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(audio_path)],
            check=True,
        )
        subprocess.run(
            [whisper_bin, "-m", str(model_path), "-f", str(audio_path), "-l", language, "-osrt", "-of", str(output_base)],
            check=True,
        )
    result = output_base.with_suffix(".srt")
    if not result.is_file():
        raise RuntimeError("whisper-cli completed but did not create {}".format(result))
    return result

