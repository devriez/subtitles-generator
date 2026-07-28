# CapCut Subtitle Formatter

Небольшая CLI-утилита, которая создаёт аккуратные SRT-субтитры для CapCut Desktop: извлекает аудио через `ffmpeg`, распознаёт речь с помощью `whisper.cpp`, затем делит длинные реплики на короткие фрагменты без разрыва слов.

## Возможности

- запускает `ffmpeg` и `whisper.cpp` (`whisper-cli`) из одной команды;
- создаёт SRT рядом с исходным видео;
- ограничивает число слов и приблизительную визуальную ширину реплики;
- никогда не делит слово на части;
- распределяет длительность исходной реплики между новыми фрагментами пропорционально их длине;
- сохраняет исходный SRT как `video.original.srt` перед форматированием.

CapCut сам центрирует текст, поэтому утилита не добавляет ведущие пробелы.

## Требования

- Python 3.9 или новее;
- [ffmpeg](https://ffmpeg.org/), доступный как команда `ffmpeg`;
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp), доступный как команда `whisper-cli`;
- модель whisper.cpp, например `ggml-small.bin`.

На macOS с Homebrew, например:

```bash
brew install ffmpeg whisper-cpp
mkdir -p ~/whisper-models
# Скачайте нужную модель whisper.cpp в ~/whisper-models/ggml-small.bin
```

## Установка

После публикации пакета в PyPI:

```bash
pip install capcut-subtitles
```

Пока пакет не опубликован, установите прямо из GitHub:

```bash
pip install git+https://github.com/devriez/subtitles-generator.git
```

Для разработки:

```bash
git clone https://github.com/devriez/subtitles-generator.git
cd subtitles-generator
python3 -m pip install -e .
```

## Использование

```bash
capcut-subtitles my_video.mp4
```

Результатом будут файлы рядом с видео:

```text
my_video.srt
my_video.original.srt
```

Можно передать несколько файлов:

```bash
capcut-subtitles first.mp4 second.mp4
```

Или использовать shell-маску:

```bash
capcut-subtitles *.mp4
```

По умолчанию программа ищет модель по пути `~/whisper-models/ggml-small.bin`. Другой путь можно передать явно:

```bash
capcut-subtitles my_video.mp4 --model-path ~/Downloads/ggml-medium.bin
```

## Настройка

Все частые настройки доступны как параметры:

```bash
capcut-subtitles my_video.mp4 \
  --language ru \
  --max-words 4 \
  --max-visual-width 18
```

Либо скопируйте [`examples/config.toml`](examples/config.toml) и передайте его:

```bash
capcut-subtitles --config config.toml my_video.mp4
```

Параметры командной строки имеют приоритет над конфигом. Чтобы не создавать резервную копию, добавьте `--no-backup`.

## Разработка

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## Лицензия

[MIT](LICENSE)
