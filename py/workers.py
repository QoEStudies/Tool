from dataclasses import dataclass, field
from typing import Set, Dict


@dataclass
class Worker:
    arrival_time: int = field(default=0)
    leave_time: int = field(default=0)
    is_alive: bool = field(default=True)
    id: str = field(default='Unknown')
    rated_video_map_rating: Dict[str, int] = field(default_factory=dict)
    n_rated_videos_this_round: int = field(default=0)


@dataclass
class WorkManager:
    id_map_workers: Dict[str, Worker] = field(default_factory=dict)

    def add_worker(self, worker_id: str, arrival_time: int = 0) -> None:
        if id in self.id_map_workers:
            self.id_map_workers[worker_id] = Worker(id=worker_id, arrival_time=arrival_time)
        else:
            self.id_map_workers[worker_id].is_alive = True

    def terminate_worker(self, worker_id: str) -> None:
        self.id_map_workers[worker_id].is_alive = False
        self.id_map_workers[worker_id].n_rated_videos_this_round = 0

    def allocate_video_to_worker(self, worker_id) -> None:
        return