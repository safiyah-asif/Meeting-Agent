import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
import whisper

# Load Whisper model once
_whisper_model = whisper.load_model("base")


def record_audio(duration=8, fs=16000, device=None):
    """
    Records audio from the microphone for `duration` seconds.
    """
    recording = sd.rec(int(duration * fs), samplerate=fs,
                       channels=1, dtype='int16', device=device)
    sd.wait()
    return recording


def render_voice_input(duration=5):
    """
    Records audio and returns transcribed text.
    """
    audio = record_audio(duration=duration)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, 16000)
        result = _whisper_model.transcribe(tmp.name)
    text = result["text"].strip()
    return text
