from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip
import subprocess

def extractAudio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "audio.wav"
    video.audio.write_audiofile(audio_path, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])  # Mono, fast
    return audio_path

def crop_video(input_file, output_file, start_time, end_time):
    video = VideoFileClip(input_file).subclip(start_time, end_time)
    video.write_videofile(output_file, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)
    video.close()  # Ensure the clip is closed
    
# Example usage:
if __name__ == "__main__":
    input_file = r"Example.mp4" ## Test
    print(input_file)
    output_file = "Short.mp4"
    start_time = 31.92 
    end_time = 49.2   

    crop_video(input_file, output_file, start_time, end_time)