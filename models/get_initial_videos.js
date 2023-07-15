async function get_initial_videos() {

    const node_calls_python = require("node-calls-python");
    const py = node_calls_python.interpreter;

    const pymodule_initial_video_order = py.importSync("./py/get_initial_videos.py");
    var initial_order = py.callSync(pymodule_initial_video_order, "get_initial_video_order");

    console.log("In get_initial_videos", initial_order);

    return initial_order;
}

module.exports = get_initial_videos;
