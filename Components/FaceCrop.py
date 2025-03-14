
from moviepy.editor import VideoFileClip

def crop_to_vertical(input_video_path, output_video_path):
    clip = VideoFileClip(input_video_path)
    width, height = clip.size
    vertical_width = int(height * 9 / 16)
    x_start = (width - vertical_width) // 2
    cropped_clip = clip.crop(x1=x_start, x2=x_start + vertical_width)
    cropped_clip.write_videofile(output_video_path, codec='libx264', audio=False, preset='ultrafast', threads=4)

def combine_videos(video_with_audio, video_without_audio, output_filename):
    clip_with_audio = VideoFileClip(video_with_audio)
    clip_without_audio = VideoFileClip(video_without_audio)
    final_clip = clip_without_audio.set_audio(clip_with_audio.audio)
    final_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)
    final_clip.close()  # Ensure all clips are closed