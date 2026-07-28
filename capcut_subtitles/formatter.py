"""Split SRT cues into short, CapCut-friendly subtitle fragments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from .srt import Subtitle, read_srt, write_srt

NARROW_CHARS = set("ilI1|!.,:;'`йіїтгГТ")
WIDE_CHARS = set("MWШЩЖЮФЫМДЦЪWmw")


@dataclass(frozen=True)
class FormatOptions:
    max_words: int = 4
    max_visual_width: float = 18.0
    backup: bool = True


def char_width(char: str) -> float:
    if char.isspace() or char in NARROW_CHARS:
        return 0.55
    if char in WIDE_CHARS:
        return 1.35
    if char.isupper():
        return 1.1
    return 1.0


def visual_width(text: str) -> float:
    return sum(char_width(char) for char in text)


def split_text(text: str, options: FormatOptions) -> List[str]:
    """Split only at word boundaries; a single long word is preserved whole."""
    chunks: List[str] = []
    current: List[str] = []
    for word in text.split():
        candidate = " ".join(current + [word])
        exceeds_limits = (
            visual_width(candidate) > options.max_visual_width
            or len(current) + 1 > options.max_words
        )
        if current and exceeds_limits:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_timing(start_ms: int, end_ms: int, chunks: List[str]) -> List[Tuple[int, int]]:
    """Allocate cue duration proportionally to each fragment's visual width."""
    if not chunks:
        return []
    if len(chunks) == 1:
        return [(start_ms, end_ms)]
    duration = max(1, end_ms - start_ms)
    weights = [max(1.0, visual_width(chunk)) for chunk in chunks]
    total_weight = sum(weights)
    timings = []
    current_start = start_ms
    accumulated = 0.0
    for index, weight in enumerate(weights):
        accumulated += weight
        current_end = end_ms if index == len(weights) - 1 else start_ms + round(duration * accumulated / total_weight)
        current_end = min(end_ms, max(current_start + 1, current_end))
        timings.append((current_start, current_end))
        current_start = current_end
    return timings


def format_subtitles(subtitles: List[Subtitle], options: FormatOptions) -> List[Subtitle]:
    result = []
    for subtitle in subtitles:
        chunks = split_text(subtitle.text, options)
        for chunk, (start_ms, end_ms) in zip(chunks, split_timing(subtitle.start_ms, subtitle.end_ms, chunks)):
            result.append(Subtitle(start_ms, end_ms, chunk))
    return result


def format_srt(path: Path, options: FormatOptions) -> Tuple[int, int, Path | None]:
    """Format an SRT in place, retaining its original beside it when requested."""
    original_content = path.read_text(encoding="utf-8-sig")
    subtitles = read_srt(path)
    formatted = format_subtitles(subtitles, options)
    backup_path = None
    if options.backup:
        backup_path = path.with_name("{}.original{}".format(path.stem, path.suffix))
        if not backup_path.exists():
            backup_path.write_text(original_content, encoding="utf-8")
    write_srt(path, formatted)
    return len(subtitles), len(formatted), backup_path

