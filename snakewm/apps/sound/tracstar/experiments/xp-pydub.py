#!/usr/bin/python
# Requires sudo apt install -y ffmpeg
# Opens a file, auto detects the format, and starts playing.
# Downside: Converts to WAV as an intermediate.
from pydub import AudioSegment
from pydub import playback
song = AudioSegment.from_file("music/test-file.flac")
print("Duration:")
print(song.duration_seconds)
playback.play(song)
