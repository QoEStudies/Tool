"""
Manage the videos and their ratings
"""
import copy
import os
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Any
import utils
import video_ops
import uuid
from py.user_defined_module.next_videos import update_next_videos

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
    filename_map_video_obj: Dict[str, Any] = field(default_factory=dict)

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
                output_path = test_video_root + str(uuid.uuid4()) + '.mp4'
                video_ops.rewrite_video(original_video_path, output_path)
            else:
                '''
                Type of quality_change
                ['change_bitrate', start_time, end_time]
                ['freeze_frame', freeze_time, duration]
                ['change_playback_rate', start_time, end_time, new_speed]
                ['drop_frames', start_time, end_time, drop_percentage]
                '''
                video_for_delete = []
                for i, quality_change in enumerate(video_quality_sequence):
                    output_path = test_video_root + str(uuid.uuid4()) + '.mp4'
                    if quality_change[0] == 'change_bitrate':
                        video_ops.change_bitrate(original_video_path, output_path, quality_change[1], quality_change[2],
                                                 quality_change[3])
                    elif quality_change[0] == 'freeze_frame':
                        video_ops.freeze_frame(original_video_path, output_path, quality_change[1], quality_change[2])
                    elif quality_change[0] == 'change_playback_rate':
                        video_ops.change_playback_rate(original_video_path, output_path, quality_change[1],
                                                       quality_change[2], quality_change[3])
                    elif quality_change[0] == 'drop_frames':
                        video_ops.drop_frames(original_video_path, output_path, quality_change[1], quality_change[2],
                                              quality_change[3])
                    else:
                        return False
                    if i > 0:
                        video_for_delete.append(copy.deepcopy(original_video_path))
                    original_video_path = output_path

                for delete_video_path in video_for_delete:
                    os.remove(delete_video_path)

            self.video_id_map_filename[video_id] = output_path
            video_obj = Video(raw_id=video_id[0], video_quality=video_id[1], video_filename=output_path)
            self.filename_map_video_obj[output_path] = video_obj
            self.filename_map_remain_times[output_path] = 0
            self.filename_map_pending[output_path] = 0
            return True

    def add_video(self, raw_id: str, video_quality_seq: List[Tuple[Any, ...]], rating_count: int = 1) -> None:
        video_quality_byte = utils.video_quality_to_bytes(video_quality=video_quality_seq)
        if not self.is_video_created(video_id=(raw_id, video_quality_byte)):
            self.create_video(video_id=(raw_id, video_quality_byte))

        video_filename = self.video_id_map_filename[(raw_id, video_quality_byte)]
        rating_count_already_set = self.filename_map_pending[video_filename] + self.filename_map_remain_times[
            video_filename]
        if rating_count_already_set < rating_count:
            self.filename_map_remain_times[video_filename] += (rating_count - rating_count_already_set)

    def is_rating_valid(self, video_filename: str, view_time: float) -> bool:
        # TODO: add control question support
        if view_time < video_ops.get_duration(video_filename):
            return False
        return True

    def update_assignments(self) -> None:
        video_quality_seqs, ratings = self.video_quality_map_ratings
        next_video_quality_seqs, next_video_views = update_next_videos(videos=video_quality_seqs, ratings=ratings)
        if len(next_video_views) > 0:
            #  update scores
            for i in range(0, len(next_video_quality_seqs)):
                video_raw_data = next_video_quality_seqs[i]
                self.add_video(raw_id=video_raw_data[0], video_quality_seq=video_raw_data[1],
                               rating_count=next_video_views[i])

    def update_valid_rating(self, video_filename: str, rating: int) -> None:
        self.filename_map_pending[video_filename] -= 1
        self.filename_map_video_obj[video_filename].ratings.append(rating)

    def update_invalid_rating(self, video_filename: str) -> None:
        self.filename_map_pending[video_filename] -= 1
        self.filename_map_remain_times[video_filename] += 1

    @property
    def video_quality_map_ratings(self) -> Tuple[List[Tuple[str, List[Tuple[Any, ...]]]], List[List[int]]]:
        video_quality_seqs = []
        video_ratings = []
        for _, video_obj in self.filename_map_video_obj.items():
            video_ratings.append(video_obj.ratings)
            video_quality_seqs.append((video_obj.raw_id, utils.bytes_to_video_quality(video_obj.video_quality)))
        return video_quality_seqs, video_ratings

    @property
    def has_video_to_rate(self) -> bool:
        n_ratings_left = 0
        for filename in self.filename_map_pending:
            n_ratings_left += self.filename_map_pending[filename]
        for filename in self.filename_map_remain_times:
            n_ratings_left += self.filename_map_remain_times[filename]

        return n_ratings_left > 0
