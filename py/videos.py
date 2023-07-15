"""
Manage the videos and their ratings
"""
from dataclasses import dataclass, field
from typing import List, Tuple

"""
Support different
"""
@dataclass
class VideoQuality:
    quality_sequence: List[]


@dataclass
class Video:
    video_id: str
    ratings: List[int] = field(default_factory=list)
