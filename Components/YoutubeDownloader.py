import os
from pytubefix import YouTube
import ffmpeg

import re

def sanitize_filename(filename):
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_video_size(stream):
    return stream.filesize / (1024 * 1024)

from pytubefix import YouTube
import os

def download_youtube_video(url):
    yt = YouTube(url)
    print("Available streams:")
    for i, stream in enumerate(yt.streams, 1):
        print(f"{i}. {stream}")
    
    resolutions = ["720p", "480p", "360p", "144p"]  # Dropped 1080p progressive - rare
    stream = None
    for res in resolutions:
        stream = yt.streams.filter(progressive=True, file_extension='mp4', res=res).first()
        if stream:
            print(f"Using progressive stream: {stream}")
            break
    
    if not stream:
        for res in resolutions:
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', res=res).first()
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
            if video_stream and audio_stream:
                print(f"Using adaptive streams: Video={video_stream}, Audio={audio_stream}")
                break
        if not video_stream or not audio_stream:
            raise Exception("No suitable streams found")
    
    # Sanitize filename
    safe_title = "".join(c if c.isalnum() else "_" for c in yt.title)  # e.g., Self_Motivation_Brendan_Clark_TEDxYouth_BarnstableHS
    output_file = os.path.join('videos', f"{safe_title}.mp4")
    if not os.path.exists('videos'):
        os.makedirs('videos')
    
    if stream:
        stream.download(output_path='videos', filename=f"{safe_title}.mp4")
    else:
        video_path = os.path.join('videos', f"{safe_title}_video.mp4")
        audio_path = os.path.join('videos', f"{safe_title}_audio.mp4")
        video_stream.download(output_path='videos', filename=f"{safe_title}_video.mp4")
        audio_stream.download(output_path='videos', filename=f"{safe_title}_audio.mp4")
        cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_file}" -y -loglevel error'
        if os.system(cmd) != 0:
            raise Exception("ffmpeg merge failed")
        os.remove(video_path)
        os.remove(audio_path)
    
    print(f"Downloaded: {output_file}")
    return output_file

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    download_youtube_video(youtube_url)