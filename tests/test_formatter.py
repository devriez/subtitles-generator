import tempfile
import unittest
from pathlib import Path

from capcut_subtitles.formatter import FormatOptions, format_srt, split_text, split_timing


class FormatterTests(unittest.TestCase):
    def test_split_text_never_splits_a_word(self):
        options = FormatOptions(max_words=2, max_visual_width=12)
        chunks = split_text("Недавно появилась новость о брачном агентстве", options)
        self.assertEqual(" ".join(chunks), "Недавно появилась новость о брачном агентстве")
        self.assertEqual(split_text("сверхдлинноеслово", options), ["сверхдлинноеслово"])

    def test_timing_covers_the_original_interval(self):
        timings = split_timing(1_000, 5_000, ["коротко", "значительно длиннее"])
        self.assertEqual(timings[0][0], 1_000)
        self.assertEqual(timings[-1][1], 5_000)
        self.assertEqual(timings[0][1], timings[1][0])
        self.assertGreater(timings[1][1] - timings[1][0], timings[0][1] - timings[0][0])

    def test_format_srt_creates_backup_and_renumbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "video.srt"
            path.write_text("1\n00:00:00,000 --> 00:00:04,000\nРаз два три четыре пять шесть\n", encoding="utf-8")
            before, after, backup = format_srt(path, FormatOptions(max_words=2, max_visual_width=100))
            self.assertEqual((before, after), (1, 3))
            self.assertEqual(backup, Path(directory) / "video.original.srt")
            self.assertTrue(backup.is_file())
            self.assertTrue(path.read_text(encoding="utf-8").startswith("1\n"))
