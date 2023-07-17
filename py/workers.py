from dataclasses import dataclass, field
from typing import Set, Dict
from videos import VideoManager

@dataclass
class Worker:
    arrival_time: int = field(default=0)
    leave_time: int = field(default=0)
    is_alive: bool = field(default=True)
    id: str = field(default='Unknown')
    rated_video_filename_map_rating: Dict[str, int] = field(default_factory=dict)
    n_rated_videos_this_round: int = field(default=0)
    video_filename_not_accepted: Set[str] = field(default_factory=set)


@dataclass
class WorkManager:
    id_map_workers: Dict[str, Worker] = field(default_factory=dict)

    def add_worker(self, worker_id: str, arrival_time: int = 0) -> None:
        if worker_id not in self.id_map_workers:
            self.id_map_workers[worker_id] = Worker(id=worker_id, arrival_time=arrival_time)
        else:
            self.id_map_workers[worker_id].is_alive = True

    def terminate_worker(self, worker_id: str) -> None:
        self.id_map_workers[worker_id].is_alive = False
        self.id_map_workers[worker_id].n_rated_videos_this_round = 0

    def allocate_video_to_worker(self, worker_id: str, video_manager: VideoManager) -> str | None:

        new_video_filename = video_manager.allocate_video_filename_to_worker(
            existing_files=set(self.id_map_workers[worker_id].rated_video_filename_map_rating.keys()))

        return new_video_filename

    def submit_worker_rating(self, worker_id: str, video_filename: str, rating: int, view_time: int, video_manager: VideoManager) -> bool:
        self.id_map_workers[worker_id].n_rated_videos_this_round += 1
        self.id_map_workers[worker_id].rated_video_filename_map_rating[video_filename] = rating

        if video_manager.is_rating_valid(video_filename=video_filename, view_time=view_time):
            video_manager.update_valid_rating(video_filename=video_filename, rating=rating)
            video_manager.update_assignments()
            return True
        else:
            self.id_map_workers[worker_id].video_filename_not_accepted.add(video_filename)
            video_manager.update_invalid_rating(video_filename=video_filename)
            return False


