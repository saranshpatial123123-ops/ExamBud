import ffmpeg
import os
import pytesseract
from PIL import Image
import tempfile
import glob
import hashlib
from backend.utils.file_utils import delete_file

def extract_frames(video_path: str, frame_dir: str = None) -> list[str]:
    if not frame_dir:
        frame_dir = tempfile.mkdtemp(prefix="video_frames_")
    
    output_pattern = os.path.join(frame_dir, "frame_%04d.jpg")
    try:
        # fps=0.5 extracts 1 frame every 2 seconds
        (
            ffmpeg
            .input(video_path)
            .output(output_pattern, vf="fps=0.5", loglevel="error")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error extracting frames: {e.stderr.decode()}")
        
    frames = sorted(glob.glob(os.path.join(frame_dir, "*.jpg")))
    return frames

def extract_slide_text(frame_paths: list[str]) -> list[dict]:
    """
    Extracts text from each frame using OCR.
    Assumes 1 frame every 2 seconds.
    Skips duplicate frames using hashing.
    """
    visual_data = []
    seen_hashes = set()
    seen_texts = set()
    
    for i, frame in enumerate(frame_paths):
        start_time = i * 2 # seconds
        try:
            img = Image.open(frame)
            # Skip exact duplicate frames via hashing
            frame_hash = hashlib.md5(img.tobytes()).hexdigest()
            if frame_hash in seen_hashes:
                continue
            seen_hashes.add(frame_hash)
            
            text = pytesseract.image_to_string(img).strip()
            # Deduplicate text
            if text and text not in seen_texts:
                seen_texts.add(text)
                m, s = divmod(start_time, 60)
                timestamp = f"{m:02d}:{s:02d}"
                visual_data.append({
                    "timestamp": timestamp,
                    "start": start_time,
                    "visual_text": text
                })
        except Exception:
            pass
        finally:
            delete_file(frame) # Delete frame after OCR immediately
            
    return visual_data
