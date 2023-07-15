import random
import subprocess
import tempfile
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
import os


def get_duration(input_file):
    # Get the duration of the video
    return VideoFileClip(input_file).duration


def rewrite_video(input_file, output_file):
    # Load the video clip
    clip = VideoFileClip(input_file)

    # Write the final video to the output path
    clip.write_videofile(output_file)


def change_bitrate(input_file, output_file, start_time, end_time, bitrate):
    # Get the duration of the video
    clip = VideoFileClip(input_file)
    v_length = clip.duration

    # Create temporary files
    tmp_file_before = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    tmp_file_during = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    tmp_file_after = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    tmp_file_during_bitrate_changed = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    # Extract three separate clips
    ffmpeg_extract_subclip(input_file, 0, start_time, targetname=tmp_file_before)
    ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=tmp_file_during)
    ffmpeg_extract_subclip(input_file, end_time, v_length, targetname=tmp_file_after)

    # Change the bitrate of the 'during' clip
    command = f'ffmpeg -y -i {tmp_file_during} -b:v {bitrate}k {tmp_file_during_bitrate_changed}'
    subprocess.run(command, shell=True, check=True)

    # Concatenate the clips
    tmp_concat = tempfile.NamedTemporaryFile(delete=True, suffix=".txt").name
    command = f'ffmpeg -y -f concat -safe 0 -i {tmp_concat} -c copy {output_file}'
    with open(tmp_concat, 'w') as f:
        f.write(f"file '{tmp_file_before}'\n")
        f.write(f"file '{tmp_file_during_bitrate_changed}'\n")
        f.write(f"file '{tmp_file_after}'\n")
    subprocess.run(command, shell=True, check=True)
    os.remove(tmp_file_before)
    os.remove(tmp_file_during)
    os.remove(tmp_file_after)
    os.remove(tmp_file_during_bitrate_changed)
    os.remove(tmp_concat)


def freeze_frame(input_file, output_file, freeze_time, duration):
    # Load the video clip
    clip = VideoFileClip(input_file)
    v_length = clip.duration

    # Calculate the start and end times for the freeze segment
    freeze_start = freeze_time
    freeze_end = freeze_time + duration

    # Split the clip into segments
    clip_before = clip.subclip(0, freeze_start)
    clip_freeze = clip.subclip(freeze_start, freeze_end)
    clip_after = clip.subclip(freeze_start, v_length)

    # Freeze the frame by duplicating the first frame of the freeze segment
    freezing_frame = ImageClip(clip_freeze.get_frame(0))
    freeze_effect = freezing_frame.set_duration(duration)

    # Concatenate the segments
    final_clip = concatenate_videoclips([clip_before, freeze_effect, clip_after])

    # Write the final video to the output path
    final_clip.write_videofile(output_file)


def change_playback_rate(input_file, output_file, start_time, end_time, new_speed):
    # Load the video clip
    clip = VideoFileClip(input_file)
    v_length = clip.duration

    # Split the clip into segments
    clip_before = clip.subclip(0, start_time)
    clip_slowmotion = clip.subclip(start_time, end_time).fx(VideoFileClip.speedx, new_speed)
    clip_after = clip.subclip(end_time, v_length)

    # Concatenate the segments
    final_clip = concatenate_videoclips([clip_before, clip_slowmotion, clip_after])

    # Write the final video to the output path
    final_clip.write_videofile(output_file)


def drop_frames(input_file, output_file, start_time, end_time, drop_percentage):
    # Load the video clip
    clip = VideoFileClip(input_file)
    v_length = clip.duration

    clip_before = clip.subclip(0, start_time)
    clip_drop = clip.subclip(start_time, end_time)
    clip_after = clip.subclip(end_time, v_length)

    # Iterate over the frames and select a portion of them
    selected_frames = []
    for i, frame in enumerate(clip_drop.iter_frames()):
        keep = (random.random() > drop_percentage) or i == 0
        if keep:
            selected_frames.append(frame)
        else:
            selected_frames.append(selected_frames[-1])

    # Create a new video clip from the selected frames
    selected_clip = VideoFileClip(input_file)
    selected_clip = selected_clip.set_duration(len(selected_frames) / clip_drop.fps)
    selected_clip = selected_clip.set_make_frame(lambda t: selected_frames[int(t * clip_drop.fps)])

    # Concatenate the segments
    final_clip = concatenate_videoclips([clip_before, selected_clip, clip_after])

    # Write the final video to the output path
    final_clip.write_videofile(output_file)


# drop_frames('input.mp4', 'output.mp4', 2, 7, 0.8)
# change_playback_rate('input.mp4', 'output.mp4', 5, 8, 0.5)
# freeze_frame('input.mp4', 'output.mp4', 5, 2)
# change_bitrate('input.mp4', 'output.mp4', 2, 8, 200)
