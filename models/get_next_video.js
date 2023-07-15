async function get_next_video(user_feedback) {

    const node_calls_python = require("node-calls-python");
    const py = node_calls_python.interpreter;

    const pymodule_get_next_video = py.importSync("./py/get_next_video.py");
    var next_video = py.callSync(pymodule_get_next_video, "get_next_video", user_feedback);

    console.log("next video is " + next_video);

    return next_video;
}

module.exports = get_next_video;
