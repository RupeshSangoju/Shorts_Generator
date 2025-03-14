import os

# Lock ImageMagick in
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import time
from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extractAudio, crop_video
from Components.AudioTranscibe import transcribe_audio
from Components.Speaker import detect_faces_and_speakers
from Components.FaceCrop import crop_to_vertical, combine_videos
from Components.Captions import add_captions_to_video

def safe_remove(file, max_retries=3, delay=1):
    """Attempt to remove a file with retries if it's locked."""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed: {file}")
            return
        except PermissionError as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Error removing {file}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)  # Wait before retrying
    print(f"Failed to remove {file} after {max_retries} attempts.")

def main():
    url = input("Enter YouTube video URL: ")
    video_path = download_youtube_video(url)
    audio_path = extractAudio(video_path)
    transcriptions = transcribe_audio(audio_path)
    
    # Pick a highlight that is at least 20 seconds long
    highlight = None
    min_duration = 20  # Minimum duration in seconds
    
    for segment in transcriptions:
        text, start, end = segment
        duration = end - start
        if text.strip().endswith('.') and duration >= min_duration:
            highlight = segment
            break
    
    if not highlight:
        for i, segment in enumerate(transcriptions):
            if segment[0].strip().endswith('.'):
                extended_text = segment[0]
                extended_start = segment[1]
                extended_end = segment[2]
                extended_duration = extended_end - extended_start
                
                if extended_duration >= min_duration:
                    highlight = [extended_text, extended_start, extended_end]
                    break
                
                for next_segment in transcriptions[i+1:]:
                    extended_text += " " + next_segment[0]
                    extended_end = next_segment[2]
                    extended_duration = extended_end - extended_start
                    if extended_duration >= min_duration and next_segment[0].strip().endswith('.'):
                        highlight = [extended_text, extended_start, extended_end]
                        break
                if highlight:
                    break
    
    if not highlight:
        longest_segment = max(transcriptions, key=lambda x: x[2] - x[1])
        text, start, end = longest_segment
        duration = end - start
        if duration < min_duration:
            extended_end = start + min_duration
            highlight = [text, start, extended_end]
            print(f"Warning: No 20s+ segment found. Extending longest segment ({duration}s) to {min_duration}s")
        else:
            highlight = longest_segment
    
    print(f"Selected highlight: '{highlight[0]}' ({highlight[1]}s - {highlight[2]}s, {highlight[2] - highlight[1]}s)")
    
    # Process the video
    cropped_video = "cropped.mp4"
    crop_video(video_path, cropped_video, highlight[1], highlight[2])
    detected_video = "detected.mp4"
    detect_faces_and_speakers(cropped_video, detected_video)
    vertical_video = "vertical.mp4"
    crop_to_vertical(detected_video, vertical_video)
    final_no_captions = "final_no_captions.mp4"
    combine_videos(cropped_video, vertical_video, final_no_captions)
    
    # Filter transcriptions
    highlight_start = highlight[1]
    highlight_end = highlight[2]
    filtered_transcriptions = [
        [text, start - highlight_start, end - highlight_start]
        for text, start, end in transcriptions
        if start >= highlight_start and end <= highlight_end
    ]
    video_duration = highlight_end - highlight_start
    filtered_transcriptions = [
        [text, max(0, start), min(end, video_duration)]
        for text, start, end in filtered_transcriptions
    ]
    
    final_video = "final.mp4"
    add_captions_to_video(final_no_captions, filtered_transcriptions, final_video)
    
    # Cleanup with safe removal
    files_to_remove = [video_path, audio_path, cropped_video, detected_video, vertical_video, final_no_captions]
    for file in files_to_remove:
        safe_remove(file)
    print(f"Cleanup done, only {final_video} remains.")

if __name__ == "__main__":

    main()