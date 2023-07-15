import pickle
from typing import List, Tuple, Any


def video_quality_to_bytes(video_quality: List[Tuple[Any, ...]]) -> bytes:
    return pickle.dumps(video_quality)


def bytes_to_video_quality(quality_bytes: bytes) -> List[Tuple[Any, ...]]:
    return pickle.loads(quality_bytes)




