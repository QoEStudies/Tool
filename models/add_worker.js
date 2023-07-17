function add_worker(worker_id) {

    var url = "http://127.0.0.1:5000/add_worker";
    var data = {'worker_id': worker_id};

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

module.exports = add_worker;
