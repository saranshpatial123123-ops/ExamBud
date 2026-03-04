def merge_transcript_and_visuals(transcript: list[dict], visuals: list[dict]) -> list[dict]:
    """
    Combines speech segments with nearest visual text based on frame timestamp proximity.
    """
    merged_chunks = []
    
    for seg in transcript:
        nearest_visual = None
        min_diff = float("inf")
        
        for v in visuals:
            diff = abs(v["start"] - seg["start"])
            if diff < min_diff:
                min_diff = diff
                nearest_visual = v
                
        merged_chunk = {
            "timestamp": seg["timestamp"],
            "speech": seg["speech"],
            "visual_text": nearest_visual["visual_text"] if nearest_visual else "",
            "nearest_visual_timestamp": nearest_visual["timestamp"] if nearest_visual else ""
        }
        merged_chunks.append(merged_chunk)
        
    return merged_chunks

def format_embedding_text(chunk: dict) -> str:
    text = chunk["speech"]
    if chunk.get("visual_text"):
        text += f"\nSlide Content:\n{chunk['visual_text']}"
    return text
