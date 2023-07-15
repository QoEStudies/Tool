async function process_user_feedback(user_feedback) {

    const node_calls_python = require("node-calls-python");
    const py = node_calls_python.interpreter;

    const pymodule_process_user_feedback = py.importSync("./py/process_user_feedback.py");
    var process_results = py.callSync(pymodule_process_user_feedback, "process_user_feedback", user_feedback);

    return process_results;
}

module.exports = process_user_feedback;
