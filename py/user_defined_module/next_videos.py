from typing import List, Tuple, Any


def update_next_videos(videos: List[Tuple[str, List[Tuple[Any, ...]]]], ratings: List[List[int]]) -> Tuple[List[Tuple[
    str, Any]], List[int]]:
    """
    Here is the example code. You can freely replace it as long as it is compatible with the output format.
    """
    candidate_videos = [('1.mp4', [('drop_frames', 1, 2, 0.8)]), ('1.mp4', [('drop_frames', 2, 3, 0.8)]),
                        ('1.mp4', [('drop_frames', 2, 3, 0.8), ('drop_frames', 6, 8, 0.8)]),
                        ('1.mp4', [('change_playback_rate', 1, 6, 0.5)]), ('1.mp4', [('change_bitrate', 2, 8, 200)]),
                        ('1.mp4', [('freeze_frame', 5, 2)])]

    if len(ratings) > len(candidate_videos):
        return [], []

    return [candidate_videos[len(ratings) - 1]], [2]
