const request = require("sync-request");

function get_next_video(worker_id) {

    var url = "http://127.0.0.1:5000/get_next_video";
    var data = {'worker_id': worker_id};


    const request = require('sync-request');

    try {
        const res = request('POST', url, {
            json: data
        });
        const response = JSON.parse(res.getBody('utf8'));
        const video_path = response.next_filename;
        const parts = video_path.split('/');
        return parts[parts.length - 1];
    } catch (error) {
        console.error('Error sending POST request:', error);
        return "None";
    }




    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, false);  // Make the request synchronous

    // Set the content type header if sending JSON data
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Send the request
    xhr.send(JSON.stringify(data));

    if (xhr.status === 200) {
        // Request successful
        const response = JSON.parse(xhr.responseText);
        const video_path = response.next_filename;
        const parts = video_path.split('/');
        return parts[parts.length - 1];
    } else {
        // Request failed
        console.error('Error:', xhr.status);
        return 'None';
    }
}

module.exports = get_next_video;
