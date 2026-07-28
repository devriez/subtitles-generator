# CapCut Subtitle Formatter

A small command-line tool that creates neat SRT subtitles for CapCut Desktop. It extracts audio with `ffmpeg`, transcribes speech with `whisper.cpp`, and splits long captions into short fragments without breaking words.

## Features

- Runs `ffmpeg` and `whisper.cpp` (`whisper-cli`) from one command.
- Creates an SRT file next to the source video.
- Limits the number of words and approximate visual width of each caption.
- Never splits a word in the middle.
- Allocates each original cue's duration among new fragments proportionally to their length.
- Saves the original SRT as `video.original.srt` before formatting it.

CapCut centers the text itself, so the tool never adds leading spaces.

## Requirements

- Python 3.9 or later.
- [ffmpeg](https://ffmpeg.org/), available as the `ffmpeg` command.
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp), available as the `whisper-cli` command.
- A whisper.cpp model, for example `ggml-small.bin`.

For example, on macOS with Homebrew:

```bash
brew install ffmpeg whisper-cpp
mkdir -p ~/whisper-models
# Download a whisper.cpp model to ~/whisper-models/ggml-small.bin
```

## Installation

Once the package is published to PyPI:

```bash
pip install capcut-subtitles
```

Until then, install it directly from GitHub:

```bash
pip install git+https://github.com/devriez/subtitles-generator.git
```

For local development:

```bash
git clone https://github.com/devriez/subtitles-generator.git
cd subtitles-generator
python3 -m pip install -e .
```

## Usage

```bash
subtitles my_video.mp4
```

The following files will appear next to the video:

```text
my_video.srt
my_video.original.srt
```

You can pass multiple videos:

```bash
subtitles first.mp4 second.mp4
```

Or use a shell wildcard:

```bash
subtitles *.mp4
```

By default, the tool looks for the model at `~/whisper-models/ggml-small.bin`. To use another model, pass its path explicitly:

```bash
subtitles my_video.mp4 --model-path ~/Downloads/ggml-medium.bin
```

## Configuration

The common settings are available as command-line options:

```bash
subtitles my_video.mp4 \
  --language ru \
  --max-words 4 \
  --max-visual-width 18
```

Alternatively, copy [`examples/config.toml`](examples/config.toml) and pass it to the command:

```bash
subtitles --config config.toml my_video.mp4
```

Command-line options take precedence over values in the configuration file. Add `--no-backup` to skip creation of the original-SRT backup.

## Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## License

[MIT](LICENSE)
