const request = require("sync-request");

function submit_rating(worker_id, view_time, video_filename, rating) {

    var url = "http://127.0.0.1:5000/submit_rating";
    var new_filename = "../static/videos/test_videos/" + video_filename;
    var data = {'worker_id': worker_id, 'video_filename': new_filename, 'view_time': view_time, 'rating': rating};


    const request = require('sync-request');

    try {
        const res = request('POST', url, {
            json: data
        });
        return JSON.parse(res.getBody('utf8'));
    } catch (error) {
        console.error('Error sending POST request:', error);
        return null;
    }

}

module.exports = submit_rating;
