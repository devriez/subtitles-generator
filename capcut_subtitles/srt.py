"""Minimal, dependency-free SRT parsing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Subtitle:
    start_ms: int
    end_ms: int
    text: str


def timestamp_to_ms(timestamp: str) -> int:
    match = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})", timestamp.strip())
    if not match:
        raise ValueError("Invalid timestamp: {}".format(timestamp))
    hours, minutes, seconds, milliseconds = map(int, match.groups())
    return hours * 3_600_000 + minutes * 60_000 + seconds * 1_000 + milliseconds


def ms_to_timestamp(milliseconds: int) -> str:
    milliseconds = max(0, milliseconds)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1_000)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)


def parse_srt(content: str) -> List[Subtitle]:
    """Parse conventional SRT while retaining only valid subtitle blocks."""
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    subtitles = []
    for block in re.split(r"\n\s*\n", normalized):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        timing = re.fullmatch(
            r"\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
            r"(\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*",
            lines[1],
        )
        if not timing:
            continue
        text = " ".join(line.strip() for line in lines[2:] if line.strip())
        if text:
            subtitles.append(Subtitle(timestamp_to_ms(timing.group(1)), timestamp_to_ms(timing.group(2)), text))
    return subtitles


def render_srt(subtitles: Iterable[Subtitle]) -> str:
    blocks = []
    for number, subtitle in enumerate(subtitles, start=1):
        blocks.append(
            "{}\n{} --> {}\n{}".format(
                number,
                ms_to_timestamp(subtitle.start_ms),
                ms_to_timestamp(subtitle.end_ms),
                subtitle.text,
            )
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def read_srt(path: Path) -> List[Subtitle]:
    return parse_srt(path.read_text(encoding="utf-8-sig"))


def write_srt(path: Path, subtitles: Iterable[Subtitle]) -> None:
    path.write_text(render_srt(subtitles), encoding="utf-8")

