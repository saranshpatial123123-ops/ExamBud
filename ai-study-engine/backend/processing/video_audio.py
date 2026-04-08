import ffmpeg
from faster_whisper import WhisperModel
import os

def extract_audio(video_path: str, audio_path: str = None) -> str:
    if not audio_path:
        audio_path = f"{os.path.splitext(video_path)[0]}.wav"
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, ar=16000, ac=1, loglevel="error")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return audio_path
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error extracting audio: {e.stderr.decode()}")

def transcribe_audio(audio_path: str) -> list[dict]:
    # Using 'base' model for speed
    model_size = "base"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, _ = model.transcribe(audio_path, beam_size=5)
    
    transcript = []
    for segment in segments:
        m, s = divmod(int(segment.start), 60)
        timestamp = f"{m:02d}:{s:02d}"
        transcript.append({
            "timestamp": timestamp,
            "speech": segment.text.strip(),
            "start": segment.start
        })
    return transcript
