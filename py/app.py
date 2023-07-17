from flask import Flask, request, jsonify
from workers import WorkManager
from videos import VideoManager
from py.user_defined_module.initialize_videos import get_initial_videos
import pickle
import time


def create_app():
    app = Flask(__name__)
    app.config['worker_manager'] = WorkManager()
    app.config['video_manager'] = VideoManager()
    with app.app_context():
        # Set up initialize videos
        initial_videos, initial_video_n_ratings = get_initial_videos()
        for i in range(0, len(initial_videos)):
            raw_id, video_quality_seq = initial_videos[i]
            app.config['video_manager'].add_video(raw_id=raw_id, video_quality_seq=video_quality_seq,
                                                  rating_count=initial_video_n_ratings[i])

    def terminate_experiment() -> None:
        worker_manager = app.config['worker_manager']
        video_manager = app.config['video_manager']
        worker_history = []
        for worker_id, worker_obj in worker_manager.id_map_workers.items():
            worker_history.append(worker_obj)
        with open('../results/worker_history.pkl', 'wb') as worker_file:
            pickle.dump(worker_history, worker_file)

        video_history = []
        for filename, video_obj in video_manager.filename_map_video_obj.items():
            video_history.append(video_obj)
        with open('../results/video_history.pkl', 'wb') as video_file:
            pickle.dump(video_history, video_file)

    # Hello world
    @app.route('/hello')
    def hello_world():
        response_data = {'return_message': 'HAHAHA'}
        return jsonify(response_data)

    # Add worker
    @app.route('/add_worker', methods=['POST'])
    def add_worker_request():
        worker_manager = app.config['worker_manager']
        data = request.json
        # print('********REGISTER WORKER****************')
        # print(data)
        # print('********REGISTER WORKER****************')

        worker_id = data.get('worker_id')
        worker_manager.add_worker(worker_id=worker_id, arrival_time=int(time.time()))
        response_data = {'return_message': 'OK'}
        return jsonify(response_data)

    # Submit rating
    @app.route('/submit_rating', methods=['POST'])
    def submit_rating_request():
        worker_manager = app.config['worker_manager']
        video_manager = app.config['video_manager']
        data = request.json
        worker_id = data.get('worker_id')
        video_filename = data.get('video_filename')
        rating = int(data.get('rating'))
        view_time = int(data.get('view_time'))
        is_rating_accepted = worker_manager.submit_worker_rating(worker_id=worker_id, video_filename=video_filename,
                                                                 rating=rating, view_time=view_time,
                                                                 video_manager=video_manager)
        response_data = {'is_rating_accepted': is_rating_accepted}
        # print('********GET RATING****************')
        # print(response_data)
        # print(worker_id)
        # print(is_rating_accepted)
        # print(video_filename)
        # print(rating)
        # print(view_time)
        # print('********GET RATING****************')

        if not video_manager.has_video_to_rate:
            terminate_experiment()

        return jsonify(response_data)

    # Get next video
    @app.route('/get_next_video', methods=['POST'])
    def get_next_video():
        worker_manager = app.config['worker_manager']
        video_manager = app.config['video_manager']

        data = request.json
        worker_id = data.get('worker_id')

        # calculate the next video
        next_filename = worker_manager.allocate_video_to_worker(worker_id=worker_id, video_manager=video_manager)
        if next_filename is None:
            next_filename = 'None'

        response_data = {'next_filename': next_filename}
        # print('********GET NEXT VIDEO****************')
        # print(response_data)
        # print(worker_id)
        # print('********RGET NEXT VIDEO****************')
        return jsonify(response_data)

    return app


# Start the Flask server
if __name__ == '__main__':
    my_app = create_app()
    my_app.run(port=5000, debug=False)

#
# rating_counter = 0
# while True:
#     rating_counter += 1
#     video_quality_seqs, ratings = video_manager.video_quality_map_ratings
#     next_video_quality_seqs, next_video_views = update_next_videos(videos=video_quality_seqs, ratings=ratings)
#     if len(next_video_views) == 0:
#         break
#
#     #  update scores
#     for i in range(0, len(next_video_quality_seqs)):
#         video_raw_data = next_video_quality_seqs[i]
#         video_manager.add_video(raw_id=video_raw_data[0], video_quality_seq=video_raw_data[1],
#                                 rating_count=next_video_views[i])
#         video_id = (video_raw_data[0], utils.video_quality_to_bytes(video_raw_data[1]))
#         video_filename = video_manager.video_id_map_filename[video_id]
#         video_manager.update_valid_rating(video_filename, rating_counter)

# worker_manager.add_worker('u1')
# worker_manager.add_worker('u2')
# worker_manager.add_worker('u3')
#
# v1_1 = worker_manager.allocate_video_to_worker('u1', video_manager)
# worker_manager.submit_worker_rating(worker_id='u1', video_filename=v1_1, view_time=100, rating=10, video_manager=video_manager)
#
# v1_2 = worker_manager.allocate_video_to_worker('u2', video_manager)
#
# v1_3 = worker_manager.allocate_video_to_worker('u3', video_manager=video_manager)
# print('first video u3', v1_3)
#
# worker_manager.submit_worker_rating(worker_id='u2', video_filename=v1_2, view_time=1, rating=10, video_manager=video_manager)
#
# v2_1 = worker_manager.allocate_video_to_worker('u1', video_manager=video_manager)
# print('next video u1', v2_1)
#
# v2_2 = worker_manager.allocate_video_to_worker('u2', video_manager=video_manager)
# print('next video u2', v2_2)
#
# v1_3 = worker_manager.allocate_video_to_worker('u3', video_manager=video_manager)
# print('next video u3', v1_3)
