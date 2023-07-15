"""
Manage the videos and their ratings
"""
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set
import utils
import video_ops
import os, uuid

raw_video_root = '../static/videos/raw_videos/'
test_video_root = '../static/videos/test_videos/'

@dataclass
class Video:
    raw_id: str = field(default_factory=str)
    video_quality: bytes = field(default=None)
    video_filename: str = field(default=None)
    ratings: List[int] = field(default_factory=list)


@dataclass
class VideoManager:
    video_id_map_filename: Dict[Tuple[str, bytes], str] = field(default_factory=dict)
    filename_map_remain_times: Dict[str, int] = field(default_factory=dict)
    filename_map_pending: Dict[str, int] = field(default_factory=dict)

    def is_video_created(self, video_id: Tuple[str, bytes]) -> bool:
        return video_id in self.video_id_map_filename

    def allocate_video_filename_to_worker(self, existing_files: Set[str]) -> str | None:

        available_video_filename_set = set(
            [filename for filename in self.filename_map_remain_times if self.filename_map_remain_times[filename] > 0])

        not_rated_video_filenames = available_video_filename_set - existing_files
        if len(not_rated_video_filenames) == 0:
            return None
        else:
            assigned_filename = random.choice(list(not_rated_video_filenames))
            self.filename_map_remain_times[assigned_filename] -= 1
            if assigned_filename in self.filename_map_pending:
                self.filename_map_pending[assigned_filename] += 1
            else:
                self.filename_map_pending[assigned_filename] = 1

            return assigned_filename

    def create_video(self, video_id: Tuple[str, bytes]) -> bool:
        if self.is_video_created(video_id=video_id):
            return False
        else:
            # TODO: Now, we regard two video quality sequences are different if they are NOT exactly the same.
            video_quality_sequence = utils.bytes_to_video_quality(quality_bytes=video_id[1])
            original_video_path = raw_video_root + video_id[0]
            output_path = None

            if len(video_quality_sequence) == 0:
                output_path = test_video_root + str(uuid.uuid4())
                video_ops.rewrite_video(original_video_path, output_path)
            else:
                '''
                Type of quality_change
                ['change_bitrate', start_time, end_time]
                ['freeze_frame', freeze_time, duration]
                ['change_playback_rate', start_time, end_time, new_speed]
                ['drop_frames', start_time, end_time, drop_percentage]
                '''
                for quality_change in video_quality_sequence:
                    output_path = test_video_root + str(uuid.uuid4())
                    if quality_change[0] == 'change_bitrate':
                        video_ops.change_bitrate(original_video_path, output_path, quality_change[1], quality_change[2], quality_change[3])
                    elif quality_change[0] == 'freeze_frame':
                        video_ops.freeze_frame(original_video_path, output_path, quality_change[1], quality_change[2])
                    elif quality_change[0] == 'change_playback_rate':
                        video_ops.change_playback_rate(original_video_path, output_path, quality_change[1], quality_change[2], quality_change[3])
                    elif quality_change[0] == 'drop_frames':
                        video_ops.drop_frames(original_video_path, output_path, quality_change[1], quality_change[2], quality_change[3])
                    else:
                        return False
                    original_video_path = output_path

            self.video_id_map_filename[video_id] = output_path
            return True


    def exam_rating(self, video_filename: str, view_time: float) -> bool:
        # TODO: add control question support
        if view_time < video_ops.get_duration(video_filename):
            return False
        return True

    def update_rating(self, video_file: str, rating: int) -> None:
        self.filename_map_pending[video_file] -= 1




# drop_frames('input.mp4', 'output.mp4', 2, 7, 0.8)
# change_playback_rate('input.mp4', 'output.mp4', 5, 8, 0.5)
# freeze_frame('input.mp4', 'output.mp4', 5, 2)
# change_bitrate('input.mp4', 'output.mp4', 2, 8, 200)