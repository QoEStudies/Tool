
# README

## Description

It is a tool for setting up user studies for video QoE studies.
Different from the traditional tools which need you to specify the videos and the number of ratings for the videos to collect before the user study,
this tool can dynamically generate videos to rate during the user study task.

## Environmental setup

1. Install `node.js` from its [official website](https://nodejs.org/en/download/)

   if you are using Windows, make sure to click 'add to path' when installing.

   To test if the installation is successful, you can input 

   ```shell
   node -v
   ```

   in your command line.

2. Download the zip file and unzip  it. Locate to the folder:

   ```shell
   cd Tool
   ```

3. (Optional) Install all the dependencies:

   This is an optional step for those without `node-modules` folder. If you have downloaded the complete file, all the modules are already in the `node-modules` folder.

   ```shell
   npm install
   pip install Flask, request, jsonify, moviepy
   ```
   
   Install FFMPEG
   ```shell
   #Cent OS 
   sudo yum install ffmpeg ffmpeg-devel
   
   #MacOS
   brew install ffmpeg
   
   #Windows: Download from https://ffmpeg.org/download.html
   ```

4. Start the server on localhost:

   ```shell
   node app.js & python ./py/app.py
   ```

   ```shell
   node app.js & python ./py/app.py 1>/dev/null 2>&1 &
   ```

   If you run into any errors regarding modules not found, try removing the "node_modules" folder and go back to step 3.

5. Visit `localhost:3001` on your website, you should see the instruction page.

   After finishing the test, the results will be stored in `./results/`, the file name will be the MTurk ID.

## Customize your user study

### Customize your video quality

This tool supports to customize video quality from a source (or raw) video. We support four types of operations.

| Operation                                               | Meaning                                                                |
|---------------------------------------------------------|------------------------------------------------------------------------|
| change_bitrate(start_time, end_time, new_bitrate)       | Change the original bitrate to new_bitrate from start_time to end_time |      
| freeze_frame(freeze_point, freeze_duration)             | Freeze the frame at freeze_point for a time period of freeze_duration  | 
| change_playback_rate(start_time, end_time, new_playback) | Set the playback rate to new_playback from start_time to end_time      |  
 | drop_frames(start_time, end_time, drop_rate)            | Drop drop_rate frames from start_time to end_time                      | 

In this tool, a video's quality is presented as the following format:
```python3
"""
Format of video quality presentation: Tuple[str, List[Operation]]
"""
# Example: for source video source.mp4, we first set the bitrate to 200Kbps from 1 to 5 seconds,
# and then add a 2-second buffering stall at the 5-th second.
perceived_video_quality = ('source.mp4',  [('change_bitrate', 1, 5, 200), ('freee_frame', 5, 2)])
```

### Set up your source video

Please put all your source videos under `static/videos/raw_videos` 

### Set an initial set of application demos to rate

The initial set of videos for ratings is defined `get_initial_videos` in `py/user_defined_module/initialize videos`.
Please write your own logic.

The output format is
```python
(List[PerceivedVideoQuality], List[int]])
```
The first element of the output tuple is a list of perceived video quality (already defined above), and the second element
is a list of number of ratings needed for the corresponding perceived video quality. For example, in the following output tuple
```python
([('1.mp4', []), ('1.mp4', [('freeze_frame', 5, 1)])], [10, 20])
```
, we two videos to rate, i.e., `('1.mp4', [])` and `('1.mp4', [('freeze_frame', 5, 1)])` respectively. We need 10 ratings for the first video, and 20 for the second.


### Dynamically update worker assignment
We can dynamically determine next videos that need to be rated based on the collected QoE ratings. 
The logic is defined in `update_next_videos` in `py/user_defined_module/initialize videos`.
The input format is a tuple as
```python
(List[PerceivedVideoQuality], List[List[int]])
```
The first element is a list of perceived videos, and the second element is a list of the ratings for each video.
Each video has a list of ratings that we already collected.
For example,
```python
([('1.mp4', []), ('1.mp4', [('freeze_frame', 5, 1)])], [[1, 1], [2, 3]])
```
, we have two videos, `('1.mp4', [])` and `('1.mp4', [('freeze_frame', 5, 1)])`, and we have collected two ratings `[1, 1]` for the first video, `[2, 3]` for the second.

The output format is the same as `get_initial_videos` as
```python
(List[PerceivedVideoQuality], List[int]])
```
But the meaning is a little bit different.
It means how many **MORE** ratings we need for the videos. For example, if the output is
```python
([('1.mp4', []), ('1.mp4', [('freeze_frame', 5, 1)])], [2, 6])
```
, it means we need 2 more ratings for the first video, and 6 more for the second, based on the QoE ratings we already collected.

## Running on Amazon MTurk

1. Login to [Amazon Requester](https://requester.mturk.com/begin_signin) using your Amazon account.

2. Create a new project using their "Survey Link" template.

3. Fill out the survey properties. Here is an example of my settings:
   ![MTurk Settings](https://github.com/sheric98/QoEProject/blob/master/static/MTurk_Settings.png)

4. Click on Design Layout. Click on "Source" in the editor to edit the text.
   Here is an exmaple of my layout:
   ![Design Layout](https://github.com/sheric98/QoEProject/blob/master/static/Design_Layout.png)

   Remember to change the link correspondingly if you changed the port number.

5. Finish and publish a batch.

