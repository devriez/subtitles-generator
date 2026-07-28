"""Command line interface for capcut-subtitles."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .formatter import FormatOptions, format_srt
from .whisper import generate_srt


def _load_config(path: Path) -> Dict[str, Any]:
    try:
        try:
            import tomllib  # type: ignore
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore
        with path.open("rb") as config_file:
            return tomllib.load(config_file)
    except OSError as error:
        raise ValueError("Cannot read config {}: {}".format(path, error)) from error
    except Exception as error:
        raise ValueError("Invalid TOML config {}: {}".format(path, error)) from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate CapCut-friendly SRT subtitles with whisper.cpp.")
    parser.add_argument("videos", nargs="+", type=Path, help="Video file(s) to transcribe")
    parser.add_argument("--config", type=Path, help="Path to a TOML config file")
    parser.add_argument("--language", help="Spoken language code (default: ru)")
    parser.add_argument("--model", help="Model name under --models-dir (default: small)")
    parser.add_argument("--models-dir", type=Path, help="Directory containing ggml-<model>.bin files")
    parser.add_argument("--model-path", type=Path, help="Exact path to a whisper.cpp model")
    parser.add_argument("--ffmpeg-bin", help="ffmpeg executable (default: ffmpeg)")
    parser.add_argument("--whisper-bin", help="whisper.cpp executable (default: whisper-cli)")
    parser.add_argument("--max-words", type=int, help="Maximum words in one cue (default: 4)")
    parser.add_argument("--max-visual-width", type=float, help="Approximate maximum visual width (default: 18)")
    parser.add_argument("--no-backup", action="store_true", help="Do not retain <video>.original.srt")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    config = _load_config(args.config) if args.config else {}
    models_dir = Path(args.models_dir or config.get("models_dir", Path.home() / "whisper-models"))
    model = args.model or config.get("model", "small")
    model_path = Path(args.model_path or config.get("model_path", models_dir / "ggml-{}.bin".format(model))).expanduser()
    language = args.language or config.get("language", "ru")
    options = FormatOptions(
        max_words=args.max_words if args.max_words is not None else int(config.get("max_words", 4)),
        max_visual_width=args.max_visual_width if args.max_visual_width is not None else float(config.get("max_visual_width", 18)),
        backup=not args.no_backup and bool(config.get("backup", True)),
    )
    if options.max_words < 1 or options.max_visual_width <= 0:
        raise SystemExit("--max-words must be at least 1 and --max-visual-width must be positive")
    ffmpeg_bin = args.ffmpeg_bin or config.get("ffmpeg_bin", "ffmpeg")
    whisper_bin = args.whisper_bin or config.get("whisper_bin", "whisper-cli")
    if not model_path.is_file():
        raise SystemExit("Whisper model not found: {}".format(model_path))
    for executable in (ffmpeg_bin, whisper_bin):
        if not shutil.which(executable):
            raise SystemExit("Executable not found in PATH: {}".format(executable))
    failures = 0
    for video in args.videos:
        video = video.expanduser().resolve()
        if not video.is_file():
            print("Skipping missing file: {}".format(video), file=sys.stderr)
            failures += 1
            continue
        try:
            print("Transcribing {}…".format(video.name))
            srt_path = generate_srt(video, video.with_suffix(""), language, model_path, ffmpeg_bin, whisper_bin)
            before, after, backup = format_srt(srt_path, options)
            if backup:
                print("Original saved: {}".format(backup.name))
            print("Done: {} ({} cues → {})".format(srt_path.name, before, after))
        except Exception as error:
            print("Failed for {}: {}".format(video.name, error), file=sys.stderr)
            failures += 1
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
