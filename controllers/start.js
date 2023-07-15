// start test:
var get_initial_videos = require('../models/get_initial_videos')
var process_user_feedback = require('../models/process_user_feedback')

var get_next_video = require('../models/get_next_video')

var fs = require('fs');

// change it when you use a different website URL
const server_path = "http://localhost:3001/static/videos/"

const video_folder = "test_videos";
const video_path = "./static/videos/" + video_folder;
const video_url = server_path + video_folder + "/";

// default setting: best, worst video names are best & worst
var best_quality = "1";
var worst_quality = "2";

// you have to pre-determine the # of videos.
var num_vids;

fs.readdir(video_path, function (err, files) {
    // examine # of videos
    let file_numbers;
    file_numbers = files.length;
    console.log("Initially, we have " + file_numbers + " videos.");
});

var post_example = async (ctx, next) => {
    ctx.render('example.html', {});
}

var post_start = async (ctx, next) => {
    var mturkID = ctx.request.body.MTurkID;
    var device = ctx.request.body.device;
    var age = ctx.request.body.age;
    var network = ctx.request.body.network;

    var initial_order = await get_initial_videos();

    var video_order = [best_quality, worst_quality, ...initial_order];
    num_vids = video_order.length;

    console.log("User info: ", mturkID, device, age);
    console.log("videos", video_order)

    var start = new Date().getTime();
    var results = fs.readdirSync('./results/')

    if (results.indexOf(mturkID + '.txt') > -1) {
        flag = false;
        ctx.render('repeat.html', {});
        return;
    }

    let user = {
        mturkID: mturkID,
        device: device,
        age: age,
        network: network,
        video_order: video_order,
        count: 1,
        result: [],
        video_time: [],
        grade_time: [],
        test: [],
        start: start
    };

    for (i = 0; i < num_vids; i++) {
        user.video_time.push(0);
        user.grade_time.push(0);
    }

    let value = Buffer.from(JSON.stringify(user)).toString('base64');
    ctx.cookies.set('name', value);
    ctx.render('training_page.html', {});
}

var post_grade = async (ctx, next) => {
    var user = ctx.state.user;
    var end = new Date().getTime();
    var exe_time = end - user.start;
    user.video_time[user.count - 1] += exe_time;
    user.start = end;

    let value = Buffer.from(JSON.stringify(user)).toString('base64');
    ctx.cookies.set('name', value);

    var title = user.count + "/" + num_vids;

    ctx.render('grade.html', {
        title: title, count: user.count, num_vids: num_vids
    });
}

var post_first = async (ctx, next) => {
    var video_src = video_url + best_quality + ".mp4";
    // https://github.com/michaelliao/learn-javascript/raw/master/video/vscode-nodejs.mp4

    var title = "1/" + num_vids;
    ctx.render('video.html', {
        title: title, video_src: video_src
    });
}

var post_training = async (ctx, next) => {

    ctx.render('training_page.html', {});
}

var post_reference = async (ctx, next) => {

    ctx.render('reference.html', {
        best_quality: video_url + best_quality + ".mp4", worst_quality: video_url + worst_quality + ".mp4"
    });
}

var post_back2video = async (ctx, next) => {
    var user = ctx.state.user;
    var video_src = video_url + user.video_order[user.count - 1] + ".mp4";
    var end = new Date().getTime();
    var exe_time = end - user.start;
    user.grade_time[user.count - 1] += exe_time;
    user.start = end;
    let value = Buffer.from(JSON.stringify(user)).toString('base64');
    ctx.cookies.set('name', value);
    var title = user.count + "/" + num_vids;
    if (user.video_order[user.count - 1] == 1) {
        ctx.render('video.html', {
            title: title, video_src: video_src
        });
    } else if (user.video_order[user.count - 1] == 2) {
        ctx.render('bad_video.html', {
            title: title, video_src: video_src
        });
    } else {
        ctx.render('2video.html', {
            title: title, video_src: video_src
        });
    }
}


var post_next = async (ctx, next) => {
    var user = ctx.state.user;
    var grade = ctx.request.body.sentiment;
    var end = new Date().getTime();
    var exe_time = end - user.start;

    var attention_test = Number(ctx.request.body.blur) + Number(ctx.request.body.stall);

    user.test.push(attention_test);
    user.result.push(grade);

    user.grade_time[user.count - 1] += exe_time;

    user.start = end;

    if (user.count < num_vids) {
        var user_feedback = grade + '\n' + '\n' + exe_time;
        var video_file_name = await get_next_video(user_feedback);
        if (video_file_name != "-1") {
            console.log("next video is not -1" + video_file_name);
            user.video_order.splice(user.count, 1, video_file_name);
        }

        var video_src = video_url + user.video_order[user.count] + ".mp4";

        user.count = user.count + 1;
        var title = user.count + "/" + num_vids;

        // set new cookie
        let value = Buffer.from(JSON.stringify(user)).toString('base64');
        ctx.cookies.set('name', value);
        if (user.count == 2) {
            ctx.render('bad_video.html', {
                title: title, video_src: video_src
            });
        } else if (user.count == 3) {
            ctx.render('test_page.html', {
                title: title, video_src: video_src
            });
        } else {
            ctx.render('2video.html', {
                title: title, video_src: video_src
            });
        }
    } else {
        // set new cookie
        let value = Buffer.from(JSON.stringify(user)).toString('base64');
        ctx.cookies.set('name', value);
        ctx.render('reason.html', {
            title: 'Post Survey Question'
        });
    }
}

var post_end = async (ctx, next) => {
    var user = ctx.state.user;

    // set user reason
    var reason = ctx.request.body.Reason;
    console.log("reason is " + reason + "\n");
    user.reason = reason;

    // record results
    console.log(user.result);

    var filename = "./results/" + user.mturkID + ".txt";
    var write_data = [];
    var write_test = [];
    var write_video_time = [], write_grade_time = [];
    for (var i in user.video_order) {
        write_data[user.video_order[i] - 1] = user.result[i];
        write_test[user.video_order[i] - 1] = user.test[i];
        write_video_time[user.video_order[i] - 1] = user.video_time[i];
        write_grade_time[user.video_order[i] - 1] = user.grade_time[i];
    }

    var user_feedback = write_data + '\n' + user.video_order + '\n' +
        write_video_time + '\n'
        + write_grade_time + '\n' + user.mturkID + '\n'
        + user.device + '\n' + user.age + '\n'
        + user.network + '\n' + user.reason + '\n' + write_test;

    fs.writeFile(filename, user_feedback, function (err) {
        if (err) {
            return console.log(err);
        }
    });

    var user_feedback_processing_results = await process_user_feedback(user_feedback);
    console.log("information processed: ", user_feedback_processing_results)

    // clear cookie
    ctx.cookies.set('name', '');

    var return_code = video_folder;
    ctx.render('ending.html', {
        title: 'Thank you', return_code: return_code
    });
}


module.exports = {
    'POST /start': post_start,
    'POST /training': post_training,
    'POST /grade': post_grade,
    'POST /back2video': post_back2video,
    'POST /next': post_next,
    'POST /end': post_end,
    'POST /example': post_example,
    'POST /first': post_first,
    'POST /reference': post_reference
};
